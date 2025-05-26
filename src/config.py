"""
Configuration settings for OpenAI
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# File paths
DATA_DIR = "data/raw"
OUTPUT_DIR = "output"

# Analysis settings
TEMPERATURE = 0.3
MAX_TOKENS = 500 