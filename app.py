
import os
os.environ["PYTHONUTF8"] = "1"
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import send_from_directory
import sqlite3
import subprocess
import os
from datetime import datetime
from flask import jsonify
import json
from flask import make_response, render_template
from weasyprint import HTML
from flask import send_file
from openpyxl import Workbook
import io

app = Flask(__name__)
app.secret_key = 'secretkey'  # Obligatoire pour les sessions





# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Page principale : login + signup
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/download_report_excel')
def download_report_excel():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, script_name, browser, status, date, stdout, stderr FROM test_results ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Rapports Tests"

    # Écrire l'entête
    ws.append(["ID", "Script", "Navigateur", "Statut", "Date", "Sortie", "Erreurs"])

    # Écrire les données
    for row in rows:
        ws.append(row)

    # Sauvegarder dans un buffer mémoire (pas sur disque)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output,
                     download_name="rapport_tests.xlsx",
                     as_attachment=True,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


#Route pour le Dashboard
@app.route('/dashboard_dev', methods=['GET', 'POST'])
def dashboard_dev():
    output = ""
    error = ""

    if request.method == 'POST':
        action = request.form.get('action')
        print(f"Action reçue : {action}")

        if action == 'save_script':
            script_name = request.form.get('scriptName')
            script_content = request.form.get('scriptContent')
            if script_name and script_content:
                with open(f'scripts/{script_name}.py', 'w', encoding='utf-8') as f:
                    f.write(script_content)
                output = f"Script '{script_name}' sauvegardé avec succès."
            else:
                error = "Nom ou contenu du script manquant."

        elif action == 'upload_script':
            file = request.files.get('script_file')
            if file and file.filename.endswith(('.py', '.java')):
                filepath = f'scripts/{file.filename}'
                file.save(filepath)
                print(f"File saved at: {filepath}, exists: {os.path.exists(filepath)}")

                output = f"Fichier '{file.filename}' importé avec succès."
            else:
                error = "Fichier invalide ou manquant."

        else:
            error = "Action inconnue."
    # Lister tous les scripts disponibles dans le dossier /scripts
    script_files = []
    scripts_path = os.path.join(os.getcwd(), 'scripts')
    if os.path.exists(scripts_path):
        script_files = [f for f in os.listdir(scripts_path) if f.endswith('.py') or f.endswith('.java')]

    # Connexion à la base
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer les résultats
    cursor.execute("SELECT * FROM test_results ORDER BY date DESC")
    test_results = cursor.fetchall()
    conn.close()

    return render_template("dashboard_dev.html", output=output, error=error, script_files=script_files, test_results=test_results)


# Route pour s'inscrire
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']  # Tu dois ajouter un champ "role" dans le formulaire signup

    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
        conn.commit()
        return redirect(url_for('index'))
    except sqlite3.IntegrityError:
        return "❌ Email déjà utilisé."
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard_dev'))
        else:
            flash("❌ Email ou mot de passe incorrect.")
            return render_template("login.html")

    # Handle GET request → just show the form
    return render_template("login.html")



@app.route('/download_script/<filename>')
def download_script(filename):
    scripts_dir = os.path.join(os.getcwd(), 'scripts')
    return send_from_directory(directory=scripts_dir, path=filename, as_attachment=True)

SCRIPT_FOLDER = os.path.join(os.getcwd(), "scripts")

from datetime import datetime
import sqlite3

@app.route('/run_test', methods=['POST'])
def run_test():
    test_script = request.form.get("testScript")
    browser = request.form.get("browser")
    environment = request.form.get("environment")

    if not test_script or not browser or not environment:
        return "Tous les champs sont requis", 400

    script_path = os.path.join(SCRIPT_FOLDER, test_script)

    try:
        python_path = r"C:\Users\PC MAROC\AppData\Local\Programs\Python\Python39\python.exe"
        result = subprocess.run(
            [python_path, script_path, browser, environment],
            capture_output=True,
            text=True
        )

        output = result.stdout
        errors = result.stderr

        # ➕ Déterminer le statut
        if result.returncode == 0:
            status = "Réussi"
        else:
            status = "Échoué"

        # ➕ Insérer dans la base
        conn = sqlite3.connect("database.db")  # remplace "ta_base.db" par le vrai nom
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_results (script_name, browser, status, date, stdout, stderr)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_script,
            browser,
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            output,
            errors
        ))
        test_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            output=output,
            errors=errors,
            script_name=test_script,
            browser=browser,
            environment=environment,
            status=status,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            test_id=test_id  # on passe l'id du test ici
        )


    except Exception as e:
        return f"Erreur pendant l'exécution du test : {str(e)}", 500



def save_test_result(script_name, browser, status):
    conn = sqlite3.connect('database.db')  # ⛔ remplace par le bon nom
    cursor = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO test_results (script_name, browser, status, date)
        VALUES (?, ?, ?, ?)
    """, (script_name, browser, status, date))

    conn.commit()
    print("✅ Insertion réussie dans test_results")
    conn.close()
@app.route('/view_result_detail', methods=['POST'])
def view_result_detail():
    script_name = request.form['script_name']
    date = request.form['date']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # 🔍 Récupère toutes les colonnes utiles du test
    c.execute("""
        SELECT script_name, browser, status, date, stdout, stderr
        FROM test_results
        WHERE script_name = ? AND date = ?
    """, (script_name, date))
    result = c.fetchone()
    conn.close()

    if result:
        script_name, browser, status, date, output, errors = result

        return render_template(
            "result.html",
            script_name=script_name,
            browser=browser,
            status=status,
            date=date,
            output=output,
            errors=errors,
            environment="Environnement inconnu"  # Si tu ne l’as pas encore stocké dans la base
        )
    else:
        return "Résultat non trouvé", 404


@app.route('/generate_pdf/<int:test_id>')
def generate_pdf(test_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT script_name, browser, status, date, stdout, stderr FROM test_results WHERE id=?", (test_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Rapport non trouvé", 404

    data = {
        'script_name': row[0],
        'browser': row[1],
        'status': row[2],
        'date': row[3],
        'output': row[4],
        'errors': row[5],
        'environment': 'Environnement inconnu'  # ou tu peux aussi sauvegarder l'environnement dans ta base et récupérer ici
    }

    html = render_template('result_pdf.html', **data)
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=rapport_test_{test_id}.pdf'

    return response


@app.route('/get_test_results')
def get_test_results():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM test_results")
    total = cursor.fetchone()[0]

    # Get paginated results
    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT id, script_name, browser, status, date 
        FROM test_results 
        ORDER BY date DESC 
        LIMIT ? OFFSET ?
    """, (per_page, offset))

    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row['id'],
            'script_name': row['script_name'],
            'browser': row['browser'],
            'status': row['status'],
            'date': row['date']
        })

    conn.close()

    return jsonify({
        'results': results,
        'total': total,
        'page': page,
        'per_page': per_page
    })


@app.route('/get_scripts')
def get_scripts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    scripts_path = os.path.join(os.getcwd(), 'scripts')
    script_files = []
    if os.path.exists(scripts_path):
        script_files = sorted([f for f in os.listdir(scripts_path) if f.endswith(('.py', '.java'))])

    # Paginate the results
    total = len(script_files)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_scripts = script_files[start:end]

    return jsonify({
        'scripts': paginated_scripts,
        'total': total,
        'page': page,
        'per_page': per_page
    })
if __name__ == '__main__':
    app.run(debug=True)
