# -*- coding: utf-8 -*-
from Tkinter import *
import sqlite3 #Module Base de Données
import nxppy #Module de la carte NFC
import time

PRIX_ENTREE = 2.90#Constante du prix de l'entrée

entryValidated = False#Booléen définissant si les saisies ont été validées

fenetre = Tk()#Fenêtre principale TKinter
valeurRechargement = DoubleVar()#Valeur numérique de la barre de saisie
valeurNomNouvelAbonne = StringVar()#Valeur saisie dans la zone de saisie

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
    connexion.commit()#Appliquation de la requête SQL
    return (connexion, curseur)

def fermerBaseDeDonnee(connexion):
    """Fonction qui ferme la base de donnée correspondant à la connexion passée en paramètre"""
    connexion.close()

def obtenirAbonne(uid, curseur):
    """Fonction qui récupére le client correspondant à l'uid donnée"""
    curseur.execute("""SELECT id, name, credits FROM subs WHERE uid = ?""", (uid,))#Selection de la ligne de l'abonné
    listeAbonne = curseur.fetchone()#Transformation de la ligne de la base de donnée en liste
    return listeAbonne

def lectureCarte():
    """Fonction qui renvoie l'UID de la carte ou None si aucune carte n'est présente"""
    mifare = nxppy.Mifare()#Création d'un objet Mifare permettant la lecture NFC
    try:
        uid = mifare.select()#Détection de la carte
        return str(uid)
    except nxppy.SelectError:#Erreur levée lorsque aucune carte n'est présentée
        return None

def effacerEcran():
    """Fonction qui remet l'ecran d'affichage à zéro pour un nouveau client"""
    entree.delete("0.0", "end")

def debiterEntree(uid):
    """Fonction qui vérifie si un abonnée possède assez de crédit pour une entrée et le débite"""
    global PRIX_ENTREE#Récupération de la constante
    
    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    listeAbonne = obtenirAbonne(uid, curseur)#Récupération de l'abonné

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
    effacerEcran()
    
    uid = None
    while uid == None:
        uid = lectureCarte()#Récupération de l'UID de la carte
    
    debitInfos = debiterEntree(uid)#Débit de l'entrée
    if debitInfos[0] == 0 :#Réponse selon le code de réussite du débit
        entree.insert('end', '\n' + str(debitInfos[1]) + " vous avez été débité d'une entrée, il vous reste " + str(debitInfos[2]) + " €.")
    elif debitInfos[0] == 1:
        entree.insert('end', '\n' + str(debitInfos[1]) + " vous n'avez pas assez d'argent pour une entrée. Il vous reste " + str(debitInfos[2]) + " €, veuillez recharger votre carte.")
    elif debitInfos[0] == 2:
        entree.insert('end', '\n' + "Cette carte n'est associée à aucun abonnée !")

def afficherInfos():
    """Fonction affichant les données d'un abonnée sous présentation de sa carte"""
    effacerEcran()
    
    uid = None
    while uid == None :#Attente de présentation d'une carte
        uid = lectureCarte()

    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    listeAbonne = obtenirAbonne(uid, curseur)#Récupération de l'abonné
    if listeAbonne != None:
        entree.insert('end', '\n' + str(listeAbonne[1]) + " vous avez " + str(listeAbonne[2]) + "€ sur votre carte.")
    else:
        entree.insert('end', '\n' + "Cette carte n'est associée à aucun abonnée !")

def rechargerCredit(uid):
    """Fonction rechargeant une carte"""
    crediter = valeurRechargement.get()#Récupération du montant à créditer

    coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
    connexion = coupleConnexionCurseur[0]
    curseur = coupleConnexionCurseur[1]

    listeAbonne = obtenirAbonne(uid, curseur)#Récupération de l'abonné
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
    global entryValidated#Récupération du booléen

    effacerEcran()
    
    if entryValidated:#Si la saisie a été validée
        uid = None
        
        while uid == None :#Attente de présentation d'une carte
            uid = lectureCarte()

        rechargementInfo = rechargerCredit(uid)#Application du rechargement
        if rechargementInfo[0] == 0:
            entree.insert('end', '\n' + str(rechargementInfo[1]) + " vous avez bien été crédité de " + str(rechargementInfo[2]) +  "€. Vous avez désormais " + str(rechargementInfo[3]) + "€.")
        else:
            entree.insert('end', '\n' + "Cette carte n'est associée à aucun abonnée !")
        entryValidated = False
    else:
        entree.insert('end', '\n' + "Valider d'abord la saisie du montant à recharger.")#Message si la saisie n'a pas été validée


def insertionAbonne(uid, curseur):
    """Fonction pour ajouter un nouvel abonnée"""
    nom = valeurNomNouvelAbonne.get()#Saisi du nom du nouvel abonné

    curseur.execute("""INSERT INTO subs(uid, name, credits) VALUES(?, ?, ?)""", (uid, nom, 0))#Ajout de l'abonné
    return (uid, nom)

def ajoutAbonne():
    """Fonction principale pour l'ajout d'un abonnée"""    
    global entryValidated#Récupération du booléen
    
    effacerEcran()
    
    if entryValidated:#Si la saisie a été validée
        uid = None
        while uid == None :#Attente de la présentation d'une carte
            uid = lectureCarte()

        coupleConnexionCurseur = ouvrirBaseDeDonnee()#Récupération de la base de donnée
        connexion = coupleConnexionCurseur[0]
        curseur = coupleConnexionCurseur[1]

        if obtenirAbonne(uid, curseur) == None:
            ajoutInfos = insertionAbonne(uid, curseur)#Ajout de l'abonné
            entree.insert('end', '\n' + "Bienvenue " + str(ajoutInfos[1]) + " !")

        else:
            entree.insert('end', '\n' + "Cette carte est déja associée à un abonnée !")
        
        connexion.commit()
        fermerBaseDeDonnee(connexion)
        entryValidated = False
    else:
        entree.insert('end', '\n' + "Valider d'abord la saisie du du nom du nouvel abonné.")#Message si la saisie n'a pas été validée

def validerSaisie():
    """Fonction qui change le boolean pour définir la validaiton de la saisie"""
    global entryValidated#Récupération du booléen
    entryValidated = True

def validerNom(evenement):
    """Fonction qui valide la saisie si entrée est appuyé sur le clavier quand l'utilisateur est dans le champ de saisie du nom"""
    global entryValidated#Récupération du booléen
    entryValidated = True
    
label = Label(fenetre, text="Gestion d'une piscine", fg="#1BB7A3")#Label titre de l'interface (parent, texte, couleur)
label.pack(side=TOP)

entree = Text(fenetre)#Editeur de texte permettant l'affichage (parent)
entree.insert('end', "Démarrage NFC...")
entree.pack(side=RIGHT)

cadre = LabelFrame(fenetre, text="Fonctionnalités", padx=10, pady=10, fg="#1BB7A3")#Cadre à titre encadrant les boutons de fonctionnalités (parent, texte, marge intérieure horizontale, marge intérieure verticale, couleur du texte)
cadre.pack(side=TOP, expand=Y)

cadreSelecteur = LabelFrame(fenetre, text="Saisies", padx=5, pady=5, fg="#1BB7A3")#Cadre a titre encadrant les saisies (parent, texte, marge intérieur horizontale, marge intérieure verticale, couleur du texte)
cadreSelecteur.pack(side=BOTTOM, expand=Y)

boutonEntree = Button(cadre, text="Entrée abonné", command=detectionEntree)#Bouton pour déclencher l'entrée (parent, texte, fonction déclenchée)
boutonEntree.pack(fill=X)

boutonInfos = Button(cadre, text="Informations abonné", command=afficherInfos)#Bouton pour déclencher l'affichage des infos (parent, texte, fonction déclenchée)
boutonInfos.pack(fill=X)

boutonRechargement = Button(cadre, text="Recharger carte", command=rechargement)#Bouton pour déclencher le rechargement (parent, texte, fonction déclenchée)
boutonRechargement.pack(fill=X)

boutonNouvelAbonne = Button(cadre, text="Ajout abonné", command=ajoutAbonne)#Bouton pour déclencher l'ajout d'un nouvel abonné (parent, texte, fonction déclenchée)
boutonNouvelAbonne.pack(fill=X)

barre = Scale(cadreSelecteur, variable=valeurRechargement, orient="horizontal", from_=0, to=100, resolution=0.5)#Barre de sélection numérique (parent, variable, orientation, minimum, maximum, pas)
barre.pack(fill=X)

entreeNom = Entry(cadreSelecteur, textvariable=valeurNomNouvelAbonne)#Zone de saisie pour le nom d'un nouvel abonné (parent, variable)
entreeNom.focus_set()#Mise en place de l'observation
entreeNom.bind("<Return>", validerNom)#Définition de l'événement "L'utilisateur clique sur Entrée" (événement, fonction déclenchée)
entreeNom.pack(fill=X, pady=2)

boutonValiderSaisie = Button(cadreSelecteur, text="Valider saisie", command=validerSaisie)#Bouton pour valider les saisies (parent, texte, fonction déclenchée)
boutonValiderSaisie.pack(fill=X)

fenetre.mainloop()#Démarrage de la fenêtre construite
