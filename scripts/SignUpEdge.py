from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time

# ✅ Configuration d'Edge
options = Options()
options.add_argument("--inprivate")  # 🕵️ Mode navigation privée
options.add_argument("--start-maximized")  # Ouvrir en plein écran

# 🔧 Chemin vers le WebDriver (modifie si besoin)
service = Service(executable_path="msedgedriver.exe")

# 🚀 Démarrage d'Edge
driver = webdriver.Edge(service=service, options=options)

# 🌐 Aller à la page de test (exemple RAM sign-up)
driver.get("https://flightpass.royalairmaroc.com/realms/flightpass/login-actions/registration?client_id=ram-flightpass-back")

# 🕒 Attendre pour voir ce qu’il se passe (tu peux remplacer plus tard par des tests automatiques)
time.sleep(15)

# ❌ Fermer le navigateur à la fin
driver.quit()
