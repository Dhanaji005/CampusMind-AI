# =====================================================
# CAMPUSMIND AI - CONFIGURATION
# =====================================================

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv()


class Config:
    # -----------------------------------------------------
    # APPLICATION SETTINGS
    # -----------------------------------------------------
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "campusmind-ai-super-secret-jwt-token-signing-key-2026-enterprise-grade"
    )
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        SECRET_KEY
    )
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "24"))
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # -----------------------------------------------------
    # MYSQL SETTINGS (Optional Local Database)
    # -----------------------------------------------------
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "campusmind_ai")

    # -----------------------------------------------------
    # OPENROUTER SETTINGS (NVIDIA Nemotron & Vision)
    # -----------------------------------------------------
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv(
        "OPENROUTER_MODEL",
        "nex-agi/nex-n2.5-mini:free"
    )
    OPENROUTER_FALLBACK_MODELS = [
        "nex-agi/nex-n2.5-mini:free",
        "nex-agi/nex-n2.5-pro:free",
        "nvidia/nemotron-3.5-lightning:free",
        "google/gemma-4-31b-it:free",
        "deepseek/deepseek-chat",
    ]
    OPENROUTER_TIMEOUT = int(os.getenv("OPENROUTER_TIMEOUT", "15"))
    OPENROUTER_BASE_URL = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1"
    )
    OPENROUTER_APP_NAME = os.getenv(
        "OPENROUTER_APP_NAME",
        "CampusMind AI Smart Campus Platform"
    )
    OPENROUTER_APP_URL = os.getenv(
        "OPENROUTER_APP_URL",
        "http://localhost:5000"
    )

    # -----------------------------------------------------
    # RAG & EMBEDDING SETTINGS
    # -----------------------------------------------------
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "openai/text-embedding-3-small"
    )
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "6"))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.20"))
    RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1800"))
    RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "250"))

    # -----------------------------------------------------
    # SUPABASE SETTINGS (Cloud PostgreSQL + Storage)
    # -----------------------------------------------------
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
