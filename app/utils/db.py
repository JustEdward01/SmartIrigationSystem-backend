import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
"""Supabase client used across the application."""

