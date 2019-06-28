from tabulate import tabulate
from datetime import datetime
import os
import random
import string
import json
import configparser

# ------------------------------------ Default-Konfiguration ------------------------------------ #
# Allgemeine Konfigurationseinstellungen
configuration = {
    "priority": [ "low", "medium", "high" ],
    "type": ["bug", "feature", "improvement"],
    "submit_state": "open",
    "default_type": "bug",
    "default_priority": "medium",
    "workflow": {
        "open": ["working", "rejected"],
        "working": ["rejected", "testing", "resolved"],
        "testing": ["working", "resolved"],
        "resolved": ["reopen", "closed"]
    }
}

# Grundstruktur von einem Vorgang
issue_structure = {
    "id": None,
    "status": None,
    "type": None,
    "summary": None,
    "description": None,
    "priority": None,
    "created_by": None,
    "created_at": None,
    "comments": []
}

# ------------------------------------ Default-Konfiguration ------------------------------------ #

# Initialisieren von dem Datenverzeichnis
# path          Daten-Oberverzeichnis
# Liefert True zurueck wenn das Datenverzeichnis initialisiert wurde und sonst False
def initialize_bugtracker(path):
    full_path=os.path.join(path, ".mbt")

    # Existiert in dem angeben Verzeichnis bereits ein .mbt Datenordner?
    if not os.path.isdir(full_path) and not os.path.exists(full_path):
        try:
            os.mkdir(full_path)
        except PermissionError as e:
            raise PermissionError("Initialisierung fehlgeschlagen: Verzeichnis .mbt konnte nicht erstellt werden")

        try:
            with open(os.path.join(os.path.join(full_path, ".config")), 'w') as fh:
                json.dump(configuration, fh)
        except:
            raise PermissionError("Initialisierung fehlgeschlagen: Das Verzeichnis .mbt konnte nicht erstellt werden")

        print("MBT wurde erfolgreich initialisiert")
        return True
    else:
        raise ValueError("Initialisierung fehlgeschlagen: Verzeichnis .mbt existiert bereits")



# Erzeugen von einem neuen Vorgang
# summary       Titel des Vorgangs
# description   Beschreibung des Vorgangs
# type          Vorgangstyp
# path          Daten-Oberverzeichnis
# Liefert true zurueck wenn der Vorgang erfolgreich erstellt wurde und sonst False
def new_issue(summary, description, type, path):
    full_path=os.path.join(path, ".mbt")

    # Einlesen der Konfigurationsdatei (falls vorhanden)
    configuration=readConfiguration(full_path)

    # Existiert das Datenverzeichnis und ist es beschreibbar?
    if os.path.isdir(full_path) and os.access(path, os.W_OK):

        # Erzeuge solange eine Vorgang-ID bis keine Kollision im Datenverzeichnis auftritt
        while True:
            new_id = generateID(10)

            if not os.path.isfile(os.path.join(full_path, new_id)):
                break

        # Setzen der Felder
        issue_structure['id']=new_id
        issue_structure['status']=configuration['submit_state']
        issue_structure['priority']=configuration['default_priority']
        issue_structure['summary']=summary
        issue_structure['description']=description
        issue_structure['created_by']=readUserFromVCS(path)
        issue_structure['created_at']=datetime.now().strftime('%d-%m-%Y %H:%M')

        # Fallunterscheidung fuer den Vorgangstyp es wird der default_type gesetzt falls beim Aufruf kein Typ
        # uebergeben wurde
        if type==None:
            issue_structure['type'] = configuration['default_type']
        else:
            if type in configuration['type']:
                issue_structure['type'] = type
            else:
                raise ValueError("Ungueltiger Vorgangstyp, gueltige Werte sind: " + ', '.join(configuration['type']))

        # Schreiben des Vorgangs ins Dateisystem
        try:
            with open(os.path.join(full_path, new_id), 'w') as fh:
                json.dump(issue_structure, fh)
        except:
            raise PermissionError("Der Vorgang konnte nicht erstellt werden")

        print("Es wurde ein neues Ticket mit der ID: \""+new_id+"\" erstellt")
        return True
    else:
        raise ValueError("Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar")



# Anzeigen von einem vorhandenen Vorgang
# id            Vorgangs-ID
# path          Daten-Oberverzeichnis
# Liefert True zurueck wenn der Vorgang angezeigt werden konnte und sonst False
def show_issue(id, path):
    # Liste der Titel und Vorgangs-Felder
    fields=[['id', 'ID'],
            ['status', 'Status'],
            ['summary','Titel'],
            ['description', 'Beschreibung'],
            ['priority','Prioritaet'],
            ['created_by', 'Erstellt von'],
            ['created_at', 'Erstellt am']]

    issue_details = []
    full_path = os.path.join(path, ".mbt")

    # Existiert das Datenverzeichnis und ist es lesbar?
    if os.path.isdir(full_path) and os.access(path, os.R_OK):

        # Existiert der uebergebene Vorgang (Dateiname == ID) und ist er lesbar?
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.R_OK):
            try:
                with open(os.path.join(full_path, id)) as fh:
                    issue = json.load(fh)
            except PermissionError as e:
                raise PermissionError(str(e)+" Vorgang "+id+" konnte nicht gelesen werden")

            for i in fields:
                if i[0] in issue:
                    field_name = i[1]+" ("+i[0]+"): "
                    if issue[i[0]] != None:
                        issue_details.extend([[field_name, issue[i[0]]]])
                    else:
                        issue_details.extend([[field_name, "---"]])

            print(tabulate(issue_details))

            # Anzeigen der Kommentare
            for c in issue['comments']:
                print(c['user']+" hat am "+c['date']+" einen Kommentar hinzugefuegt:")
                print(c['comment'])
                print("---------------------------")

            return True
        else:
            raise PermissionError("Der Vorgang existiert nicht oder ist nicht lesbar")
    else:
        raise PermissionError("Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar")



# Bearbeiten von einem vorhandenen Vorgang
# id            Vorgangs-ID
# key           Feldname der geaendert werden soll
# value         neuer Wert fuer das Feld
# path          Daten-Oberverzeichnis
# Liefert True zurueck wenn der Vorgang erfolgreich aktualisiert werden konnte und sonst False
def edit_issue(id, key, value, path):
    # Liste der bearbeitbarer Felder
    modifiable = ['summary', 'description', 'priority' ]
    full_path = os.path.join(path, ".mbt")

    # Einlesen der Konfigurationsdatei (falls vorhanden)
    configuration=readConfiguration(full_path)

    # Falls die Prioritaet geaendert werden soll, liegt der neue Wert im gueltigen Bereich?
    if key == 'priority' and value not in configuration['priority']:
        raise ValueError("Fuer priority sind nur die Werte: "+", ".join(configuration['priority']))

    # Ist das uebergebene Feld bearbeitbar?
    if key in modifiable:

        # Existiert das Daten-Verzeichnis und ist es schreibbar?
        if os.path.isdir(full_path) and os.access(path, os.W_OK):

            # Existiert der Vorgang (Vorgangs-ID == Dateiname) und ist er sowohl les- als auch schreibbar?
            if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.W_OK) and os.access(os.path.join(full_path, id), os.R_OK):

                try:
                    with open(os.path.join(full_path, id)) as fh:
                        issue = json.load(fh)
                except PermissionError as e:
                    raise PermissionError("Vorgang " + id + " konnte nicht gelesen werden")

                issue[key]=value

                try:
                    with open(os.path.join(full_path, id), 'w') as fh:
                        json.dump(issue, fh)
                except PermissionError as e:
                    raise PermissionError("Vorgang " + id + " konnte nicht geschrieben werden")

                print("Vorgang "+id+" wurde erfolgreich aktualisiert")
                return True
            else:
                raise PermissionError("Der Vorgang existiert nicht oder ist nicht lesbar")
        else:
            raise PermissionError("Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar")
    else:
        raise ValueError("Es sind nur folgende Felder bearbeitbar: "+', '.join(modifiable))



# Auflisten aller Vorgaenge
# path          Daten-Oberverzeichnis
# Liefert True zurueck wenn die Vorgaenge aufgelistet werden konnten und sonst False
def list_issue(path):
    full_path = os.path.join(path, ".mbt")
    issues_list = []

    # Existiert das Daten-Verzeichnis und ist es lesbar?
    if os.path.isdir(full_path) and os.access(path, os.R_OK):
        for f in os.listdir(full_path):
            try:
                with open(os.path.join(full_path, f)) as fh:
                     issue = json.load(fh)
            except:
                continue

            if len(issue['summary']) > 20:
                summary = issue['summary'][:17]+"..."
            else:
                summary = issue['summary']

            issues_list.extend([[issue['id'], summary, issue['type'], issue['status']]])

        print(tabulate(issues_list, headers=['ID', 'Titel', 'Type', 'Status']))
        return True

    else:
        raise PermissionError("Ticket-Verzeichnis ist nicht lesbar")



# Aendern von dem Status eines Vorgangs
# id            Vorgangs-ID
# status        Neuer Status des Vorgangs
# path          Daten-Oberverzeichnis
# Liefert True zurueck wenn die geforderte Transition erfolgreich durchgefuehrt werden konnte, sonst False
def status_issue(id, status, path):
    full_path = os.path.join(path, ".mbt")

    # Existiert das Daten-Oberverzeichnis und ist es beschreibbar?
    if os.path.isdir(full_path) and os.access(path, os.W_OK):

        # Existiert der Vorgang (Vorgangs-ID == Datename) und ist die Datei les- und schreibbar?
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.W_OK) and os.access(os.path.join(full_path, id), os.R_OK):

            try:
                with open(os.path.join(full_path, id)) as fh:
                    issue = json.load(fh)
            except:
                raise PermissionError("Der Vorgang konnte nicht gelesen werden")

            # hat der Vorgang einen gueltigen Status
            if issue['status'] in configuration['workflow']:

                # Existiert eine Transition in den uebergebenen Status?
                if status in configuration['workflow'][issue['status']]:
                    issue['status']=status

                    try:
                        with open(os.path.join(full_path, id), 'w') as fh:
                            json.dump(issue, fh)
                    except:
                        raise PermissionError("Der Vorgang konnte nicht aktualisiert werden")

                    print("Vorgang wurde erfolgreich aktualisiert")
                    return True
                else:
                    raise ValueError("Ungueltiger Zielzustand, erlaubt sind nur: "+', '.join(configuration['workflow'][issue['status']]))
            else:
                raise ValueError("Der Vorgang hat einen ungueltigen Zustand")

        else:
            raise PermissionError("Der Vorgang existiert nicht oder ist nicht lesbar")
    else:
        raise PermissionError("Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar")


# Fuegt einen Kommentar zu einem Vorgang hinzu
# id            ID des Vorgangs
# user          Benutzer der den Vorgang kommentiert
# comment       Text des (neuen) Kommentars
# path          Daten-Oberverzeichnis
# Die Methode liefert True,wenn der Kommentar erfolgreich zum Vorgang hinzugefuegt wurde und sonst False
def addComments(id, user, comment, path):
    single_comment = { "user": None, "date": None, "comment": None }

    full_path = os.path.join(path, ".mbt")

    # Existiert das Datenverzeichnis und ist es lesbar?
    if os.path.isdir(full_path) and os.access(path, os.R_OK):

        # Existiert der uebergebene Vorgang (Dateiname == ID) und ist er lesbar?
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.R_OK):
            try:
                with open(os.path.join(full_path, id)) as fh:
                    issue = json.load(fh)
            except:
                raise PermissionError(str(e)+" Vorgang "+id+" konnte nicht gelesen werden")

            single_comment['user'] = user
            single_comment['date'] = datetime.now().strftime('%d-%m-%Y %H:%M')
            single_comment['comment'] = comment

            issue['comments'].append(single_comment)

            try:
                with open(os.path.join(full_path, id), 'w') as fh:
                    json.dump(issue, fh)
            except:
                raise PermissionError("Der Kommentar konnte nicht hinzugefuegt werden")

        else:
            raise PermissionError("Der Vorgang konnte nicht gelesen werden")
    else:
        raise PermissionError("Das Datenverzeichnis konnte nicht gelesen werden")

    return True



# Erzeugen von einem zufaelligen String
# n             Laenge des Strings der erzeugt werden soll
def generateID(n):
    return ''.join([random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for i in range(n)])



# Liest die Konfigurationsdatei aus dem Datenverzeichnis
# path          absoluter Pfad zum Datenverzeichnis
# Liefert die Konfiguration (als JSON) aus dem Datenverzeichnis oder die Default-Konfiugration zurueck
def readConfiguration(path):
    if os.path.isfile(os.path.join(path, ".config")) and os.access(os.path.join(path, ".config"), os.R_OK):
        try:
            with open(os.path.join(path, ".config")) as fh:
                config = json.load(fh)
        except OSError as e:
            config=configuration
    else:
        config=configuration

    return config



# Versucht den Benutzer aus der Konfiguration desVersionsmanagementsystems zu lesen
# path          Ober-Verzeichnis des Datenverzeichnisses
# Liefert den Benutzername aus der git-Konfiguration oder "anonym" zurueck
def readUserFromVCS(path):
    user="anonym"

    # Versucht den Benutzer aus git zu lesen
    if os.path.isdir(os.path.join(path, ".git")) and os.access(path, os.R_OK):
        full_path = os.path.join(path, ".git")
        if os.path.isfile(os.path.join(full_path, "config")) and os.access(os.path.join(full_path, "config"), os.R_OK):
            try:
                config = configparser.ConfigParser()
                config.read(os.path.join(full_path, "config"))
            except:
                return user

            if 'user' in config and 'name' in config['user']:
                return config['user']['name']


    return user

