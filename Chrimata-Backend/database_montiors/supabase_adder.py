import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

# Load JSON data
os.makedirs('data', exist_ok=True)
with open('data/data.json', 'r') as f:
    data = json.load(f)

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY)

# Insert data into Supabase
for item in data:
    payload = {
        "Name": item.get("Name"),
        "Provider": item.get("Provider"),
        "UseCase": item.get("Use Case"),
        "Category": item.get("Category"),
        "InputPrice": item.get("Input Price"),
        "OutputPrice": item.get("Output Price"),
        "Integration": item.get("Integration"),
        "FreeTier": item.get("Free Tier"),
        "Latency": item.get("Latency"),
        "Website": item.get("Website"),
        "Alternatives": item.get("Alternatives"),
        "Enriched":False
    }
    try:
        response = supabase.table("agents").insert(payload).execute()
        print("Added agent info in agent table successfully!")
    except Exception as exception:
        print("error:",exception)
