# AI Shop Assistant

AI Shop Assistant is a simple full-stack e-commerce application that combines a React frontend, a Python FastAPI backend, and a SQLite database. It includes product browsing, keyword and natural-language searching, product filters, a shopping cart, and an AI shopping assistant that works with a fallback mode when no API key is configured.

## Project Overview

The project demonstrates a clean monolithic architecture:

React
↓
FastAPI
↓
Services
↓
SQLite Database

AI Chat flow:

React
↓
FastAPI
↓
AI Service
↓
Product Search
↓
SQLite
↓
AI Response

## Features

- Product browsing
- Keyword search
- Search ranking using basic relevance scoring
- Natural-language search
- Product filtering by category and price
- Product detail view
- Shopping cart management
- AI chatbot assistant with fallback logic
- Product recommendation system
- Product comparison helpers
- REST API with FastAPI docs
- Docker configuration for backend and frontend

## Technologies

- React
- Vite
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Docker
- Pytest

## Local Setup

### Backend

1. Navigate to the backend folder.
2. Create a virtual environment if you want one.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Start the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. Navigate to the frontend folder.
2. Install dependencies:

```bash
npm install
```

3. Start the dev server:

```bash
npm run dev -- --host 0.0.0.0
```

### Docker Compose

From the project root:

```bash
docker compose up --build
```

The frontend is available on http://localhost:80 and the backend is available on http://localhost:8000.

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=sqlite:///./ecommerce.db
OPENAI_API_KEY=
AI_MODEL=gpt-4o-mini
FRONTEND_URL=http://localhost:5173
HOST=0.0.0.0
PORT=8000
```

## API Documentation

The FastAPI app exposes automatic docs at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Future Improvements

- PostgreSQL migration
- Elasticsearch/OpenSearch integration
- Vector database for better recommendations
- Authentication and user carts
- Kubernetes manifests
- CI/CD workflows
- Payment gateway integration

## Notes

This project intentionally keeps the code simple and beginner-friendly while still demonstrating important e-commerce and AI assistant patterns.
