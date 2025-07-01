import os
import sys
from dotenv import load_dotenv
from finlight_client import FinlightApi, ApiConfig
from finlight_client.models import GetArticlesParams
from supabase import create_client, Client

# Load env vars
load_dotenv()

# Append root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Initialize Finlight client
client = FinlightApi(config=ApiConfig(api_key=os.getenv("FINLIGHT_API_KEY")))


def fetch_finlight_articles(query):
    params = GetArticlesParams(query=query, limit=5)
    response = client.articles.get_basic_articles(params=params)
    return response.data if response and hasattr(response, 'data') else []


def analyze_articles_and_update(name, current_input_price, current_output_price):
    articles = fetch_finlight_articles(name)
    price_change_flag = None

    increase_keywords = ['price increase', 'cost rise', 'pricing update', 'price hike', 'increase in price']
    decrease_keywords = ['price decrease', 'cost reduction', 'discount', 'price drop', 'price cut', 'reduced cost']

    combined_texts = []
    for article in articles:
        title = article.title.lower() if article.title else ""
        summary = article.summary.lower() if article.summary else ""
        combined_texts.append(title + " " + summary)

    text_to_search = " ".join(combined_texts)

    if any(kw in text_to_search for kw in increase_keywords):
        price_change_flag = "Possible price increase - check latest pricing"
    elif any(kw in text_to_search for kw in decrease_keywords):
        price_change_flag = "Possible price decrease/discount - check latest pricing"

    if price_change_flag:
        # Update record in Supabase
        try:
            response = supabase.table("agents").update({
                "InputPrice": price_change_flag,
                "OutputPrice": price_change_flag
            }).eq("Name", name).execute()
            print(f"✅ Updated '{name}': {price_change_flag}")

        except Exception as exception:
            print(f"❌ Failed to update '{name}':", exception)
    else:
        print(f"No pricing changes detected in news for '{name}'")


def main():
    try:
        response = supabase.table("agents").select("Name,InputPrice,OutputPrice").execute()
        print("Fetched agents info from agents table successfully!")
        agents = response.data
        for agent in agents:
            name = agent.get("Name")
            input_price = agent.get("InputPrice")
            output_price = agent.get("OutputPrice")
            print(f"🔎 Checking news for AI agent: {name}")
            analyze_articles_and_update(name, input_price, output_price)
    except Exception as exception:
        print("❌ Failed to fetch agents:",exception)
        return

if __name__ == "__main__":
    main()
