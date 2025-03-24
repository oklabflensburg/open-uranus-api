# Uranus – Digitally Mapping and Providing the Event Landscape

_Disclaimer: This repository and the associated database are currently in a beta version. Some aspects of the code and data may still contain errors. Please contact us via email or create an issue on GitHub if you discover any issues._

## Introduction

With this project, we aim to create a detailed and flexible representation of the event landscape. Our goal is to make it easier to create, maintain, publish, and share high-quality event data.

The Uranus database provides a differentiated representation of event venues (Venues), space descriptions (Spaces), and organizations, for example, in a hierarchical structure such as Institution > Association > Working Group. Additionally, it enables the description of events (Events) with flexible scheduling (EventDate).

The generated data is accessible via an open API in various combinations. This allows the development of plugins (e.g., for WordPress) or integrations for websites.

Unlike other systems that primarily focus on individual events, Uranus also considers the relationships between locations, spaces, dates, and organizations. This opens up new possibilities for queries and applications. Locations and events can be visualized and presented in innovative ways on maps and portals.


## Target Groups
-	Event Organizers: Anyone who publicly offers events with participation opportunities, such as:
	-	Associations, initiatives, educational institutions
	-	Organizations in the fields of culture, leisure, and sports
-	Event Enthusiasts: Users who are actively searching for events, based on criteria such as:
	-	Dates
	-	Target audiences
	-	Event types and genres
	-	Event locations
	-	Organizers
	-	Accessibility-friendly events
	-	Festivals, exhibitions, and event series
-	Portals and Institutions: Associations, municipalities, or website operators who want to integrate event data into their platforms
- Journalists and Culture Reporters: Anyone looking for information about cultural events


## Project Status

The project was initiated on March 2, 2025. We are currently working on the first MVP (Minimal Viable Product) with the goal of presenting the core concept of Uranus in a demo. The MVP will include essential features such as event data creation and management, as well as API availability. Additional features will be added in the coming months.


## Installation

### Prerequisites

1. **Database Setup**

- Ensure PostgreSQL is installed and running on `localhost` (default port: `5432`).
- Create a database named `uranus`, owned by a user with the same name.
- Make sure the database accepts connections from `localhost`.

2. **Environment Variables**

- Create a `.env` file in the root directory of this repository and add the following environment variables with your specific values:

> You may use `openssl rand -hex 32` to generate your `SECRET_KEY` and `REFRESH_SECRET_KEY` keys.

```sh
MAIL_USERNAME=YOUR_EMAIL_USERNAME
MAIL_PASSWORD=YOUR_EMAIL_PASSWORD
MAIL_FROM=YOUR_EMAIL_ADDRESS
MAIL_PORT=YOUR_SMTP_PORT
MAIL_SERVER=YOUR_SMTP_SERVER
MAIL_STARTTLS=1
MAIL_SSL_TLS=0
FRONTEND_URL=YOUR_FRONTEND_URL
SECRET_KEY=YOUR_SECRET_KEY
REFRESH_TOKEN_EXPIRE_DAYS=DAYS
REFRESH_SECRET_KEY=YOUR_REFRESH_SECRET_KEY
UPLOAD_DIR=YOUR_UPLOADS_PATH
DATABASE_URL="postgresql+asyncpg://YOUR_DB_USER:YOUR_DB_PASS@YOUR_DB_HOST:YOUR_DB_PORT/YOUR_DB_NAME"
```

3. **Python**

- Python 3 installed with `venv` and `pip` available.

### Steps

1. Set up the database schema:

```sh
psql -U uranus -h localhost -d uranus -p 5432 < data/uranus-venue-schema.sql
psql -U uranus -h localhost -d uranus -p 5432 -c "CREATE EXTENSION IF NOT EXISTS pg_trgm"
psql -U uranus -h localhost -d uranus -p 5432 -c "CREATE INDEX IF NOT EXISTS venue_name_gin_idx ON uranus.venue USING gin (LOWER(name) gin_trgm_ops)"
```

2. Activate a Python virtual environment and install dependencies:

```sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

3. Run the API:

```sh
uvicorn app.main:app --reload --env-file .env
```

## Export Data

```sh
pg_dump -U oklab -h localhost -d oklab -n uranus --data-only --column-inserts --no-owner --no-comments --verbose -f uranus_data_dump.sql
pg_dump -U oklab -h localhost -d oklab -n uranus --schema-only --no-owner --no-comments --verbose -f uranus_schema_dump.sql
```
