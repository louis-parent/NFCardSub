# -*- coding: utf-8 -*-
import sqlite3 #Module Base de Données
import nxppy #Module de la carte NFC

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
    return (listeAbonne)

def lectureCarte():
    """Fonction qui renvoie l'UID de la carte ou None si aucune carte n'est présente"""
    mifare = nxppy.Mifare()#Création d'un objet Mifare permettant la lecture NFC
    try:
        uid = mifare.select()#Détection de la carte
        return str(uid)
    except nxppy.SelectError:#Erreur levée lorque aucune carte n'est présenté
        return None

def delete():
    print("Présenter la carte à supprimer...")
    uid = None
    
    while uid == None :#Attente de présentation d'une carte
        uid = lectureCarte()

    connexion, curseur = ouvrirBaseDeDonnee()
    curseur.execute("""DELETE FROM subs WHERE uid = ?""", (uid,))
    connexion.commit()
    fermerBaseDeDonnee(connexion)
    print("Abonnée supprimé")
