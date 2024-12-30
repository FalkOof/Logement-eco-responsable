import sqlite3, random
from datetime import datetime, timedelta
# J'utilise la bibliothèque datetime afin d'importer des dates randoms proches de la date actuelle


# Afin de créer le Data Base file, j'utilise la commande suivante dans le répertoire contenant le fichier .sql
# sqlite3 logement.db < logement.sql


# Ouverture de la base de données
conn = sqlite3.connect('logement.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()


# Fonction pour générer une date aléatoire dans les x derniers jours
def date_aleatoire(Nombre : int):
    return datetime.now() - timedelta(days = random.randint(1, Nombre))


def initialiser_donnees():
    # Insertion d'un logement
    c.execute("INSERT INTO Logement (IdAdresse, Telephone, Adresse_IP) VALUES (1, 0743759230, '192.168.1.1')")
    print("Logement ajouté.")
    
    # Insertion d'un capteur
    c.execute("INSERT INTO Capteur (Reference_Commerciale, Port_de_Communication, IdPiece) VALUES ('Capteur1', 1, 1)")
    print("Capteur ajouté.")

initialiser_donnees()
    

# Insertion de plusieurs factures pour un logement spécifique
def inserer_factures(Nombre : int):
    
    valeurs_factures = []
    types_factures = ['eau', 'électricité', 'déchets']
    
    # Sélection d'un logement au hasard
    c.execute('SELECT Id FROM Logement')
    logements = c.fetchall()
    
    for logement in logements:
        for _ in range(Nombre):
            
            type_f = random.choice(types_factures)
            date_f = date_aleatoire(30).strftime('%Y-%m-%d %H:%M:%S')
            montant = round(random.uniform(50, 500), 2)
            valeur_consommee = round(random.uniform(10, 100), 2)
            valeurs_factures.append((type_f, date_f, montant, valeur_consommee, logement['Id']))
    
    c.executemany("INSERT INTO Facture (Type_F, Date_F, Montant, Valeur_Consommee, IdLogement) VALUES (?, ?, ?, ?, ?)", valeurs_factures)
    print(f"{len(valeurs_factures)} factures ont été insérées avec succès.")


# Insertion de plusieurs mesures pour chaque capteur
def inserer_mesures(Nombre : int):
    
    valeurs_mesures = []
    
    # Sélection de tous les capteurs
    c.execute('SELECT Id FROM Capteur')
    capteurs = c.fetchall()
    
    for capteur in capteurs:
        for _ in range(Nombre):
            
            valeur = random.randint(0, 100)
            date_m = date_aleatoire(30).strftime('%Y-%m-%d %H:%M:%S')
            valeurs_mesures.append((valeur, date_m, capteur['Id']))
    
    c.executemany("INSERT INTO Mesure (Valeur, Date_M, IdCapteur) VALUES (?, ?, ?)", valeurs_mesures)
    print(f"{len(valeurs_mesures)} mesures ont été insérées avec succès.")


# Appel des fonctions d'insertion
inserer_factures(5)
inserer_mesures(5)


# Validation des changements
conn.commit()
print("Les changements ont été enregistrés dans la base de données.")


# Fermeture de la connexion
conn.close()
