import sqlite3
from finlight_client import FinlightApi, ApiConfig
from finlight_client.models import GetArticlesParams

# Initialize Finlight client once
client = FinlightApi(
    config=ApiConfig(
        api_key="sk_a7c538f8cf9f7b36483c96c06a8b37fdb07e1045ea01e6f54f4478f3b414bbcb"
    )
)

def fetch_finlight_articles(query):
    params = GetArticlesParams(query=query, limit=5)  # Fetch recent 5 articles
    response = client.articles.get_basic_articles(params=params)
    return response.data if response and hasattr(response, 'data') else []

def analyze_articles_and_update(name, current_input_price, current_output_price):
    articles = fetch_finlight_articles(name)
    price_change_flag = None

    # Keywords for detecting price-related news (increase or decrease)
    increase_keywords = ['price increase', 'cost rise', 'pricing update', 'price hike', 'increase in price']
    decrease_keywords = ['price decrease', 'cost reduction', 'discount', 'price drop', 'price cut', 'reduced cost']

    combined_texts = []
    for article in articles:
        title = article.title.lower() if article.title else ""
        summary = article.summary.lower() if article.summary else ""
        combined_texts.append(title + " " + summary)

    text_to_search = " ".join(combined_texts)

    # Check for price increase keywords
    if any(kw in text_to_search for kw in increase_keywords):
        price_change_flag = "Possible price increase - check latest pricing"
    # Check for price decrease keywords
    elif any(kw in text_to_search for kw in decrease_keywords):
        price_change_flag = "Possible price decrease/discount - check latest pricing"

    if price_change_flag:
        # Update both Input Price and Output Price in SQLite DB with the flag message
        conn = sqlite3.connect('agents.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE agents SET InputPrice = ?, OutputPrice = ? WHERE Name = ?",
            (price_change_flag, price_change_flag, name)
        )
        conn.commit()
        conn.close()
        print(f"Updated pricing info for '{name}': {price_change_flag}")
    else:
        print(f"No pricing changes detected in news for '{name}'")

def main():
    # Connect to DB and fetch all agent names and their prices
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name, InputPrice, OutputPrice FROM agents")
    agents = cursor.fetchall()
    conn.close()

    for name, input_price, output_price in agents:
        print(f"Checking news for AI agent: {name}")
        analyze_articles_and_update(name, input_price, output_price)

if __name__ == "__main__":
    main()
