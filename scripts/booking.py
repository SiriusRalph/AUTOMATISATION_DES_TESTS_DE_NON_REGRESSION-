import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔐 Infos du compte
EMAIL = "dilogo7206@ihnpo.com"
PASSWORD = "SARAbs1234*"

# 🌐 Initialisation du navigateur
options = uc.ChromeOptions()
options.add_argument("--incognito")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

def log(msg, ok=True):
    print(f"{'✅' if ok else '❌'} {msg}")

# 💡 Nouvelle fonction pour autocomplétion correcte
def fill_city_with_autocomplete(input_id, city_code):
    try:
        input_elem = wait.until(EC.presence_of_element_located((By.ID, input_id)))
        driver.execute_script("arguments[0].scrollIntoView(true);", input_elem)
        input_elem.clear()
        input_elem.click()
        input_elem.send_keys(city_code)

        # Attente explicite que la liste s'affiche
        time.sleep(1.5)
        suggestions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.autocomplete-option")))

        if suggestions:
            suggestions[0].click()
            log(f"✅ {input_id} rempli avec : {city_code}")
        else:
            log(f"❌ Aucune suggestion trouvée pour {input_id}", ok=False)
            raise Exception("Suggestion vide")
    except Exception as e:
        log(f"❌ Erreur lors du remplissage de {input_id} : {e}", ok=False)
        raise e


try:
    # 1. Page d'accueil
    log("Ouverture de la page d'accueil")
    driver.get("https://flightpass.royalairmaroc.com/")
    print("✅ Page chargée avec succès :", driver.title)
    time.sleep(2)

    # 2. Cookies
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        cookie_btn.click()
        log("Cookies acceptés")
    except:
        log("Pas de bannière cookie", ok=True)

    # 3. Connexion
    login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".signIn")))
    login_btn.click()
    log("Bouton Se connecter cliqué")
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']").click()
    log("Formulaire de connexion soumis")

    # 4. Connexion réussie
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-name")))
    log("Connexion réussie")
    wait.until(EC.url_contains("/?lg=fr"))
    log("Redirection vers page d'accueil confirmée")

    # 5. Pause pour React
    log("Pause pour chargement des composants React...")
    time.sleep(7)

    # 6. Vérifier que le bouton Configurer est désactivé au départ
    try:
        config_btn_disabled = driver.find_element(By.XPATH, "//button[contains(text(),'Configurer')]")
        if config_btn_disabled.get_attribute("disabled"):
            log("✅ Bouton 'Configurer' désactivé quand les champs sont vides")
        else:
            log("❌ Le bouton 'Configurer' est actif alors que les champs sont vides", ok=False)
    except:
        log("❌ Bouton 'Configurer' introuvable au début", ok=False)

    # 7. Origine
    fill_city_with_autocomplete("origin-autocomplete", "CAS")

    # 8. Destination
    fill_city_with_autocomplete("destination-autocomplete", "BRU")

    # 9. Sélection Pass Standard
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".buttons-container .segment-button")))
    for btn in buttons:
        value = btn.get_attribute("value")
        if value == "NORMAL":
            if "active" in btn.get_attribute("class"):
                log("Pass Standard déjà actif")
            else:
                btn.click()
                log("Pass Standard sélectionné")
            break

    # 10. Vérifier bouton "Aperçu des Dates éligibles"
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "disablackouts")))
        log("✅ 'Aperçu des Dates éligibles' visible")
    except:
        log("❌ 'Aperçu des Dates éligibles' non détecté", ok=False)

    # 11. Sélection Pass Premium
    premium_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@value='PREMIUM']")))
    if "active" not in premium_btn.get_attribute("class"):
        premium_btn.click()
        log("✅ Pass Premium sélectionné")
    else:
        log("✅ Pass Premium déjà actif")

    # 12. Vérifier "Sans restriction de date de voyage"
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "premblackouts")))
        log("✅ 'Sans restriction de date de voyage' visible")
    except:
        log("❌ 'Sans restriction de date de voyage' non détecté", ok=False)

    # 13. Cliquer sur Configurer
    config_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Configurer')]")))
    if config_btn.get_attribute("disabled"):
        log("❌ Bouton 'Configurer' reste désactivé après remplissage", ok=False)
    else:
        config_btn.click()
        log("✅ Bouton 'Configurer' cliqué")

        # 14. Redirection
        time.sleep(3)
        if "currency" in driver.current_url or "MAD" in driver.current_url:
            log("✅ Redirection vers la page de paiement OK")
        else:
            log("❌ Redirection vers paiement non détectée", ok=False)

        try:
            # Attente que le conteneur de l'itinéraire soit présent
            itineraire_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "selectSegment")))

            # Récupérer le texte des aéroports départ et arrivée
            depart = itineraire_div.find_element(By.CLASS_NAME, "departure").text
            arrivee = itineraire_div.find_element(By.CLASS_NAME, "arrival").text

            log(f"Itinéraire affiché : départ = {depart}, arrivée = {arrivee}")

            # Vérifier que les villes attendues sont présentes (exemple ici "Casablanca" et "Milan")
            if "CMN" in depart and "BRU" in arrivee:
                log("✅ Itinéraire correctement affiché sur la page de paiement")
            else:
                log("❌ Itinéraire incorrect ou incomplet sur la page de paiement", ok=False)
        except Exception as e:
            log(f"❌ Impossible de vérifier l'itinéraire sur la page paiement : {e}", ok=False)
    try:
        # Attendre que le bouton contenant le nombre de vols soit présent
        vols_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.cust-select")))

        # Extraire le texte du span dans la structure imbriquée
        span_text = vols_btn.find_element(By.CSS_SELECTOR, "div.value span").text.strip()

        # Le texte contient probablement plusieurs lignes / valeurs, ex: "3\nAller-Retour"
        # Pour récupérer le nombre seul, on peut prendre la première ligne ou utiliser une regex
        nombre_vols = span_text.split()[0].strip('"')  # Retire les guillemets et prend le premier mot

        log(f"Nombre de vols affiché : {nombre_vols}")

        # Optionnel : vérifier que le nombre est un entier > 0
        if nombre_vols.isdigit() and int(nombre_vols) > 0:
            log("✅ Nombre de vols valide")
        else:
            log("❌ Nombre de vols invalide ou non détecté", ok=False)

    except Exception as e:
        log(f"❌ Impossible de récupérer le nombre de vols : {e}", ok=False)

    try:
        # Attendre que le bouton contenant les jours soit présent
        jours_btn = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dayToDeparture button.cust-select")))

        # Récupérer le texte dans le span
        span_text = jours_btn.find_element(By.CSS_SELECTOR, "div.value span").text.strip()

        # Extraire le nombre (extrait la première partie avant le mot "jours")
        nombre_jours = span_text.split()[0].strip('"')

        log(f"✅ Jours de réservation à l'avance affichés : {nombre_jours}")

    except Exception as e:
        log(f"❌ Impossible de récupérer les jours de réservation à l'avance : {e}", ok=False)
    try:
        # Attendre que le bouton contenant la validité soit présent
        validite_btn = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sliderDelay button.cust-select")))

        # Récupérer le texte dans le span
        span_text = validite_btn.find_element(By.CSS_SELECTOR, "div.value span").text.strip()

        # Extraire la valeur numérique (ex: "12")
        validite = span_text.split()[0].strip('"')

        log(f"Validité RAM FLIGHT PASS affichée : {validite} mois")


    except Exception as e:
        log(f"❌ Impossible de récupérer la validité RAM FLIGHT PASS : {e}", ok=False)

    try:
        # Trouver le radio bouton Standard (actif)
        standard_radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.standard span.MuiRadio-root")))
        # Cliquer dessus (normalement déjà sélectionné si class 'active')
        standard_radio.click()
        log("✅ Option Standard cliquée")

        # Trouver le radio bouton Premium
        premium_radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.standard span.MuiRadio-root")))
        premium_radio.click()
        log("✅ Option Premium cliquée")

        # Re-cliquer sur Standard si besoin (pour test)
        standard_radio.click()
        log("✅ Option Standard recliquée")
    except Exception as e:
        log(f"❌ Erreur lors de la sélection Standard/Premium : {e}", ok=False)

    try:
        # Étape 1 : localiser le bouton "Valider"
        valider_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.next")))

        # Étape 2 : scroller jusqu'au bouton
        driver.execute_script("arguments[0].scrollIntoView(true);", valider_btn)
        time.sleep(1)

        # Étape 3 : détecter s'il y a un overlay ou un élément qui bloque le clic
        overlays = driver.find_elements(By.CSS_SELECTOR, "div.value.disabled")
        if overlays:
            log(f"⚠️ Un overlay bloquant détecté : {len(overlays)} élément(s)")
            try:
                driver.execute_script("arguments[0].style.display = 'none';", overlays[0])
                log("✅ Overlay masqué temporairement")
            except Exception as e:
                log(f"❌ Échec du masquage overlay : {e}", ok=False)

        # Étape 4 : clic forcé via JavaScript
        driver.execute_script("arguments[0].click();", valider_btn)
        log("✅ Bouton 'Valider' cliqué via JavaScript")

        # Étape 5 : vérifier redirection vers la page de confirmation
        wait.until(EC.url_contains("/achat/confirmation"))
        current_url = driver.current_url

        if "https://flightpass.royalairmaroc.com/achat/confirmation" in current_url:
            log("✅ Redirection correcte vers la page de confirmation/paiement")
        else:
            log(f"❌ Redirection inattendue : {current_url}", ok=False)

    except Exception as e:
        log(f"❌ Erreur lors du clic ou de la redirection après 'Valider' : {e}", ok=False)







except Exception as e:
    log(f"❌ ❌ Erreur inattendue : {str(e)}", ok=False)
    timestamp = int(time.time())
    driver.save_screenshot(f"error_screenshot_{timestamp}.png")
    with open(f"error_dom_{timestamp}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"📸 Screenshot enregistré : error_screenshot_{timestamp}.png")
    print(f"📄 DOM snapshot enregistré : error_dom_{timestamp}.html")

finally:
    time.sleep(5)
    driver.quit()
