from app import db
from app.models import Trip
from app.routes import (
    round_score,
    infer_zone_name,
    calculate_trip_score,
    recalculate_user_score,
)


def test_round_score_clamps_and_rounds():
    assert round_score(11.27) == 10.0
    assert round_score(-3.0) == 0.0
    assert round_score(6.66) == 6.7


def test_infer_zone_name():
    assert infer_zone_name("Birmingham City Centre") == "Birmingham Clean Air Zone"
    assert infer_zone_name("London Bridge") == "London ULEZ"
    assert infer_zone_name("Leeds") == "Emission Zone"


def test_short_walking_trip_scores_better_than_short_petrol_trip(walking_mode, petrol_mode):
    walk_carbon, walk_score, _, _ = calculate_trip_score(
        distance=1.0,
        mode=walking_mode,
        location="Birmingham",
        enters_emission_zone=False,
    )
    petrol_carbon, petrol_score, _, _ = calculate_trip_score(
        distance=1.0,
        mode=petrol_mode,
        location="Birmingham",
        enters_emission_zone=False,
    )

    assert walk_carbon < petrol_carbon
    assert walk_score > petrol_score


def test_emission_zone_penalty_applied_to_petrol_trip(petrol_mode):
    _, score_no_zone, breakdown_no_zone, _ = calculate_trip_score(
        distance=5.0,
        mode=petrol_mode,
        location="Birmingham",
        enters_emission_zone=False,
    )
    _, score_zone, breakdown_zone, zone_name = calculate_trip_score(
        distance=5.0,
        mode=petrol_mode,
        location="Birmingham",
        enters_emission_zone=True,
    )

    assert score_zone < score_no_zone
    assert "Emission zone penalty -1.4" in breakdown_zone
    assert "Emission zone penalty -1.4" not in breakdown_no_zone
    assert zone_name == "Birmingham Clean Air Zone"


def test_emission_zone_bonus_applied_to_train_trip(train_mode):
    _, score_no_zone, _, _ = calculate_trip_score(
        distance=5.0,
        mode=train_mode,
        location="London",
        enters_emission_zone=False,
    )
    _, score_zone, breakdown_zone, zone_name = calculate_trip_score(
        distance=5.0,
        mode=train_mode,
        location="London",
        enters_emission_zone=True,
    )

    assert score_zone > score_no_zone
    assert "Emission zone bonus +0.6" in breakdown_zone
    assert zone_name == "London ULEZ"


def test_recalculate_user_score_averages_trip_scores(app_context, normal_user, walking_mode):
    trip1 = Trip(
        distance_km=1.0,
        carbon_emission=0.0,
        score_earned=8.0,
        location="Birmingham",
        location_normalized="birmingham",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="",
        user=normal_user,
        mode=walking_mode,
    )
    trip2 = Trip(
        distance_km=2.0,
        carbon_emission=0.0,
        score_earned=6.0,
        location="Birmingham",
        location_normalized="birmingham",
        entered_emission_zone=False,
        emission_zone_name=None,
        score_breakdown="",
        user=normal_user,
        mode=walking_mode,
    )

    db.session.add_all([trip1, trip2])
    db.session.commit()

    recalculate_user_score(normal_user)
    db.session.commit()

    assert normal_user.current_score == 7.0