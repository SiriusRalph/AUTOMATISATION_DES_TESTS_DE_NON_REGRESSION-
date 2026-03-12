import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from openpyxl import Workbook

logs = []

def log_success(msg):
    print(f"✅ {msg}")
    logs.append(("Succès", msg))

def log_info(msg):
    print(f"🔹 {msg}")
    logs.append(("Info", msg))

def log_fail(msg):
    print(f"❌ {msg}")
    logs.append(("Erreur", msg))

def check_visibility(driver, field_id, label):
    try:
        driver.find_element(By.ID, field_id)
        log_success(f"Champ '{label}' visible")
    except:
        log_fail(f"Champ '{label}' non trouvé")

def check_error_message(driver, field_id, expected, custom_selector=None):
    try:
        if custom_selector:
            error = driver.find_element(By.CSS_SELECTOR, custom_selector)
        else:
            error = driver.find_element(By.CSS_SELECTOR, f"#{field_id} ~ .error-message, #{field_id}-error, .invalid-feedback")
        if expected.lower() in error.text.lower():
            log_success(f"Message d'erreur pour {field_id} : « {error.text.strip()} »")
        else:
            log_fail(f"Message incorrect pour {field_id} : « {error.text.strip()} »")
    except:
        log_fail(f"Aucun message d'erreur affiché pour {field_id}")

def check_password_error(driver):
    try:
        # Attendre au maximum 1 seconde que le span apparaisse
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.ID, "input-error-password"))
        )
        # Lire le message immédiatement via JS
        error_text = driver.execute_script("""
            let el = document.getElementById('input-error-password');
            return el ? el.textContent.trim() : '';
        """)
        if error_text:
            log_success(f"✅ Message d'erreur pour le mot de passe : « {error_text} »")
        else:
            log_fail("⚠️ Élément trouvé mais texte vide")
    except Exception as e:
        log_fail(f"❌ Aucun message d'erreur affiché pour le mot de passe")


def fill_and_tab(driver, field_id, value):
    field = driver.find_element(By.ID, field_id)
    field.clear()
    field.send_keys(value)
    field.send_keys(Keys.TAB)
    time.sleep(0.5)

options = uc.ChromeOptions()
options.add_argument("--incognito")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    log_info("Ouverture de la page d'accueil")
    driver.get("https://flightpass.royalairmaroc.com/")
    time.sleep(3)
    log_success("Page d'accueil ouverte")

    try:
        cookie_home = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        cookie_home.click()
        log_success("Cookie banner accepté sur la page d'accueil")
    except:
        log_fail("Cookie banner non trouvé sur la page d'accueil")

    print()
    log_info("Recherche et clic sur le bouton 'Register'")
    try:
        register_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".signUp")))
        register_btn.click()
        log_success("Clic sur le bouton 'Register' effectué avec succès")
    except:
        log_fail("Impossible de cliquer sur le bouton 'Register'")

    time.sleep(2)
    log_success("Page d'inscription ouverte")

    try:
        cookie_signup = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        cookie_signup.click()
        log_success("Cookie banner accepté sur la page d'inscription")
    except:
        pass

    print()
    log_info("Vérification de la visibilité des champs")
    check_visibility(driver, "firstName", "Prénom")
    check_visibility(driver, "lastName", "Nom")
    check_visibility(driver, "email", "Email")
    check_visibility(driver, "password", "Mot de passe")
    check_visibility(driver, "password-confirm", "Confirmation mot de passe")
    check_visibility(driver, "mobile", "Numéro mobile")
    check_visibility(driver, "birthDate", "Date de naissance")

    print()
    log_info("Test bouton de soumission sans remplissage")
    submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
    color = submit_btn.value_of_css_property("background-color")
    enabled = submit_btn.is_enabled()
    print(f"ℹ️ Couleur bouton : {color}")
    print("✅ Bouton désactivé" if not enabled else "⚠️ Bouton activé alors que formulaire vide")

    print()
    log_info("Remplissage automatique du formulaire avec données erronées")
    fill_and_tab(driver, "firstName", "Sara")
    fill_and_tab(driver, "lastName", "Bouras")
    fill_and_tab(driver, "email", "sara@@mail")
    fill_and_tab(driver, "password", "123")
    fill_and_tab(driver, "password-confirm", "1234")
    fill_and_tab(driver, "mobile", "06abc12345")
    fill_and_tab(driver, "birthDate", "01/01/2015")
    log_success("Formulaire rempli avec succès (valeurs erronées)")

    submit_btn.click()
    time.sleep(0.3)
    driver.save_screenshot("screenshot_er.png")

    print()
    log_info("Vérification des erreurs de validation")
    check_error_message(driver, "email", "email", custom_selector=".email-error-message")
    check_error_message(driver, "birthDate", "12", custom_selector=".validDate")
    check_password_error(driver)
    check_error_message(driver, "password-confirm", "password", custom_selector=".input-error-password-confirm")
    check_error_message(driver, "mobile", "phone", custom_selector=".mobile-error-message")

    print()
    log_info("Test d'inscription avec email déjà utilisé")
    fill_and_tab(driver, "email", "sara_test@example.com")
    fill_and_tab(driver, "password", "Test1234$")
    fill_and_tab(driver, "password-confirm", "Test1234$")
    fill_and_tab(driver, "mobile", "0612345678")
    fill_and_tab(driver, "birthDate", "01/01/2000")
    submit_btn.click()
    time.sleep(2)

    try:
        alert = driver.find_element(By.CLASS_NAME, "alert-danger")
        log_success(f"Message d'erreur email existant : {alert.text.strip()}")
    except:
        log_fail("Aucun message d'erreur affiché pour email déjà utilisé")

except Exception as e:
    log_fail(f"Erreur inattendue : {str(e)}")

finally:
    driver.quit()
