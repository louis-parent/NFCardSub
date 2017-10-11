# -*- coding: utf-8 -*-
import sqlite3 #Module Base de Données
import nxppy #Module de la carte NFC
import time

PRIX_ENTREE = 2.90

def ouvrirBaseDeDonnee():
    """Fonction qui ouvre la base de donnée des abonnés"""
    connexion = sqlite3.connect('subscribers.db')#Ouverture de la base de donnée
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS subs(
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        uid TEXT,
        name TEXT,
        credits DOUBLE)
    """)#Création de la table si elle n'existe pas
    connexion.commit()#Appliquation de la requète SQL
    return (connexion, curseur)

def fermerBaseDeDonnee(connexion):
    """Fonction qui ferme la base de donnée correspondant à la connexion passée en paramètre"""
    connexion.close()

def obtenirAbonne(uid, curseur):
    curseur.execute("""SELECT id, name, credits FROM subs WHERE uid = ?""", (uid,))#Selection de la ligne de l'abonnée
    listeAbonne = curseur.fetchone()#Transformation de la ligne de la base de donnée en liste
    return listeAbonne

def lectureCarte():
    """Fonction qui renvoie l'UID de la carte ou None si aucune carte n'est présente"""
    mifare = nxppy.Mifare()#Création d'un objet Mifare permettant la lecture NFC
    try:
        uid = mifare.select()#Détection de la carte
        return str(uid)
    except nxppy.SelectError:#Erreur levée lorque aucune carte n'est présenté
        return None


def debiterEntree(uid):
    global PRIX_ENTREE#Récupération de la constante
    
    """Fonction qui vérifie si un abonnée possède assez de crédit pour une entrée et le débite"""
    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    listeAbonne = obtenirAbonne(uid, curseur)#Récupération de l'abonnée

    if listeAbonne != None:
        if listeAbonne[2] >= PRIX_ENTREE:#Si il y a assez de crédits sur la carte
            solde = listeAbonne[2] - PRIX_ENTREE
            curseur.execute("""UPDATE subs SET credits = ? WHERE uid = ?""", (solde, uid))#Mise a jour du solde dans la base de donnée
            connexion.commit()
            fermerBaseDeDonnee(connexion)
            return (0, listeAbonne[1], solde)#(code de réussite, nom, crédits)
        else :
            fermerBaseDeDonnee(connexion)
            return (1, listeAbonne[1], listeAbonne[2])#(code de réussite, nom, crédits)
    else:
        return (2, None, None)

def detectionEntree():
    """Fonction principale gérant l'entrée"""
    while True :
        uid = lectureCarte()#Récupération de l'UID de la carte
        if uid != None :
            debitInfos = debiterEntree(uid)#Débit de l'entrée
            if debitInfos[0] == 0 :#Réponse selon le code de réussite du débit
                print(str(debitInfos[1]) + " vous avez été débité d'une entrée, il vous reste " + str(debitInfos[2]) + " €.")
            elif debitInfos[0] == 1:
                print(str(debitInfos[1]) + " vous n'avez pas assez d'argent pour une entrée. Il vous reste " + str(debitInfos[2]) + " €, veuillez recharger votre carte.")
            elif debitInfos[0] == 2:
                print("Cette carte n'est associée à aucun abonnée !")
        time.sleep(1)

def rechargerCredit(uid):
    """Fonction rechargeant une carte"""
    crediter = float(raw_input("Entrez le montant à créditer : "))#Récupération du montant a créditer

    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    listeAbonne = obtenirAbonne(uid, curseur)#Récupération de l'abonnée
    if listeAbonne != None:
        solde = listeAbonne[2] + crediter#Calcul du nouveau solde

        curseur.execute("""UPDATE subs SET credits = ? WHERE uid = ?""", (solde, uid))#Mise à jour du solde dans la base de donnée
        connexion.commit()
        fermerBaseDeDonnee(connexion)

        return (0, listeAbonne[1], crediter, solde)#(Code de réusite, nom, crédits crédités, solde)
    else:
        return (1, None, None, None)
def rechargement():
    """Fonction principale pour recharger une carte"""
    print("Présenter la carte à recharger...")
    uid = None
    
    while uid == None :#Attente de présentation d'une carte
        uid = lectureCarte()

    rechargementInfo = rechargerCredit(uid)#Application du rechargement
    if rechargementInfo[0] == 0:
        print(str(rechargementInfo[1]) + " vous avez bien été crédité de " + str(rechargementInfo[2]) +  "€. Vous avez désormais " + str(rechargementInfo[3]) + "€.")
    else:
        print("Cette carte n'est associée à aucun abonnée !")
        
def insertionAbonne(uid, curseur):
    """Fonction pour ajouter un nouvel abonnée"""
    nom = raw_input("Veuillez entrer votre nom et votre prénom : ")#Saisi du nom du nouvel abonné

    curseur.execute("""INSERT INTO subs(uid, name, credits) VALUES(?, ?, ?)""", (uid, nom, 0))#Ajout de l'abonnée
    return (uid, nom)

def ajoutAbonne():
    """Fonction principale pour l'ajout d'un abonnée"""
    print("Présenter la carte du nouvel abonnée...")
    uid = None
    while uid == None :#Attente de la présentation d'une carte
        uid = lectureCarte()

    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    if obtenirAbonne(uid, curseur) == None:
        ajoutInfos = insertionAbonne(uid, curseur)#Ajout de l'abonnée
        print("Bienvenue " + str(ajoutInfos[1]) + " !")

    else:
        print("Cette carte est déja associée à un abonnée !")
    
    connexion.commit()
    fermerBaseDeDonnee(connexion)

def afficherInfos():
    """Fonction affichant les données d'un abonnée sous présentation de sa carte"""
    print("Présenter la carte...")
    uid = None
    
    while uid == None :#Attente de présentation d'une carte
        uid = lectureCarte()

    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    listeAbonne = obtenirAbonne(uid, curseur)#Récupération du abonnée
    if listeAbonne != None:
        print(str(listeAbonne[1]) + " vous avez " + str(listeAbonne[2]) + "€ sur votre carte.")
    else:
        print("Cette carte n'est associée à aucun abonnée !")
