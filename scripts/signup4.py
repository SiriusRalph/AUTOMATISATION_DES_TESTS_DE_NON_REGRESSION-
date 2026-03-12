import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mailtm import MailTMClient

def log(msg, ok=True):
    print(f"{'✅' if ok else '❌'} {msg}")

def fill(driver, fid, val):
    f = driver.find_element(By.ID, fid)
    driver.execute_script("arguments[0].scrollIntoView(true);", f)
    f.clear()
    f.send_keys(val)
    f.send_keys(Keys.TAB)
    time.sleep(0.5)

log("Création d'une boîte mail temporaire")

try:
    domains = MailTMClient.get_domains()
    domain = domains[0].domain
except Exception as e:
    log(f"Erreur récupération domaines : {e}, utilisation domaine par défaut", ok=False)
    domain = "punkproof.com"

password = "TempPass123!"
email_address = f"user{int(time.time())}@{domain}"

# Création du client non authentifié (anonyme)
client = MailTMClient()

# Création du compte (retourne un Account)
account = client.create_account(address=email_address, password=password)
log(f"Adresse générée : {account.address}")

# Authentification du client avec email + password pour récupérer le token
client.login(email_address, password)

# Maintenant client est authentifié et peut accéder aux messages

# --- Automatisation du navigateur ---
options = uc.ChromeOptions()
options.add_argument("--incognito")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://flightpass.royalairmaroc.com/")
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
    except: pass

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".signUp"))).click()
    time.sleep(2)

    fill(driver, "firstName", "Sara")
    fill(driver, "lastName", "Bouras")
    fill(driver, "email", email_address)
    fill(driver, "password", "MotDePasse@1234")
    fill(driver, "password-confirm", "MotDePasse@1234")
    fill(driver, "mobile", "0612345678")
    fill(driver, "birthDate", "01/01/2000")

    driver.find_element(By.CSS_SELECTOR, "button[type=submit], input[type=submit]").click()

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Vérification')]")))
        log("Page de vérification email OK")
    except:
        log("La page de vérification n'apparaît pas", ok=False)

    # --- Attente de l'email ---
    log("Attente de l'email de confirmation…")
    for i in range(24):  # 2 minutes max, toutes les 5 secondes
        msgs = client.get_messages()
        if msgs:
            msg = client.fetch(msgs[0].id)
            body = msg.html or msg.text
            break
        time.sleep(5)
    else:
        raise Exception("Aucun email reçu en 2 min")

    # --- Extraction du lien de confirmation ---
    match = re.search(r'https://flightpass\.royalairmaroc\.com[^\s"<>]+', body)
    if not match:
        raise Exception("Lien de confirmation introuvable dans l'email")
    link = match.group(0)
    log(f"Lien extrait : {link}")

    # --- Visite du lien pour activer le compte ---
    driver.get(link)
    time.sleep(5)
    page_content = driver.page_source.lower()
    if "activé" in page_content or "account" in page_content:
        log("Compte activé ✅")
    else:
        log("Confirmation non détectée", ok=False)

except Exception as e:
    log(f"Erreur : {e}", ok=False)

finally:
    time.sleep(5)
    driver.quit()
