from dotenv import load_dotenv
import os 

load_dotenv()


CREDENTIALS_FILE_PATH = os.getenv("CREDENTIALS_FILE_PATH")
GOOGLE_SERVICE_EMAIL = os.getenv("GOOGLE_SERVICE_EMAIL")
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")


