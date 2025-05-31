import sqlite3
import requests

API_KEY = "f1e774ac922c49ffb01c58c9fb8e92ca"
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
DB_PATH = "agents.db"

def get_agents_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rowid, Name, Provider, "Use Case", Category, "Input Price", "Output Price", 
               Integration, "Free Tier", Latency, Website, Alternatives 
        FROM agents
    """)
    agents = cursor.fetchall()
    conn.close()
    return agents

def update_prices(rowid, new_input_price, new_output_price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE agents 
        SET "Input Price" = ?, "Output Price" = ?
        WHERE rowid = ?
    """, (new_input_price, new_output_price, rowid))
    conn.commit()
    conn.close()

def search_news_for_price_increase(agent_name):
    query = f"{agent_name} price OR cost OR pricing OR increase"
    params = {
        "q": query,
        "apiKey": API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
    }
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print(f"Error fetching news for {agent_name}: {data.get('message')}")
        return False

    articles = data.get("articles", [])
    keywords = [
        "price increase", "cost rise", "pricing update", 
        "price hike", "cost increase", "price change"
    ]

    for article in articles:
        title = article.get("title", "").lower()
        # print(title)
        description = (article.get("description") or "").lower()
        combined_text = title + " " + description
        if any(keyword in combined_text for keyword in keywords):
            return True  # Found price increase news
    return False

def main():
    agents = get_agents_from_db()
    updated_agents = []

    for agent in agents:
        rowid, name, *rest = agent
        print(f"Checking news for {name}...")
        if search_news_for_price_increase(name):
            print(f" -> Price increase news found for {name}, updating database...")
            update_prices(rowid, "Increased - Check News", "Increased - Check News")
            updated_agents.append(name)
        else:
            print(f" -> No price increase news found for {name}.")

    print("\nSummary of updated agents:")
    if updated_agents:
        for agent_name in updated_agents:
            print(f" - {agent_name}")
    else:
        print("No agents had price updates.")

if __name__ == "__main__":
    main()
