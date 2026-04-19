# Purpose Marketing Analytics Dashboard

> Interactive visualizations for Purpose Marketing spend and application data — built with AI assistance and deployed on Digital Ocean App Platform.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![Digital Ocean](https://img.shields.io/badge/Deployed_on-Digital_Ocean-0080FF)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

This application provides a centralized dashboard for exploring, filtering, and visualizing Purpose Marketing spend and application performance data. It enables teams to surface trends, compare program effectiveness, and make data-driven decisions across marketing initiatives.

The codebase was generated with the assistance of **CODEX** and is designed to be deployed as a web application on Digital Ocean App Platform.

---

## Features

- Interactive charts and visualizations for marketing spend data
- Application performance tracking across programs and time periods
- Filterable views by date range, program type, and spend category
- Responsive layout optimized for desktop and tablet
- Multi-user access via cloud deployment on Digital Ocean

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Deployment | Digital Ocean App Platform |
| AI Assisted By | CODEX |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-org/purpose-marketing-dashboard.git
cd purpose-marketing-dashboard
```

**2. Set up environment variables**
```bash
cp .env.example .env
# Open .env and fill in your values
```

**3. Run the backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**4. Run the frontend**
```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

---

## Environment Variables

| Variable | Description |
|---|---|
| `API_KEY` | Backend API key for authenticating requests |
| `DATABASE_URL` | Connection string for your data source |
| `VITE_API_URL` | Backend URL used by the React frontend |

See `.env.example` for the full list of required variables.

---

## Deployment (Digital Ocean App Platform)

1. Push your code to GitHub
2. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps) and create a new app
3. Connect your GitHub repository
4. Configure two components:
   - **Backend**: source directory `/backend`, run command `uvicorn main:app --host 0.0.0.0 --port 8080`
   - **Frontend**: source directory `/frontend`
5. Add all environment variables from `.env.example` in the Digital Ocean dashboard
6. Attach a storage volume at `/data` for persistent data
7. Deploy — Digital Ocean will auto-deploy on every push to `main`

---

## Project Structure
