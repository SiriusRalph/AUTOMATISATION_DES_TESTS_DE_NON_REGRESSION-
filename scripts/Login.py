import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Infos du compte à tester (modifie-les avec ton vrai compte de test)
EMAIL = "dilogo7206@ihnpo.com"
PASSWORD = "SARAbs1234*"

# ✅ Initialisation navigateur incognito
options = uc.ChromeOptions()
options.add_argument("--incognito")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

def log(msg, ok=True):
    print(f"{'✅' if ok else '❌'} {msg}")

try:
    # 1. Aller à la page d'accueil
    log("Ouverture de la page d'accueil")
    driver.get("https://flightpass.royalairmaroc.com/")
    time.sleep(3)

    # 2. Accepter les cookies s'ils apparaissent
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        cookie_btn.click()
        log("Cookies acceptés")
    except:
        log("Bannière cookie non présente (ok)", ok=True)

    # 3. Cliquer sur "Se connecter" / "Login"
    login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".signIn")))
    login_btn.click()
    log("Clic sur bouton de connexion")

    # 4. Saisie des identifiants
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
    log("Soumission du formulaire de connexion")

    # 5. Vérification que la connexion est réussie
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-name")))
        log("Connexion réussie ✅")
    except:
        log("Échec de connexion ou mauvais identifiants", ok=False)

except Exception as e:
    log(f"Erreur inattendue : {str(e)}", ok=False)

finally:
    time.sleep(5)
    driver.quit()
