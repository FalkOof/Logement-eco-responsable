-- Q2) On supprime toutes les tables dans la base de données

DROP TABLE Facture;
DROP TABLE Adresse;
DROP TABLE Logement;
DROP TABLE Piece;
DROP TABLE Capteur;
DROP TABLE Mesure;
DROP TABLE Type_T;

-- Q3) On crée toutes les bases de données


-- Cette table permet juste de bien normer une adresse
CREATE TABLE Adresse (
-- Primary key classique
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- Le numero de l'adresse
Numero INTEGER NOT NULL,
-- la rue
Rue TEXT NOT NULL,
-- le code postal
Code_Postal INT NOT NULL,
-- la ville
Ville TEXT NOT NULL
);


-- Cette table contient toutes les informations liées au logement 
CREATE TABLE Logement (
-- Primary key classique
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- l'adresse du Logement, gérée par une autre table afin de bien normer le tout
IdAdresse INTEGER,
-- Le numero de téléphone (pas obligatoire)
Telephone INTEGER,
-- L'adresse IP du logement 
Adresse_IP TEXT,
-- la date de création du champ
Date_L TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

FOREIGN KEY (IdAdresse) REFERENCES Adresse(Id)
);


-- Cette table contient toutes les factures que possède un logement
CREATE TABLE Facture (
-- Afin d'avoir une primary key permettant d'identifier les facture, on crée un champ pour cela
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- le type de la facture (eau, électricité, déchets...)
Type_F TEXT NOT NULL,
-- la date de la facture
Date_F TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
-- le montant à payer de la facture
Montant FLOAT,
-- La valeur consommée (?)
Valeur_Consommee FLOAT,
-- A quel logement appartient la facture
IdLogement INTEGER,

FOREIGN KEY (IdLogement) REFERENCES Logement(Id)
);

-- Cette table contient toutes les informations liées à une pièce
CREATE TABLE Piece (
-- Primary key classique
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- Les coordonnées de la pièce
Coordonnee_x INTEGER,
Coordonnee_y INTEGER,
Coordonnee_z INTEGER,
-- Le nom de la pièce
Nom TEXT,
-- A quel logement appartient la pièce
IdLogement INTEGER,

FOREIGN KEY (IdLogement) REFERENCES Logement(Id)
);


CREATE TABLE Capteur (
-- Primary key classique
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- La référence commerciale du capteur (il y a peut-être des normes à ce sujet donc on pourrait créer une autre table juste p
Reference_Commerciale TEXT NOT NULL,
-- Le port utilisé par le capteur pour communiquer
Port_de_Communication INTEGER NOT NULL,
-- la date de création du champ
Date_C TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
-- Dans quel piece est situé le capteur
IdPiece INTEGER,

FOREIGN KEY (IdPiece) REFERENCES Piece(Id)
);


CREATE TABLE Mesure (
-- Primary key classique
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- la valeur mesurée
Valeur INTEGER,
-- la date de création du champ
Date_M TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
-- A quel capteur est associé la mesure
IdCapteur INTEGER,

FOREIGN KEY (IdCapteur) REFERENCES Capteur(Id)
);


CREATE TABLE Type_T (
-- Primary key classique
Id INTEGER PRIMARY KEY AUTOINCREMENT,
-- l'unite de mesure
Unite_de_Mesure TEXT,
-- la plage de précision de la mesure
Plage_de_Precision FLOAT,
-- A quel capteur est associé la mesure
IdCapteur INTEGER,

FOREIGN KEY (IdCapteur) REFERENCES Capteur(Id)
);

