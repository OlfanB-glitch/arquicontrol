import os
from pathlib import Path


class Settings:
    def __init__(self):
        self.project_name = "ArquiControl API"
        self.api_prefix = "/api"
        self.mongo_url = os.environ["MONGO_URL"]
        self.db_name = os.environ["DB_NAME"]
        self.cors_origins = os.environ["CORS_ORIGINS"].split(",")
        self.jwt_secret_key = os.environ["JWT_SECRET_KEY"]
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 720
        self.uploads_dir = Path(os.environ["UPLOADS_DIR"])


settings = Settings()