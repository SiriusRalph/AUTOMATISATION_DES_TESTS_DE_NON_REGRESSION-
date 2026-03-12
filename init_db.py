import sqlite3

# Connexion (ou création) de la base de données
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Création de la table des utilisateurs
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Sauvegarder et fermer
conn.commit()
conn.close()

print("✅ Base de données créée avec succès.")
