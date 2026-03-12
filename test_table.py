import sqlite3

# Mets ici le même nom de ta base que dans app.py
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Cette requête va vérifier si la table test_results existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_results';")
table_exists = cursor.fetchone()

if table_exists:
    print("La table 'test_results' existe ! 🎉")
else:
    print("La table 'test_results' N'EXISTE PAS 😕")

conn.close()
