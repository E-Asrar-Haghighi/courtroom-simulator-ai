from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration toggles
USE_LLAMA_INDEX = os.getenv("USE_LLAMA_INDEX", "True").lower() == "true"

print(f"DEBUG: USE_LLAMA_INDEX in settings.py is: {USE_LLAMA_INDEX}")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configurations
DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS = 2000
TEMPERATURE = 0.7

# Trial configuration
MAX_ROUNDS = 5
MAX_RESPONSE_LENGTH = 500

# File paths
LEGAL_DOCS_DIR = "legal_docs"
TRANSCRIPTS_DIR = "transcripts" 