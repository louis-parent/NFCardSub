# NFCardSub

## Description
This program is project for the ISN class. It work on Raspberry Pi with Explore-NFC module. It read NFC items to reconize a subscriber and permite him to pay his enter.

## Usage
There are three files and an example Database :
* main.py, it's the  console  version of the program, you can use:
  * detectionEntree() to start the enter detection for subscriber
  * rechargement() to reload a subscriber card
  * ajoutAbonne() to create a new subscriber
  * afficherInfos() to display the data of a subcriber card
* interface.py, it's the graphical version pf the program
* delete.py, it's a console program to delete subscriber of the database, use : delete()
