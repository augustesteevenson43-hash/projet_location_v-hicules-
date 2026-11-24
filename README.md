# Application de location de véhicules

Projet Python — Sujet 2 : Location de véhicules.

## Fonctionnalités
- Gestion des voitures et motos (héritage).
- Gestion des clients.
- Réservation, départ, retour et annulation.
- Vérification des chevauchements de réservations.
- Gestion des périodes de maintenance.
- Calcul du prix et des frais de retard.
- Recherche, tri, statistiques et historique.
- Sauvegarde et chargement JSON.

## Lancer l'application
1. Installer Python 3.
2. Placer `main.py` et `donnees.json` dans le même dossier.
3. Ouvrir un terminal dans ce dossier.
4. Exécuter : `python main.py`

## Règles de gestion
- Les périodes utilisent le format AAAA-MM-JJ.
- La date de fin est exclusive : du 2026-12-01 au 2026-12-03 correspond à 2 jours.
- Les réservations actives ne peuvent pas se chevaucher pour un même véhicule.
- Une location peut démarrer uniquement pendant la période réservée.
- Seule une réservation non démarrée peut être annulée.
- Les frais de retard sont fixés à 25 % du tarif journalier par jour de retard. Cette règle est une hypothèse de projet et peut être adaptée avec l'accord de l'enseignant.

## Participants
À compléter avec les noms des participants.

## Dépôt
À compléter avec le lien GitHub.
