import sqlite3

def remove_duplicate_agents():
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()

    # Delete rows where rowid is not the minimum for a given Name (i.e., duplicates)
    cursor.execute('''
        DELETE FROM agents
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM agents
            GROUP BY Name
        )
    ''')

    conn.commit()
    conn.close()
    print("🧹 Removed duplicate agents based on Name column.")

if __name__ == "__main__":
    remove_duplicate_agents()
