# 🛒 Koimate

A Flask-based e-commerce recommendation engine that tracks real user behavior — views, cart additions, purchases — and uses **TF-IDF + KNN content-based filtering** to deliver personalized product suggestions that improve with every interaction.

> Achieved ~22% reduction in irrelevant recommendations compared to a static/category-based baseline.

---

## How It Works

Koimate doesn't just recommend based on product metadata. It builds a behavioral profile per user:

1. Every interaction (view, add-to-cart, purchase) is logged via the tracking API
2. Each product's `features_text` (name + category + description) is vectorized using TF-IDF
3. User input is vectorized into the same space and cosine similarity ranks candidate products
4. KNN finds the K nearest products in feature space to the user's current context
5. Behavioral signals (purchase weight > cart > view) re-rank results for that specific user

The result: recommendations that shift based on what you actually do, not just what category you browsed.

---

## Features

- **TF-IDF + KNN Recommendations** — content-based filtering with behavioral re-ranking
- **Behavior Tracking** — logs views, purchases, add-to-cart events per user
- **JWT Authentication** — secure registration, login, protected routes
- **Analytics Endpoint** — user interaction pattern insights
- **Modular Architecture** — Flask Blueprints, clean service/route separation
- **MySQL Backend** — Flask-SQLAlchemy + PyMySQL, tables auto-created on first run

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask, Flask-Blueprints |
| ML | scikit-learn (TF-IDF, KNN, cosine similarity), NumPy, Pandas |
| Auth | Flask-JWT-Extended, Werkzeug |
| Database | MySQL via Flask-SQLAlchemy + PyMySQL |
| Frontend | HTML, CSS, JavaScript (Jinja2) |

---

## Project Structure

```
koimate/
├── app.py              # App factory, blueprint registration
├── config.py           # DB URI, JWT secret, environment config
├── models.py           # SQLAlchemy models: User, Product, UserBehavior, UserInput
├── mock_data.py        # Dev seed data
├── requirements.txt
├── routes/
│   ├── auth.py         # /api/auth — register & login
│   ├── recommender.py  # /api/recommend — personalized recommendations
│   ├── analytics.py    # /api/analytics — usage analytics
│   ├── tracking.py     # /api/track — behavior event logging
│   └── pages.py        # Frontend routes
└── services/           # Recommendation engine and business logic
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login, receive JWT |
| `GET` | `/api/recommend` | Get personalized recommendations |
| `POST` | `/api/track` | Log a behavior event |
| `GET` | `/api/analytics` | Retrieve interaction analytics |

All protected routes require `Authorization: Bearer <token>`.

---

## Setup

**Prerequisites:** Python 3.8+, MySQL

```bash
git clone https://github.com/koi-bito/koimate.git
cd koimate
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=mysql+pymysql://user:password@localhost/koimate_db
```

```bash
python app.py
# Runs at http://localhost:5000
```

---

## Context

Koimate was built as a deep dive into recommendation systems before moving on to more complex AI projects. The TF-IDF + KNN approach is intentionally classical — the goal was to understand the math behind content filtering before abstracting it away with embedding models. The behavioral re-ranking layer was added after noticing that pure content similarity ignored actual user intent.
