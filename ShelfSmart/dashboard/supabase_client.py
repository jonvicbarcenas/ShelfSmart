
from dotenv import load_dotenv
import os
from supabase import create_client


# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Use service role key for backend operations (bypasses RLS)
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", SUPABASE_KEY)

# Create Supabase client with service role key for backend operations
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
