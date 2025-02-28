from flask import Flask
from supabase import create_client, Client
from config import Config


app = Flask(__name__)


supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


from app import routes
