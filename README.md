# The University Management Backend Service is a backend application developed using FastAPI, designed to manage users, courses, and roles in the university system.

# The service implements:
 - student and faculty management
 - faculty & section-based filtering
 - course distribution
 - role-based access control 
 - authentication (including facial recognition)

# 🛠️ Technologies 
 - FastAPI — Web framework
 - SQLAlchemy (Async) — ORM
 - Alembic — Database migrations
 - PostgreSQL — Database
 - face_recognition — Biometric authentication

# ⚙️ Installation (Python 3.11)

 - Create virtual environment
 ```
 python -m venv venv
 ```

 - Activate environment
 ```
 ./venv/Scripts/activate
 ```
 - Install dependencies
 ```
 pip install -r requirements.txt
 ``` 
 - Setup environment variables 
   - Create .env file
   ```
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=postgresql+asyncpg://user:<PASSWORD>@localhost:5432/<DB_NAME>
   ```
 - Start server
 ```
 python -m src.app.main
 ```

