""" Configuration settings for the application. """
from os import getenv
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

PORT = getenv("PORT", 80)

# Base URL for the application
BASE_URL = getenv("BASE_URL", "http://127.0.0.1:80")

# Endpoints
FILE_LINK = f"{BASE_URL}/file"
HINT_URL = f"{BASE_URL}/hint"
INSTRUCTIONS_LINK = f"{BASE_URL}/instructions"
QUESTION_LINK = f"{BASE_URL}/question"
SUBMISSION_LINK = f"{BASE_URL}/submit"

# Test team config
TEST_TEAM_ID = "123"
TEST_TEAM_NAME = "Team Test"

# Database settings
DATABASE_URI = getenv("DATABASE_URL")
DATABASE_NAME = "Enigma"

# Ensure essential environment variables are set
if not DATABASE_URI:
    raise ValueError("DATABASE_URL environment variable is not set.")
