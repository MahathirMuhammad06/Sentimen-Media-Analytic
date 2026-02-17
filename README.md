










Cara Untuk melakukan setup backendnya
cd backend-media-analytic-end

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.repository import init_db; init_db()"

# Run API server
python -m uvicorn src.api.app:app --reload

# Test API
curl http://localhost:8000/v1/articles
