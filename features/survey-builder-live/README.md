# Survey Builder

A mini survey builder. Admins build a survey on one page: the question editor
is on the left and a live preview of the survey is on the right. Respondents
answer the survey on a separate page.

A survey holds rating questions (a scale of 2 to 5 points) and single-choice
questions. The builder shows how many answers each choice has received, and
one button saves the whole survey.

The assignment is in [docs/brief.md](docs/brief.md). Read it first. The ticket
queue is in [docs/tickets/](docs/tickets/) and the product definition of how
the survey builder behaves is in
[docs/how-the-survey-builder-works.md](docs/how-the-survey-builder-works.md).

## Prerequisites

- Docker with the Compose plugin (Docker Desktop on macOS and Windows, Docker
  Engine on Linux).
- Ports `5173` (frontend) and `8000` (API) free on your machine.

You do not need Python, Node, or Postgres installed locally.

## Run

```
docker compose up --build
```

The first start builds the images, waits for the database, applies migrations,
and loads the small sample data. There are no manual steps. When the logs
settle, open:

| What | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000/api/ (for example http://localhost:8000/api/surveys/) |
| Django admin | http://localhost:8000/admin/ |

Source folders are mounted into the containers, so edits to backend and
frontend code reload automatically.

Stop with `Ctrl+C`, then `docker compose down`. To throw away the database as
well, run `docker compose down -v`.

If you change the schema (models and migrations), drop the database volume with
`docker compose down -v` and start again. The sample data loads again on that
first start.

### Django admin

The Django admin is where submitted answers are read. It has read-only lists of
surveys, questions, responses, and answers. Each answer is listed with its
question, the label that was picked, the rating number, and the size of the
rating scale. Nothing can be changed there.

Log in with `admin` / `admin`. This account is for local development only. The
sample-data loader creates it if it does not exist.

## Sample data

The small dataset loads automatically on the first start: three surveys
("Support CSAT", "Support CSAT (highest first)" and "Onboarding check-in") with
about 60 responses each. Running it again is safe, it does nothing when data
already exists. To delete all survey data and reload it:

```
docker compose exec backend python manage.py seed --clear
```

### Large dataset

For a survey with a lot of questions and about 200,000 responses, run:

```
docker compose exec backend python manage.py seed_large
```

It takes a few minutes. It adds one survey called "Big survey" next to the
small ones. Use `seed_large --clear` to remove it and load it again.

## Tests

Backend (pytest and flake8):

```
docker compose exec backend pytest
docker compose exec backend flake8
```

Frontend (Vitest, jsdom, Testing Library):

```
docker compose exec frontend npm test
docker compose exec frontend npm run typecheck
```

## Architecture tour

### Backend

Django 5 and Django REST Framework on Postgres. The API is served under
`/api/`, JSON in and out, `snake_case` keys, no authentication. Invalid input
returns 400 with `{"detail": "..."}`. The Django admin is served under
`/admin/`.

```
backend/
  config/       settings, root URLs, CORS middleware, API error format
  surveys/      Survey and SurveyQuestion; survey list, builder, save and render
                views; the seed and seed_large commands
  questions/    Question and Choice; the default rating labels
  answers/      Response and Answer; the submit view
```

- `surveys` and `answers` have `models.py`, `urls.py`, a `views/` package, and
  `tests/test_views/`. `questions` has models but no endpoints of its own.
- One view per file in `<app>/views/`, re-exported from `views/__init__.py`.
  Tests are named after the view they cover.
- Each app registers its models for the Django admin in `admin.py`, all
  read-only.
- A survey has ordered questions. A rating or single-choice question has
  choices; the points of a rating scale are choices with a rating number. A
  response holds the answers one respondent gave to a survey.

| Method and path | View | What it does |
|---|---|---|
| GET `surveys/` | `survey_list_view` | List surveys, with question and response counts |
| POST `surveys/` | `survey_list_view` | Create an empty survey |
| GET `surveys/<id>/builder/` | `survey_builder_view` | The builder payload |
| PUT `surveys/<id>/` | `survey_save_view` | Save the whole survey in one request; returns the builder payload |
| GET `surveys/<id>/render/` | `survey_render_view` | The render payload |
| POST `surveys/<id>/responses/` | `survey_response_view` | Submit a whole response |

The builder payload is what the builder page loads: the survey, its questions,
and their choices, with the answer count of each choice. The render payload has
the same shape without the counts; the respondent page loads it.

### Frontend

React 18, TypeScript, Vite, semantic-ui-react, and Tailwind.

```
frontend/src/
  App.tsx                         routes
  types.ts                        shared types and the default rating labels
  api/                            axios instance and one file per resource
  pages/SurveyListPage/           the survey list
  pages/SurveyBuilderPage/        the builder page
  pages/SurveyPage/               the respondent page
  components/SurveyPreview/       the survey as a respondent sees it
  test/setup.ts                   Testing Library and jest-dom setup
```

| Route | Page |
|---|---|
| `/` | Survey list, with links to the builder and the respondent page, and a "New survey" button |
| `/surveys/:id/builder` | Builder on the left, live preview on the right |
| `/s/:id` | Respondent page |

- `SurveyPreview` is one component used twice: in the builder as the live
  preview (`mode="preview"`) and on the respondent page (`mode="live"`).
- The builder page holds the editors for questions, choices, and the rating
  scale, and the Save survey button.
- The `api/` layer holds the axios instance and one file of request helpers per
  resource (surveys, responses). `api/index.ts` creates the axios instance with
  its base URL from `VITE_API_URL`, which defaults to
  `http://localhost:8000/api/`, and converts keys between `camelCase` in the
  code and `snake_case` on the wire.
