import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

########################################################################
# Notion
########################################################################
# ID of the database to archive
DATABASE_ID = os.getenv("DATABASE_ID")
# Access token of the integration (https://www.notion.so/my-integrations)
NOTION_ACCESS_TOKEN = os.getenv("NOTION_ACCESS_TOKEN")

########################################################################
# Twitter
########################################################################
# Twitter API keys (https://developer.twitter.com/en/portal/dashboard)
# Make sure to enable "Read, Write, and Direct Messages" permissions
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_TOKEN_SECRET = os.getenv("TWITTER_TOKEN_SECRET")
# Your Twitter username (without @)
TWITTER_USER_NAME = os.getenv("TWITTER_USER_NAME")

########################################################################
# Gyazo
########################################################################
# Gyazo API key (https://gyazo.com/oauth/applications)
# To be accessible to images semi-permanently, you need to upload images to gyazo.
# Notion API does not support uploading images.
GYAZO_ACCESS_TOKEN = os.getenv("GYAZO_ACCESS_TOKEN")

########################################################################
# Label Candidates
########################################################################
# Labels to be used for the zero-shot-classification model.
# If there is no label that matches the text, the text will be archived with wrong labels.
# You can add or remove labels as you like.
CANDIDATE_LABELS = [
    # AI/ML
    "natural language processing",
    "NLP",
    "computer vision",
    "reinforcement learning",
    "artificial intelligence",
    "machine learning",
    # AI/ML Techniques
    "transformer",
    "bert",
    "gpt",
    "diffusion model",
    "stable diffusion",
    "generative model",
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

########################################################################
# Path
########################################################################
# Path to the directory where the tmp file or log is located
CACHE_PATH = Path("content")
URLS_LOG_PATH = CACHE_PATH / "urls.log"
