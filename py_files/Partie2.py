import http.server, urllib.parse, sqlite3, json, random, threading, socketserver, requests, json
from datetime import datetime, timedelta


# Classe pour gérer la base de données
class DatabaseHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()


# Handler de requêtes HTTP
def createHandler(db_handler):
    class RESTHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):

            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query = urllib.parse.parse_qs(parsed_path.query)

            # Gestion des différentes Tables
            if path == "/logements":
                logements = db_handler.fetch_query("SELECT * FROM Logement")
                self._send_response(logements)

            elif path == "/factures":
                factures = db_handler.fetch_query("SELECT * FROM Facture")
                self._send_response(factures)

            elif path == "/mesures":
                mesures = db_handler.fetch_query("SELECT * FROM Mesure")
                self._send_response(mesures)

            elif path == "/factures/chart":
                factures = db_handler.fetch_query("SELECT Type_F, SUM(Montant) AS TotalMontant FROM Facture GROUP BY Type_F")
                self.send_chart_response(factures)

            elif path == "/meteo":
                self.send_meteo_previsions()

            elif path == "/adresses":
                adresses = db_handler.fetch_query("SELECT * FROM Adresse")
                self._send_response(adresses)

            elif path == "/pieces":
                pieces = db_handler.fetch_query("SELECT * FROM Piece")
                self._send_response(pieces)

            elif path == "/capteurs":
                capteurs = db_handler.fetch_query("SELECT * FROM Capteur")
                self._send_response(capteurs)

            elif path == "/types":
                types = db_handler.fetch_query("SELECT * FROM Type_T")
                self._send_response(types)

            else:
                self.send_error(404, "Ressource non trouvee \n")



        def do_POST(self):

            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            content_length = int(self.headers['Content-Length'])
            post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))

            # Gestion des différentes Tables
            if path == "/logement":
                db_handler.execute_query(
                    "INSERT INTO Logement (IdAdresse, Telephone, Adresse_IP) VALUES (?, ?, ?)",
                    (post_data['IdAdresse'][0], post_data['Telephone'][0], post_data['Adresse_IP'][0])
                )
                self._send_response({"message": "Logement ajoute \n"})

            elif path == "/facture":
                db_handler.execute_query(
                    "INSERT INTO Facture (Type_F, Date_F, Montant, Valeur_Consommee, IdLogement) VALUES (?, ?, ?, ?, ?)",
                    (
                        post_data['Type_F'][0],
                        post_data['Date_F'][0],
                        post_data['Montant'][0],
                        post_data['Valeur_Consommee'][0],
                        post_data['IdLogement'][0],
                    )
                )
                self._send_response({"message": "Facture ajoutee \n"})

            elif path == "/mesure":
                db_handler.execute_query(
                    "INSERT INTO Mesure (Valeur, Date_M, IdCapteur) VALUES (?, ?, ?)",
                    (
                        post_data['Valeur'][0],
                        post_data['Date_M'][0],
                        post_data['IdCapteur'][0],
                    )
                )
                self._send_response({"message": "Mesure ajoutee \n"})

            elif path == "/adresse":
                db_handler.execute_query(
                    "INSERT INTO Adresse (Numero, Rue, Code_Postal, Ville) VALUES (?, ?, ?, ?)",
                    (
                        post_data['Numero'][0],
                        post_data['Rue'][0],
                        post_data['Code_Postal'][0],
                        post_data['Ville'][0],
                    )
                )
                self._send_response({"message": "Adresse ajoutee \n"})

            elif path == "/piece":
                db_handler.execute_query(
                    "INSERT INTO Piece (Coordonnee_x, Coordonnee_y, Coordonnee_z, Nom, IdLogement) VALUES (?, ?, ?, ?, ?)",
                    (
                        post_data['Coordonnee_x'][0],
                        post_data['Coordonnee_y'][0],
                        post_data['Coordonnee_z'][0],
                        post_data['Nom'][0],
                        post_data['IdLogement'][0],
                    )
                )
                self._send_response({"message": "Piece ajoutee \n"})

            elif path == "/capteur":
                db_handler.execute_query(
                    "INSERT INTO Capteur (Reference_Commerciale, Port_de_Communication, Date_C, IdPiece) VALUES (?, ?, ?, ?)",
                    (
                        post_data['Reference_Commerciale'][0],
                        post_data['Port_de_Communication'][0],
                        post_data.get('Date_C', [None])[0],
                        post_data['IdPiece'][0],
                    )
                )
                self._send_response({"message": "Capteur ajoute \n"})

            elif path == "/type":
                db_handler.execute_query(
                    "INSERT INTO Type_T (Unite_de_Mesure, Plage_de_Precision, IdCapteur) VALUES (?, ?, ?)",
                    (
                        post_data['Unite_de_Mesure'][0],
                        post_data['Plage_de_Precision'][0],
                        post_data['IdCapteur'][0],
                    )
                )
                self._send_response({"message": "Type ajoute \n"})

            else:
                self.send_error(404, "Ressource non trouvee \n")


        def send_chart_response(self, factures):
            # Vérifie si des données existent
            if not factures:
                self.send_error(404, "Aucune facture trouvee dans la base de donnees \n")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            # Générer les données pour le graphique
            chart_data = [["Type de Facture", "Montant Total"]] + [[facture["Type_F"], facture["TotalMontant"]] for facture in factures]

            # Code HTML pour afficher le graphique
            html_content = f"""
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>Graphe des Factures</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                margin: 20px;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 20px;
                            }}
                            th, td {{
                                border: 1px solid #ccc;
                                padding: 10px;
                                text-align: left;
                            }}
                            th {{
                                background-color: #f4f4f4;
                            }}
                        </style>
                        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                        <script type="text/javascript">
                            google.charts.load('current', {{packages:['corechart']}});
                            google.charts.setOnLoadCallback(drawChart);

                            function drawChart() {{
                                var data = google.visualization.arrayToDataTable({json.dumps(chart_data)});
                                var options = {{
                                    title: 'Camembert des valeurs des factures',
                                    pieHole: 0.4,
                                }};
                                var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                                chart.draw(data, options);
                            }}
                        </script>
                    </head>
                    <body>
                        <h1>Repartition des montants des factures </h1>
                        <div id="piechart" style="width: 900px; height: 500px;"></div>
                    </body>
                </html>
            """

            # Envoyer la réponse HTML
            self.wfile.write(html_content.encode("utf-8"))


        def send_meteo_previsions(self):

            key = "f3bd19d3021a482c8ce102557241511"
            weather_request = requests.get(
                "http://api.weatherapi.com/v1/forecast.json",
                params={"key": key, "q": "Paris", "days": 5, "aqi": "no", "alerts": "no"}
            )
            weather_forecast = json.loads(weather_request.text)

            # Code HTML pour créer le tableau
            rows = ""
            for day in weather_forecast["forecast"]["forecastday"]:
                date = day["date"]
                avg_temp = day["day"]["avgtemp_c"]
                min_temp = day["day"]["mintemp_c"]
                max_temp = day["day"]["maxtemp_c"]
                condition = day["day"]["condition"]["text"]
                rows += f"""
                <tr>
                    <td>{date}</td>
                    <td>{avg_temp}°C</td>
                    <td>{min_temp}°C</td>
                    <td>{max_temp}°C</td>
                    <td>{condition}</td>
                </tr>
                """

            # Code HTML pour le reste
            html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Prévisions météo</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                            background-color: #f9f9f9;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }}
                        th, td {{
                            border: 1px solid #ccc;
                            padding: 10px;
                            text-align: center;
                        }}
                        th {{
                            background-color: #4CAF50;
                            color: white;
                        }}
                        tr:nth-child(even) {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <h1>Prévisions météo pour {weather_forecast["location"]["name"]}</h1>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Température Moyenne</th>
                                <th>Température Minimale</th>
                                <th>Température Maximale</th>
                                <th>Conditions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </body>
                </html>
            """

            # Envoyer la réponse HTML
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-16"))

        # Toutes les fonctions se terminent par ce code
        def _send_response(self, data):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps([dict(row) for row in data] if isinstance(data, list) else data).encode("utf-8"))

    return RESTHandler



# Serveur multithread
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


# Fonction principale
if __name__ == "__main__":
    db_handler = DatabaseHandler('logement.db')
    
    # Lancement du serveur
    server = ThreadingHTTPServer(("localhost", 8888), createHandler(db_handler))
    print("Serveur en cours d'execution sur http://localhost:8888 ... \n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Arret du serveur \n")
        server.server_close()
