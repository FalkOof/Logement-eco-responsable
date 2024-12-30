## Bibliothèques

import http.server, socketserver, os
from urllib.parse import urlparse
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict


## Commentaires sur le code :

# J'ai essayé d'utiliser un fichier appart appelé common_styles.css pour utiliser un style commun à toutes les pages html. Cependant pour unez raison que j'ignore, la ligne de commande
# <link href="common_style.css" rel="stylesheet"> ne marche pas et me donne une rreur 404. J'ai essayé de changer le lien pour "html_css_files/common_style.css" mais ça ne marche pas non
# plus. Après 2 heures passées sur l'erreur j'ai décidé d'abandonner et de juste copier le code de common_styles.css dans tous les fichiers html, et comme ça, ça marche.
# Il y a donc probablement des styles qui ne servent à rien dans chaque fichier html.


## Code

# Définir le répertoire racine pour le serveur (TP4)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(base_dir)

PORT = 4242

# Gestionnaire de requêtes HTTP
class EcoHomeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_home_page()
        elif parsed_path.path == '/conso':
            self.serve_consumption_page()
        elif parsed_path.path == '/etats':
            self.serve_sensors_page()
        elif parsed_path.path == '/eco':
            self.serve_savings_page()
        elif parsed_path.path == '/config':
            self.serve_configuration_page()
        else:
            print(" What is going on, bad link : " + parsed_path.path +"\n")
            self.send_error(404, "Page non trouvée.\n")



    # Page d'accueil vers les autres pages du site
    def send_home_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        with open('html_css_files/Accueil.html', 'r', encoding='utf-8') as file:
            html = file.read()
        self.wfile.write(html.encode('utf-8'))



    # Page 1 : Consommations
    def serve_consumption_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Connexion à la base de données
        db_path = r"C:\Users\quent\OneDrive\Documents\Travail\Ecole_inge\Internet des Objets\TP\TP4\database_files\logement.db"
        if not os.path.exists(db_path):
            self.send_error(404, "Base de données introuvable")
            return

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Récupération des données pour les graphiques
            cursor.execute("""
                SELECT Type_F, strftime('%Y-%m', Date_F) AS Month, SUM(Montant) AS Total
                FROM Facture
                GROUP BY Type_F, strftime('%Y-%m', Date_F)
            """)
            monthly_data = cursor.fetchall()

            cursor.execute("""
                SELECT Type_F, DATE(Date_F, '-' || (strftime('%w', Date_F) || ' days')) AS WeekStart, SUM(Montant) AS Total
                FROM Facture
                GROUP BY Type_F, DATE(Date_F, '-' || (strftime('%w', Date_F) || ' days'))
            """)
            weekly_data = cursor.fetchall()

            cursor.execute("""
                SELECT Type_F, DATE(Date_F) AS Day, SUM(Montant) AS Total
                FROM Facture
                GROUP BY Type_F, DATE(Date_F)
            """)
            daily_data = cursor.fetchall()

            conn.close()

            def generate_full_scale(data, date_format, step, is_weekly=False, is_monthly=False):
                if not data:
                    return []

                # Convertir les dates en objets datetime avec la bibliothèque pour que ce soit plus simple
                if is_weekly:
                    dates = [datetime.strptime(row[1], '%Y-%m-%d') for row in data]
                elif is_monthly:
                    dates = [datetime.strptime(row[1] + '-01', '%Y-%m-%d') for row in data]
                else:
                    dates = [datetime.strptime(row[1], date_format) for row in data]
                min_date, max_date = min(dates), max(dates)

                # Générer toutes les dates entre min_date et max_date (pour ne pas avoir de problèmes)
                all_dates = []
                current_date = min_date
                while current_date <= max_date:
                    if is_monthly:
                        all_dates.append(current_date.strftime('%Y-%m'))
                        next_month = current_date.month % 12 + 1
                        next_year = current_date.year + (current_date.month // 12)
                        current_date = current_date.replace(year=next_year, month=next_month, day=1)
                    else:
                        all_dates.append(current_date.strftime(date_format))
                        current_date += step
                filled_data = defaultdict(lambda: {"électricité": 0, "eau": 0, "déchets": 0})
                for row in data:
                    filled_data[row[1]][row["Type_F"]] = row["Total"]

                result = {
                    "electricity": [],
                    "water": [],
                    "waste": [],
                    "labels": all_dates
                }
                for date in all_dates:
                    result["electricity"].append(filled_data[date]["électricité"])
                    result["water"].append(filled_data[date]["eau"])
                    result["waste"].append(filled_data[date]["déchets"])

                return result

            monthly_processed = generate_full_scale(monthly_data, '%Y-%m', None, is_monthly=True)
            weekly_processed = generate_full_scale(weekly_data, '%Y-%m-%d', timedelta(days=7), is_weekly=True)
            daily_processed = generate_full_scale(daily_data, '%Y-%m-%d', timedelta(days=1))

            with open('html_css_files/Consommation.html', 'r', encoding='utf-8') as file:
                html = file.read()

            # Ajouter les données sous forme de script dans le HTML
            data_script = f"""
            <script>
                const dataSets = {{
                    monthly: {monthly_processed},
                    weekly: {weekly_processed},
                    daily: {daily_processed}
                }};
            </script>
            """
            html = html.replace("<!-- DATA_PLACEHOLDER -->", data_script)
            self.wfile.write(html.encode('utf-8'))

        except sqlite3.Error as e:
            self.send_error(500, f"Erreur de la base de données : {str(e)}")



    # Page 2 : État des capteurs
    def serve_sensors_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Connexion à la base de données
        db_path = r"C:\Users\quent\OneDrive\Documents\Travail\Ecole_inge\Internet des Objets\TP\TP4\database_files\logement.db"
        if not os.path.exists(db_path):
            self.send_error(404, "Base de données introuvable")
            return

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Récupération des capteurs
            cursor.execute("SELECT Id, Reference_Commerciale, Port_de_Communication, Date_C FROM Capteur")
            capteurs = cursor.fetchall()
            conn.close()
            if not capteurs:
                self.wfile.write("Pas de capteurs trouvés dans la base de données.".encode('utf-8'))
                return

            # Génération des lignes HTML pour les capteurs
            rows = ""
            for capteur in capteurs:
                rows += f"""
                    <tr>
                        <td>{capteur['Id']}</td>
                        <td>{capteur['Reference_Commerciale']}</td>
                        <td>{capteur['Port_de_Communication']}</td>
                        <td>{capteur['Date_C']}</td>
                    </tr>
                """

            with open('html_css_files/Capteurs.html', 'r', encoding='utf-8') as file:
                html = file.read()
            html = html.replace("{rows}", rows)
            self.wfile.write(html.encode('utf-8'))

        except sqlite3.Error as e:
            self.send_error(500, f"Erreur de la base de données : {str(e)}")



    # page 3 : Économies réalisées
    def serve_savings_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        with open('html_css_files/Economies.html', 'r', encoding='utf-8') as file:
            html = file.read()
        self.wfile.write(html.encode('utf-8'))



    # Page 4 : Configuration
    def serve_configuration_page(self):
        """Page 4 : Configuration avec lien retour."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        with open('html_css_files/Configuration.html', 'r', encoding='utf-8') as file:
            html = file.read()
        self.wfile.write(html.encode('utf-8'))



# On lance le serveur HTTP
def start_server():
    with socketserver.TCPServer(("", PORT), EcoHomeHTTPRequestHandler) as httpd:
        print(f"Serveur démarré sur le port {PORT}. Rendez-vous sur http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            httpd.server_close()


start_server()
