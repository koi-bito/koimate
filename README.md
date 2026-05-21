# 🛒 Koimate

A smart product recommendation web application built with **Flask**. Koimate tracks user behavior and uses **TF-IDF** based content filtering to deliver personalized product suggestions — all wrapped in a clean REST API backend.

---

## ✨ Features

- 🔐 **JWT Authentication**: Secure user registration and login
- 🤖 **Smart Recommendations**: TF-IDF content-based filtering powered by scikit-learn
- 📊 **Behavior Tracking**: Logs user actions (views, purchases, add-to-cart) to improve suggestions
- 📈 **Analytics**: Insights into user interaction patterns
- 🧩 **Modular Architecture**: Clean Blueprint-based route organization
- 🗃️ **MySQL Database**: Persistent storage via Flask-SQLAlchemy + PyMySQL

---

## 🗂️ Project Structure

```
koimate/
├── app.py              # App factory and blueprint registration
├── config.py           # Configuration (DB URI, JWT secret, etc.)
├── models.py           # SQLAlchemy models (User, Product, UserBehavior, UserInput)
├── mock_data.py        # Seed data for development
├── requirements.txt    # Python dependencies
├── routes/
│   ├── auth.py         # /api/auth — Register & Login
│   ├── recommender.py  # /api/recommend — Product recommendations
│   ├── analytics.py    # /api/analytics — Usage analytics
│   ├── tracking.py     # /api/track — Behavior event tracking
│   └── pages.py        # Frontend page routes
├── services/           # Business logic (recommendation engine, etc.)
├── static/             # CSS, JS, images
└── templates/          # Jinja2 HTML templates
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL database

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/koi-bito/koimate.git
   cd koimate
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the app**

   Create a `.env` file (or edit `config.py`) with your settings:

   ```env
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=mysql+pymysql://user:password@localhost/koimate_db
   ```

5. **Run the application**

   ```bash
   python app.py
   ```

   The server starts at `http://localhost:5000` with the database tables auto-created on first run.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT token |
| `GET` | `/api/recommend` | Get personalized product recommendations |
| `POST` | `/api/track` | Log a user behavior event |
| `GET` | `/api/analytics` | Retrieve analytics data |

> All protected routes require a `Bearer <token>` in the `Authorization` header.

---

## 🧠 How Recommendations Work

Koimate uses **TF-IDF (Term Frequency–Inverse Document Frequency)** content-based filtering:

1. Each product has a `features_text` field combining its name, category, and description.
2. When a user provides input (past purchases, needs, shortages), those are vectorized alongside product features.
3. Cosine similarity is calculated to rank the most relevant products.
4. User behavior (views, purchases, cart additions) further refines future recommendations.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, Flask-Blueprints |
| Auth | Flask-JWT-Extended |
| Database ORM | Flask-SQLAlchemy |
| Database | MySQL (via PyMySQL) |
| ML / Recommendations | scikit-learn, NumPy, Pandas |
| Frontend | HTML, CSS, JavaScript (Jinja2 templates) |
| Security | Werkzeug password hashing, cryptography |

---

## 📦 Dependencies

```
Flask
Flask-SQLAlchemy
Flask-JWT-Extended
Flask-Cors
PyMySQL
scikit-learn
numpy
pandas
python-dotenv
cryptography
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push and open a Pull Request

---

## 📄 License

This project is open source. Add your preferred license here.
