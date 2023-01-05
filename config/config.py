import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Path
JSON_PATH = Path("notion.json")
JAVASCRIPT_PATH = Path("js/markdown.js")
URLS_LOG_PATH = Path("urls.log")

# Notion
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_ACCESS_TOKEN = os.getenv("NOTION_ACCESS_TOKEN")

# Twitter
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_TOKEN_SECRET = os.getenv("TWITTER_TOKEN_SECRET")
TWITTER_USER_NAME = os.getenv("TWITTER_USER_NAME")

# Label Candidates
CANDIDATE_LABELS = [
    # AI/ML
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "artificial intelligence",
    "machine learning",
    # Programming Languages
    "sql",
    "python",
    "javascript",
    "shell script",
    # Services
    "aws",
    "google cloud",
    # Tools
    "docker",
    "kubernetes",
    "django",
    "fastapi",
    "pytorch",
    "tensorflow",
    "api",
    "git",
    # Genres
    "web",
    "lifehack",
    "business",
]
