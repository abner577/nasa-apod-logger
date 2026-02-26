# Repository Guidelines

## Project Structure
- `src/` contains the application code. Entry point: `src/main.py`.
- `src/nasa/` handles API requests and date validation.
- `src/storage/` reads/writes log data.
- `src/utils/` contains CLI helpers, formatting, and utilities.
- `src/startup/` renders the startup UI and console theming.
- `data/` stores runtime outputs such as `output.jsonl`, `output.csv`, and `settings.jsonl`.
- `.env` stores API configuration; see `.env.example`.

## Build, Test, and Development Commands
- `python -m venv .venv` creates a virtual environment.
- `.venv\Scripts\Activate.ps1` activates it on Windows PowerShell.
- `pip install -r requirements.txt` installs dependencies.
- `python src/main.py` runs the CLI locally.

## Coding Style and Naming
- Use 4-space indentation and standard Python conventions.
- Prefer `snake_case` for functions and variables, `UPPER_SNAKE_CASE` for constants.
- Keep imports organized and use absolute imports from `src` (e.g., `from src.utils...`).
- Avoid introducing new output encodings; stick to UTF-8 when writing files.

## Applying color to application
- Use the Rich library as is used throughout the application to apply colors to the application.
- Use color of "ok" for check marks and color of "err" for X's.
- Use "app.primary", "app.secondary", and "body.text" to color the main components of the application.
- Always ask what color to apply to something before doing it. 

## Testing Guidelines
- There are no automated tests in this repo yet.
- Do not write any tests 

## Commit and Pull Request Guidelines
- Commit messages in this repo use short, imperative, sentence-case summaries (e.g., "Fix bug with commands", "Refactor startup_utils").
- PRs should include a concise description, the user-facing impact, and any relevant screenshots or CLI output.
- Link related issues or tasks when applicable.

## Configuration and Data Notes
- Create a `.env` file with `NASA_API_KEY` and `BASE_URL` (see `.env.example`).
- The app reads and writes logs under `data/`. Avoid committing generated data files.
