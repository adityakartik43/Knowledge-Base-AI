import os

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5432/knowbase_test")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("SERVICE_API_KEY", "test-service-key")
