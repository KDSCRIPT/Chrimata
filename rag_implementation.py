import json
import sqlite3
import numpy as np
import faiss
import google.generativeai as genai
import re


# Setup Gemini API
genai.configure(api_key="AIzaSyBxESJZhk8uUUMzJxJUZou-eu3b5pIrn6A")
chat_model = genai.GenerativeModel("gemini-2.0-flash")

# -----------------------------
# Utility: Enrich agent data using Gemini
# -----------------------------
def enrich_agent_data(agent):
    prompt = f"""
You are an AI product expert.

Take the following basic AI tool data and enhance each field with more clarity and detail. Make sure to elaborate the 'Use Case' by listing specific tasks. Also, make each field useful for cost estimation and quality assessment.

Example data:
Name: {agent['Name']}
Provider: {agent['Provider']}
Use Case: {agent['UseCase']}
Category: {agent['Category']}
Input Price: {agent['InputPrice']}
Output Price: {agent['OutputPrice']}
Integration: {agent['Integration']}
Free Tier: {agent['FreeTier']}
Latency: {agent['Latency']}
Website: {agent['Website']}
Alternatives: {agent['Alternatives']}
This is a JSON object with keys:
Name, Provider, UseCase, Category, InputPrice, OutputPrice, Integration, FreeTier, Latency, Website, Alternatives.
Return updated fields in JSON format with the same keys.
No need to give anything else other than the JSON object.
"""

    response = chat_model.generate_content(prompt)
    print(f"\n🔎 Prompt sent to Gemini:\n{prompt}")
    print(f"\n📨 Gemini raw response:\n{response.text}")

    pattern = r'"?(Name|Provider|UseCase|Category|InputPrice|OutputPrice|Integration|FreeTier|Latency|Website|Alternatives)"?\s*:\s*["“]?(.+?)["”]?(?:,|\n|$)'
    matches = re.findall(pattern, response.text, re.DOTALL)

    enriched = {key: agent.get(key, "") for key in agent}  # Start with fallback as original

    for key, value in matches:
        cleaned_key = key.strip()
        cleaned_value = value.strip().rstrip(',')
        enriched[cleaned_key] = cleaned_value

    # Sanity check
    missing_fields = [k for k in agent if k not in enriched]
    if missing_fields:
        print(f"⚠️ Missing fields in regex parse: {missing_fields} — fallback to original values.")

    return enriched

# -----------------------------
# Step 1: Enrich All Data in DB
# -----------------------------
def enrich_all_agents():
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()

    # Ensure the Enriched column exists
    try:
        cursor.execute("ALTER TABLE agents ADD COLUMN Enriched BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Already exists

    cursor.execute("SELECT * FROM agents WHERE Enriched = 0")
    rows = cursor.fetchall()

    enriched_rows = []
    for row in rows:
        agent = {
            "Name": row[0],
            "Provider": row[1],
            "UseCase": row[2],
            "Category": row[3],
            "InputPrice": row[4],
            "OutputPrice": row[5],
            "Integration": row[6],
            "FreeTier": row[7],
            "Latency": row[8],
            "Website": row[9],
            "Alternatives": row[10]
        }

        enriched = enrich_agent_data(agent)
        enriched_rows.append(tuple([
            enriched["Name"], enriched["Provider"], enriched["UseCase"], enriched["Category"],
            enriched["InputPrice"], enriched["OutputPrice"], enriched["Integration"],
            enriched["FreeTier"], enriched["Latency"], enriched["Website"], enriched["Alternatives"], 1  # Enriched = True
        ]))

    cursor.executemany('''
        INSERT OR REPLACE INTO agents 
        (Name, Provider, UseCase, Category, InputPrice, OutputPrice, Integration, FreeTier, Latency, Website, Alternatives, Enriched)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', enriched_rows)

    conn.commit()
    conn.close()
    print("✅ Enriched only new agents and marked them in the DB.")


# -----------------------------
# Step 2: Build FAISS Index
# -----------------------------
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

def build_faiss_index():
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Name, UseCase, Category FROM agents")
    rows = cursor.fetchall()
    conn.close()

    embeddings = []
    agent_map = {}

    for i, (name, use_case, category) in enumerate(rows):
        combined_text = f"{use_case}. Category: {category}"
        embedding = get_embedding(combined_text)
        embeddings.append(embedding)
        agent_map[i] = name

    vectors = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(vectors)

    faiss.write_index(index, "agents_faiss.index")
    with open("index_map.json", "w") as f:
        json.dump(agent_map, f)

    print("✅ FAISS index built and saved.")

# -----------------------------
# Step 3: Query and Rank Agents
# -----------------------------
def generate_justification(query, agent_info):
    prompt = f"""
You are helping a company choose an AI agent for the task: "{query}".

The following AI agent is a candidate:
Name: {agent_info['Name']}
Use Case: {agent_info['UseCase']}
Category: {agent_info['Category']}
Input Price: {agent_info['InputPrice']}
Output Price: {agent_info['OutputPrice']}
Latency: {agent_info['Latency']}

Explain why this tool is a good choice for the task.
"""
    response = chat_model.generate_content(prompt)
    return response.text.strip()

def search_agents_with_reason(query, top_k=5):
    index = faiss.read_index("agents_faiss.index")
    with open("index_map.json", "r") as f:
        agent_map = json.load(f)

    query_embedding = get_embedding(query)
    D, I = index.search(np.array([query_embedding]).astype('float32'), top_k)

    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()

    results = []
    for idx in I[0]:
        if str(idx) not in agent_map:
            continue
        name = agent_map[str(idx)]
        cursor.execute("SELECT * FROM agents WHERE Name = ?", (name,))
        row = cursor.fetchone()
        if row:
            agent_info = {
                "Name": row[0],
                "Provider": row[1],
                "UseCase": row[2],
                "Category": row[3],
                "InputPrice": row[4],
                "OutputPrice": row[5],
                "Integration": row[6],
                "FreeTier": row[7],
                "Latency": row[8],
                "Website": row[9],
                "Alternatives": row[10]
            }
            reason = generate_justification(query, agent_info)
            results.append((agent_info, reason))

    conn.close()
    return results

# -----------------------------
# Mock Input From Previous Agent
# -----------------------------
mock_input = """
We have a $10,000 monthly budget, need response latency under 2 seconds for most operations,
and aim for high output quality in text summarization, image generation, and structured output.
Ideal tools would support SDKs or APIs for easy integration and offer transparent pricing models.
"""

# -----------------------------
# Run
# -----------------------------
def main():
    print("📥 Enriching agent data from Gemini...")
    enrich_all_agents()

    print("📊 Building FAISS index...")
    build_faiss_index()

    print("🔍 Searching with mock input from first agent...")
    results = search_agents_with_reason(mock_input)

    for i, (agent, reason) in enumerate(results, start=1):
        print(f"\n🔹 Result #{i}")
        print(f"🛠️  Name       : {agent['Name']}")
        print(f"🏷️  Category   : {agent['Category']}")
        print(f"📋 Use Case   : {agent['UseCase']}")
        print(f"💲 Input Price: {agent['InputPrice']}")
        print(f"💲 Output Price: {agent['OutputPrice']}")
        print(f"⚡ Latency    : {agent['Latency']}")
        print(f"🌐 Website    : {agent['Website']}")
        print(f"💡 Reason     : {reason}")

if __name__ == "__main__":
    main()
