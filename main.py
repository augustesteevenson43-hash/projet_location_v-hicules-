import json
from datetime import date, datetime
from pathlib import Path

FICHIER = Path(__file__).with_name("donnees.json")
FORMAT_DATE = "%Y-%m-%d"


def lire_date(texte):
    """Convertit une date AAAA-MM-JJ en objet date."""
    return datetime.strptime(texte, FORMAT_DATE).date()


def demander_date(message):
    while True:
        valeur = input(message).strip()
        try:
            return lire_date(valeur)
        except ValueError:
            print("Date invalide. Utilisez le format AAAA-MM-JJ (ex. 2026-12-01).")


class Vehicule:
    def __init__(self, identifiant, marque, modele, tarif_journalier, disponible=True):
        self.identifiant = str(identifiant)
        self.marque = marque
        self.modele = modele
        self.tarif_journalier = float(tarif_journalier)
        self.disponible = bool(disponible)

    def calculer_tarif(self, nombre_jours):
        return self.tarif_journalier * nombre_jours

    def description(self):
        return f"{self.identifiant} - {self.marque} {self.modele}"

    def vers_dict(self):
        return {
            "type": self.__class__.__name__,
            "identifiant": self.identifiant,
            "marque": self.marque,
            "modele": self.modele,
            "tarif_journalier": self.tarif_journalier,
            "disponible": self.disponible
        }


class Voiture(Vehicule):
    def __init__(self, identifiant, marque, modele, tarif_journalier, nombre_places, disponible=True):
        super().__init__(identifiant, marque, modele, tarif_journalier, disponible)
        self.nombre_places = int(nombre_places)

    def description(self):
        return f"{super().description()} | Voiture | {self.nombre_places} places"

    def vers_dict(self):
        donnees = super().vers_dict()
        donnees["nombre_places"] = self.nombre_places
        return donnees


class Moto(Vehicule):
    def __init__(self, identifiant, marque, modele, tarif_journalier, cylindree, disponible=True):
        super().__init__(identifiant, marque, modele, tarif_journalier, disponible)
        self.cylindree = int(cylindree)

    def description(self):
        return f"{super().description()} | Moto | {self.cylindree} cc"

    def vers_dict(self):
        donnees = super().vers_dict()
        donnees["cylindree"] = self.cylindree
        return donnees


class Client:
    def __init__(self, identifiant, nom, telephone):
        self.identifiant = str(identifiant)
        self.nom = nom
        self.telephone = telephone

    def vers_dict(self):
        return {"identifiant": self.identifiant, "nom": self.nom, "telephone": self.telephone}


class Reservation:
    def __init__(self, identifiant, client_id, vehicule_id, debut, fin,
                 statut="reservee", date_retour=None, frais_retard=0.0):
        self.identifiant = str(identifiant)
        self.client_id = str(client_id)
        self.vehicule_id = str(vehicule_id)
        self.debut = debut
        self.fin = fin
        self.statut = statut
        self.date_retour = date_retour
        self.frais_retard = float(frais_retard)

    def nombre_jours(self):
        # La date de fin est exclusive : du 1 au 3 = 2 jours.
        return max(1, (self.fin - self.debut).days)

    def vers_dict(self):
        return {
            "identifiant": self.identifiant,
            "client_id": self.client_id,
            "vehicule_id": self.vehicule_id,
            "debut": self.debut.isoformat(),
            "fin": self.fin.isoformat(),
            "statut": self.statut,
            "date_retour": self.date_retour.isoformat() if self.date_retour else None,
            "frais_retard": self.frais_retard
        }


class Maintenance:
    def __init__(self, identifiant, vehicule_id, debut, fin, motif):
        self.identifiant = str(identifiant)
        self.vehicule_id = str(vehicule_id)
        self.debut = debut
        self.fin = fin
        self.motif = motif

    def vers_dict(self):
        return {
            "identifiant": self.identifiant,
            "vehicule_id": self.vehicule_id,
            "debut": self.debut.isoformat(),
            "fin": self.fin.isoformat(),
            "motif": self.motif
        }


class Agence:
    def __init__(self):
        self.vehicules = {}
        self.clients = {}
        self.reservations = {}
        self.maintenances = {}
        self.historique = []
        self.prochain_id = {"vehicule": 1, "client": 1, "reservation": 1, "maintenance": 1}
        self.charger()

    def enregistrer_action(self, texte):
        self.historique.append({"date_heure": datetime.now().isoformat(timespec="seconds"), "action": texte})

    def sauvegarder(self):
        donnees = {
            "vehicules": [v.vers_dict() for v in self.vehicules.values()],
            "clients": [c.vers_dict() for c in self.clients.values()],
            "reservations": [r.vers_dict() for r in self.reservations.values()],
            "maintenances": [m.vers_dict() for m in self.maintenances.values()],
            "historique": self.historique,
            "prochain_id": self.prochain_id
        }
        temporaire = FICHIER.with_suffix(".tmp")
        temporaire.write_text(json.dumps(donnees, ensure_ascii=False, indent=4), encoding="utf-8")
        temporaire.replace(FICHIER)

    def charger(self):
        if not FICHIER.exists():
            # Premier lancement : créer le fichier de démonstration.
            self.ajouter_donnees_demo()
            self.sauvegarder()
            return
        try:
            donnees = json.loads(FICHIER.read_text(encoding="utf-8"))
            vehicules = {}
            for d in donnees.get("vehicules", []):
                if d["type"] == "Voiture":
                    obj = Voiture(d["identifiant"], d["marque"], d["modele"], d["tarif_journalier"], d["nombre_places"], d.get("disponible", True))
                elif d["type"] == "Moto":
                    obj = Moto(d["identifiant"], d["marque"], d["modele"], d["tarif_journalier"], d["cylindree"], d.get("disponible", True))
                else:
                    obj = Vehicule(d["identifiant"], d["marque"], d["modele"], d["tarif_journalier"], d.get("disponible", True))
                vehicules[obj.identifiant] = obj

            clients = {}
            for d in donnees.get("clients", []):
                obj = Client(d["identifiant"], d["nom"], d["telephone"])
                clients[obj.identifiant] = obj

            reservations = {}
            for d in donnees.get("reservations", []):
                obj = Reservation(d["identifiant"], d["client_id"], d["vehicule_id"],
                                 lire_date(d["debut"]), lire_date(d["fin"]), d.get("statut", "reservee"),
                                 lire_date(d["date_retour"]) if d.get("date_retour") else None,
                                 d.get("frais_retard", 0))
                reservations[obj.identifiant] = obj

            maintenances = {}
            for d in donnees.get("maintenances", []):
                obj = Maintenance(d["identifiant"], d["vehicule_id"], lire_date(d["debut"]),
                                 lire_date(d["fin"]), d["motif"])
                maintenances[obj.identifiant] = obj

            # On remplace les données en mémoire uniquement après un chargement valide.
            self.vehicules, self.clients = vehicules, clients
            self.reservations, self.maintenances = reservations, maintenances
            self.historique = donnees.get("historique", [])
            self.prochain_id = donnees.get("prochain_id", self.prochain_id)
            self.recalculer_ids()
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as erreur:
            print(f"ATTENTION : fichier JSON invalide ({erreur}).")
            print("Le fichier original n'a pas été écrasé. Corrigez ou restaurez donnees.json.")
            self.vehicules, self.clients, self.reservations, self.maintenances = {}, {}, {}, {}
            self.historique = []

    def recalculer_ids(self):
        collections = [
            ("vehicule", self.vehicules), ("client", self.clients),
            ("reservation", self.reservations), ("maintenance", self.maintenances)
        ]
        for nom, collection in collections:
            nombres = [int(k) for k in collection if str(k).isdigit()]
            self.prochain_id[nom] = max(self.prochain_id.get(nom, 1), max(nombres, default=0) + 1)

    def ajouter_donnees_demo(self):
        v1 = Voiture("1", "Toyota", "Corolla", 50, 5)
        v2 = Voiture("2", "Hyundai", "Tucson", 75, 5)
        v3 = Moto("3", "Honda", "CB", 25, 150)
        self.vehicules = {v.identifiant: v for v in [v1, v2, v3]}
        c1 = Client("1", "Client Démo", "000-000-0000")
        self.clients = {c1.identifiant: c1}
        self.prochain_id = {"vehicule": 4, "client": 2, "reservation": 1, "maintenance": 1}

    def nouvel_id(self, categorie):
        valeur = str(self.prochain_id[categorie])
        self.prochain_id[categorie] += 1
        return valeur

    @staticmethod
    def chevauchement(debut1, fin1, debut2, fin2):
        return debut1 < fin2 and debut2 < fin1

    def vehicule_bloque(self, vehicule_id, debut, fin, ignorer_reservation=None):
        for r in self.reservations.values():
            if r.vehicule_id == vehicule_id and r.identifiant != ignorer_reservation and r.statut in ("reservee", "en_cours"):
                if self.chevauchement(debut, fin, r.debut, r.fin):
                    return f"Déjà réservé pendant la période (réservation {r.identifiant})."
        for m in self.maintenances.values():
            if m.vehicule_id == vehicule_id and self.chevauchement(debut, fin, m.debut, m.fin):
                return f"Maintenance prévue (maintenance {m.identifiant})."
        return None

    def afficher_vehicules(self):
        if not self.vehicules:
            print("Aucun véhicule.")
            return
        for v in sorted(self.vehicules.values(), key=lambda x: x.identifiant):
            print(v.description() + f" | {v.tarif_journalier:.2f} $/jour")

    def ajouter_vehicule(self):
        type_v = input("Type (1=Voiture, 2=Moto) : ").strip()
        if type_v not in ("1", "2"):
            print("Type invalide.")
            return
        marque = input("Marque : ").strip()
        modele = input("Modèle : ").strip()
        try:
            tarif = float(input("Tarif par jour ($) : "))
            if tarif <= 0:
                raise ValueError
            identifiant = self.nouvel_id("vehicule")
            if type_v == "1":
                places = int(input("Nombre de places : "))
                if places <= 0:
                    raise ValueError
                v = Voiture(identifiant, marque, modele, tarif, places)
            else:
                cc = int(input("Cylindrée (cc) : "))
                if cc <= 0:
                    raise ValueError
                v = Moto(identifiant, marque, modele, tarif, cc)
            self.vehicules[identifiant] = v
            self.enregistrer_action(f"Ajout du véhicule {identifiant}")
            self.sauvegarder()
            print("Véhicule ajouté.")
        except ValueError:
            print("Valeur numérique invalide. Aucun véhicule ajouté.")

    def ajouter_client(self):
        nom = input("Nom du client : ").strip()
        telephone = input("Téléphone : ").strip()
        if not nom or not telephone:
            print("Le nom et le téléphone sont obligatoires.")
            return
        identifiant = self.nouvel_id("client")
        self.clients[identifiant] = Client(identifiant, nom, telephone)
        self.enregistrer_action(f"Ajout du client {identifiant}")
        self.sauvegarder()
        print(f"Client ajouté avec l'identifiant {identifiant}.")

    def afficher_clients(self):
        for c in sorted(self.clients.values(), key=lambda x: x.nom.lower()):
            print(f"{c.identifiant} - {c.nom} - {c.telephone}")
        if not self.clients:
            print("Aucun client.")

    def creer_reservation(self):
        if not self.clients or not self.vehicules:
            print("Ajoutez d'abord un client et un véhicule.")
            return
        self.afficher_clients()
        client_id = input("Identifiant du client : ").strip()
        self.afficher_vehicules()
        vehicule_id = input("Identifiant du véhicule : ").strip()
        if client_id not in self.clients or vehicule_id not in self.vehicules:
            print("Client ou véhicule introuvable.")
            return
        debut = demander_date("Date de début (AAAA-MM-JJ) : ")
        fin = demander_date("Date de fin exclusive (AAAA-MM-JJ) : ")
        if fin <= debut:
            print("La date de fin doit être après la date de début.")
            return
        erreur = self.vehicule_bloque(vehicule_id, debut, fin)
        if erreur:
            print("Réservation refusée :", erreur)
            return
        identifiant = self.nouvel_id("reservation")
        r = Reservation(identifiant, client_id, vehicule_id, debut, fin)
        # Toutes les validations ont été faites avant la modification.
        self.reservations[identifiant] = r
        self.enregistrer_action(f"Création de la réservation {identifiant}")
        self.sauvegarder()
        print(f"Réservation {identifiant} créée. Estimation : {self.vehicules[vehicule_id].calculer_tarif(r.nombre_jours()):.2f} $")

    def demarrer_location(self):
        identifiant = input("Identifiant de réservation : ").strip()
        r = self.reservations.get(identifiant)
        if not r or r.statut != "reservee":
            print("Réservation inexistante ou non démarrable.")
            return
        aujourd_hui = date.today()
        if aujourd_hui < r.debut or aujourd_hui >= r.fin:
            print("Le départ doit être effectué pendant la période réservée.")
            return
        r.statut = "en_cours"
        self.enregistrer_action(f"Départ de la réservation {identifiant}")
        self.sauvegarder()
        print("Location démarrée.")

    def retourner_vehicule(self):
        identifiant = input("Identifiant de réservation : ").strip()
        r = self.reservations.get(identifiant)
        if not r or r.statut != "en_cours":
            print("Réservation inexistante ou location non démarrée.")
            return
        retour = demander_date("Date de retour réelle (AAAA-MM-JJ) : ")
        if retour < r.debut:
            print("Date de retour incohérente.")
            return
        retard = max(0, (retour - r.fin).days)
        tarif = self.vehicules[r.vehicule_id].tarif_journalier
        frais = retard * tarif * 0.25  # Règle choisie : 25 % du tarif par jour de retard.
        r.date_retour = retour
        r.frais_retard = frais
        r.statut = "retournee"
        self.enregistrer_action(f"Retour de la réservation {identifiant}; frais de retard {frais:.2f}")
        self.sauvegarder()
        print(f"Retour enregistré. Jours de retard : {retard}. Frais : {frais:.2f} $")

    def annuler_reservation(self):
        identifiant = input("Identifiant de réservation : ").strip()
        r = self.reservations.get(identifiant)
        if not r or r.statut != "reservee":
            print("Seule une réservation non démarrée peut être annulée.")
            return
        r.statut = "annulee"
        self.enregistrer_action(f"Annulation de la réservation {identifiant}")
        self.sauvegarder()
        print("Réservation annulée.")

    def ajouter_maintenance(self):
        vehicule_id = input("Identifiant du véhicule : ").strip()
        if vehicule_id not in self.vehicules:
            print("Véhicule introuvable.")
            return
        debut = demander_date("Début maintenance (AAAA-MM-JJ) : ")
        fin = demander_date("Fin maintenance exclusive (AAAA-MM-JJ) : ")
        motif = input("Motif : ").strip()
        if fin <= debut:
            print("Période invalide.")
            return
        erreur = self.vehicule_bloque(vehicule_id, debut, fin)
        if erreur:
            print("Maintenance refusée :", erreur)
            return
        identifiant = self.nouvel_id("maintenance")
        self.maintenances[identifiant] = Maintenance(identifiant, vehicule_id, debut, fin, motif)
        self.enregistrer_action(f"Maintenance {identifiant} du véhicule {vehicule_id}")
        self.sauvegarder()
        print("Maintenance enregistrée.")

    def rechercher_vehicule(self):
        terme = input("Marque, modèle ou identifiant à rechercher : ").strip().lower()
        resultats = [v for v in self.vehicules.values()
                     if terme in v.identifiant.lower() or terme in v.marque.lower() or terme in v.modele.lower()]
        for v in resultats:
            print(v.description() + f" | {v.tarif_journalier:.2f} $/jour")
        if not resultats:
            print("Aucun résultat.")

    def trier_vehicules(self):
        choix = input("Tri (1=tarif croissant, 2=marque) : ").strip()
        if choix == "1":
            liste = sorted(self.vehicules.values(), key=lambda v: v.tarif_journalier)
        elif choix == "2":
            liste = sorted(self.vehicules.values(), key=lambda v: v.marque.lower())
        else:
            print("Choix invalide.")
            return
        for v in liste:
            print(v.description() + f" | {v.tarif_journalier:.2f} $/jour")

    def afficher_reservations(self):
        for r in sorted(self.reservations.values(), key=lambda x: x.debut):
            client = self.clients.get(r.client_id)
            vehicule = self.vehicules.get(r.vehicule_id)
            print(f"#{r.identifiant} | {client.nom if client else 'Client inconnu'} | "
                  f"{vehicule.description() if vehicule else 'Véhicule inconnu'} | "
                  f"{r.debut} au {r.fin} | {r.statut}")
        if not self.reservations:
            print("Aucune réservation.")

    def statistiques(self):
        revenus = 0.0
        jours_loues = 0
        for r in self.reservations.values():
            if r.statut == "retournee":
                revenus += self.vehicules[r.vehicule_id].calculer_tarif(r.nombre_jours()) + r.frais_retard
                jours_loues += r.nombre_jours()
        retards = sum(1 for r in self.reservations.values() if r.frais_retard > 0)
        print(f"Nombre de véhicules : {len(self.vehicules)}")
        print(f"Nombre de clients : {len(self.clients)}")
        print(f"Réservations : {len(self.reservations)}")
        print(f"Locations terminées : {sum(1 for r in self.reservations.values() if r.statut == 'retournee')}")
        print(f"Revenus enregistrés : {revenus:.2f} $")
        print(f"Jours de location terminés : {jours_loues}")
        print(f"Retours en retard : {retards}")

    def afficher_historique(self):
        for action in self.historique[-30:]:
            print(f"{action.get('date_heure', '')} | {action.get('action', '')}")
        if not self.historique:
            print("Historique vide.")


def menu():
    agence = Agence()
    actions = {
        "1": ("Afficher les véhicules", agence.afficher_vehicules),
        "2": ("Ajouter un véhicule", agence.ajouter_vehicule),
        "3": ("Ajouter un client", agence.ajouter_client),
        "4": ("Afficher les clients", agence.afficher_clients),
        "5": ("Créer une réservation", agence.creer_reservation),
        "6": ("Démarrer une location", agence.demarrer_location),
        "7": ("Enregistrer un retour", agence.retourner_vehicule),
        "8": ("Annuler une réservation", agence.annuler_reservation),
        "9": ("Ajouter une maintenance", agence.ajouter_maintenance),
        "10": ("Rechercher un véhicule", agence.rechercher_vehicule),
        "11": ("Trier les véhicules", agence.trier_vehicules),
        "12": ("Afficher les réservations", agence.afficher_reservations),
        "13": ("Afficher les statistiques", agence.statistiques),
        "14": ("Afficher l'historique", agence.afficher_historique)
    }
    while True:
        print("\n========== AGENCE DE LOCATION ==========")
        for numero, (titre, _) in actions.items():
            print(f"{numero}. {titre}")
        print("0. Quitter")
        choix = input("Votre choix : ").strip()
        if choix == "0":
            agence.sauvegarder()
            print("Données sauvegardées. À bientôt !")
            break
        action = actions.get(choix)
        if action:
            try:
                action[1]()
            except (ValueError, KeyError) as erreur:
                print("Opération impossible :", erreur)
        else:
            print("Choix invalide.")


if __name__ == "__main__":
    menu()
