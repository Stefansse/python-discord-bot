# cogs/playlist.py
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def init_db():
    """Ensure playlist table exists with UNIQUE song constraint."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist (
                id SERIAL PRIMARY KEY,
                song TEXT NOT NULL UNIQUE,
                author VARCHAR(100) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✅ Playlist table initialized in Postgres")
    except Exception as e:
        logger.error(f"Error initializing playlist DB: {e}")

def get_playlist():
    """Return all songs from the playlist."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT song, author FROM playlist ORDER BY song")
        songs = cursor.fetchall()
        conn.close()
        # We return url=None because the table doesn't store it
        return [{"song": row["song"], "author": row["author"], "url": None} for row in songs]
    except Exception as e:
        logger.error(f"Error fetching playlist: {e}")
        return []

def add_song_to_playlist(song: str, author: str):
    """Add a song to the playlist if it doesn't exist."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO playlist (song, author) VALUES (%s, %s) ON CONFLICT (song) DO NOTHING",
            (song, author)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error adding song to playlist: {e}")

def get_song_url(song: str):
    """Since URL is not stored, always return None."""
    return None
