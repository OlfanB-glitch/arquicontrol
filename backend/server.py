from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from app.main import create_app


app = create_app()