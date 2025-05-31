import json
import sqlite3

# Load JSON data from file
with open('data.json', 'r') as f:
    data = json.load(f)  # data is a list of dicts

# Connect to SQLite DB (or create)
conn = sqlite3.connect('agents.db')
cursor = conn.cursor()

# Create table with columns matching JSON keys
cursor.execute('''
CREATE TABLE IF NOT EXISTS agents (
    Name TEXT,
    Provider TEXT,
    UseCase TEXT,
    Category TEXT,
    InputPrice TEXT,
    OutputPrice TEXT,
    Integration TEXT,
    FreeTier TEXT,
    Latency TEXT,
    Website TEXT,
    Alternatives TEXT
)
''')

# Insert data
for item in data:
    cursor.execute('''
        INSERT INTO agents (Name, Provider, UseCase, Category, InputPrice, OutputPrice, Integration, FreeTier, Latency, Website, Alternatives)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        item.get("Name"),
        item.get("Provider"),
        item.get("Use Case"),
        item.get("Category"),
        item.get("Input Price"),
        item.get("Output Price"),
        item.get("Integration"),
        item.get("Free Tier"),
        item.get("Latency"),
        item.get("Website"),
        item.get("Alternatives")
    ))

conn.commit()
conn.close()
