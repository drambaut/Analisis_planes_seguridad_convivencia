"""
Configuration settings for Azure OpenAI
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_ENDPOINT = "https://instaciapdt.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o-mini"

# File paths
DATA_DIR = "data/raw"
OUTPUT_DIR = "output"

# Analysis settings
TEMPERATURE = 0.3
MAX_TOKENS = 500 