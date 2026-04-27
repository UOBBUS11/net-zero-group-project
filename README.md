#### net-zero-group-project
Group coursework repository for MSc Computer Science – Agile Net Zero project

on terminal/command prompt, run:
git clone https://github.com/UOBBUS11/net-zero-group-project.git

#### Basic Git Commands

- `git init` – Initialize a new Git repository.

- `git clone <repository-url>` – Clone an existing repository.

- `git status` – Check the status of files in the repository.

- `git add <file>` – Add a specific file to the staging area.

- `git add .` – Add all changes to the staging area.

- `git commit -m "message"` – Commit staged changes with a message.

- `git log` – View commit history.

- `git branch` – List all branches.

- `git checkout <branch>` – Switch to another branch.

- `git pull origin main` – Pull the latest changes from the remote repository.

- `git push origin main` – Push local commits to the remote repository.

#### Development Setup

This project uses separate dependency files for normal app usage and development/testing.

#### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

#### 2. Install development dependencies

Use `requirements-dev.txt` when working on the project locally, especially when running tests.

```bash
pip install -r requirements-dev.txt
```

This installs the normal project dependencies plus development/testing tools required for unit tests.

---

#### Database Setup

The project includes a database setup script:

```bash
setup_db.py
```

This script resets and repopulates the SQLite database with:

- default transport modes
- default admin account
- saved locations
- demo users
- sample trip history for dashboard, leaderboard, and trip history testing

#### Reset and populate the database

From the project root, run:

```bash
python setup_db.py
```

This will drop existing database tables, recreate them, and insert demo data.

#### Demo login accounts

Admin account:

```text
username: admin
password: example123
```

Demo user accounts:

```text
username: matt
password: Carbon123!

username: amina
password: Carbon123!

username: josh
password: Carbon123!

username: sophie
password: Carbon123!

username: liam
password: Carbon123!
```

Do not commit the generated database file, such as:

```text
app.db
instance/app.db
```

The database should be recreated locally using `setup_db.py`.

---

#### Running the Application

After installing dependencies and setting up the database, run:

```bash
flask run
```

Then open the local Flask address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

---

#### Running Unit Tests

Unit tests are stored in the `tests/` directory.

To run all tests, use:

```bash
pytest
```

If `pytest` is not recognised, run it through Python:

```bash
python -m pytest
```

To run tests with more detailed output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_filename.py
```

Replace `test_filename.py` with the actual test file name.

---

#### Suggested Local Workflow

When starting work on a fresh clone:

```bash
git clone https://github.com/UOBBUS11/net-zero-group-project.git
cd net-zero-group-project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python setup_db.py
flask run
```

Before committing changes, run:

```bash
pytest
git status
```