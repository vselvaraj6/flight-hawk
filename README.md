# ✈️ Flight Hawk — Flight Price Tracker

Monitor flight prices and get notified via Telegram when they drop below your target threshold.

![Dark themed dashboard](https://img.shields.io/badge/UI-Dark%20Theme-6366f1) ![Python 3.12](https://img.shields.io/badge/Python-3.12-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

## Features

- 📊 **Streamlit Dashboard** — Track multiple flight routes with a beautiful dark-themed UI
- 📉 **Automated Price Checks** — Hourly (or customizable) price monitoring via Amadeus API
- 📱 **Telegram Notifications** — Instant alerts when prices drop below your target
- ⚙️ **Configurable Frequency** — Change check intervals from the dashboard (15min to 12hr)
- 🐳 **Dockerized** — One command to run everything

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Amadeus API credentials](https://developers.amadeus.com/) (free tier)
- [Telegram Bot Token](https://core.telegram.org/bots#botfather) + your Chat ID

## Quick Start (Docker)

### 1. Clone the repo

```bash
git clone https://github.com/vselvaraj6/flight-hawk.git
cd flight-hawk
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
AMADEUS_API_KEY=your_key_here
AMADEUS_API_SECRET=your_secret_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3. Run

```bash
docker compose up -d --build
```

That's it! The dashboard is now live at **http://localhost:8501**.

Both the **Streamlit dashboard** and the **background price checker** start together.

### Useful commands

```bash
docker compose logs -f         # View live logs
docker compose down            # Stop everything
docker compose up -d --build   # Rebuild after code changes
```

## Local Development (without Docker)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start the dashboard (Terminal 1)
streamlit run app.py

# Start the price checker (Terminal 2)
python main.py
```

## Deploying on a Homeserver

If you're running this on a homeserver with a domain, expose it via a **Cloudflare Tunnel**:

1. Add a public hostname in your tunnel config pointing to `http://localhost:8501`
2. Access the dashboard at `https://flights.yourdomain.com`

## Project Structure

```
flight-hawk/
├── app.py              # Streamlit dashboard
├── main.py             # Background price checker & scheduler
├── flight_search.py    # Amadeus API integration
├── notifier.py         # Telegram notification sender
├── database.py         # SQLite database layer
├── auth.py             # OTP authentication module
├── docker-compose.yml  # Docker Compose config
├── Dockerfile          # Container build instructions
├── entrypoint.sh       # Runs both services in container
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable template
```

## License

MIT
