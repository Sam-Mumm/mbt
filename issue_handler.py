from tabulate import tabulate
from datetime import datetime
import os
import random
import string
import json

# ------------------------------------ Konfiguration ------------------------------------ #

configuration = {
    "priority": [ "low", "medium", "high" ],
    "type": ["bug", "feature", "improvement"],
    "default_type": "bug",
    "workflow": {
        "open": ["working", "rejected"],
        "working": ["rejected", "testing", "resolved"],
        "testing": ["working", "resolved"],
    }
}

issue_structure = {
    "id": None,
    "status": "open",
    "type": None,
    "summary": None,
    "description": None,
    "priority": "medium",
    "created_by": None,
    "created_at": None
}

# ------------------------------------ Konfiguration ------------------------------------ #

def initialize_bugtracker(path):
    if not os.path.isdir(os.path.join(path, ".mbt")) and not os.path.exists(os.path.join(path, ".mbt")):
        try:
            os.mkdir(os.path.join(path, ".mbt"))
        except OSError as e:
            return {'rc': 1, 'msg': str(e)+"Verzeichnis .mbt konnte nicht erstellt werden" }

        return {'rc': 0, 'msg': "MBT wurde erfolgreich initialisiert" }
    else:
        return { 'rc': 1, 'msg': "Initialisierung fehlgeschlagen: Verzeichnis .mbt existiert bereits" }

def new_issue(summary, description, type, path):
    full_path=os.path.join(path, ".mbt")
    if os.path.isdir(full_path) and os.access(path, os.W_OK):

        while True:
            new_id = generateID(10)

            if not os.path.isfile(os.path.join(full_path, new_id)):
                break

        issue_structure['id']=new_id
        issue_structure['summary']=summary
        issue_structure['description']=description
        issue_structure['created_at']=datetime.now().strftime('%d-%m-%Y %H:%M')

        if type==None:
            issue_structure['type'] = configuration['default_type']
        else:
            if type in configuration['type']:
                issue_structure['type'] = type
            else:
                return {'rc': 1, 'msg': "Ungüeltiger Vorgangstyp, gueltige Werte sind: " + ', '.join(configuration['type'])}
        with open(os.path.join(full_path, new_id), 'w') as fh:
            json.dump(issue_structure, fh)

        return { 'rc': 0, 'msg': "Es wurde ein neues Ticket mit der ID: \""+new_id+"\" erstellt" }
    else:
        return { 'rc': 1, 'msg': "Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar" }

def show_issue(id, path):
    fields=[['id', 'ID'],
            ['status', 'Status'],
            ['summary','Titel'],
            ['description', 'Beschreibung'],
            ['priority','Prioritaet'],
            ['created_by', 'Erstellt von'],
            ['created_at', 'Erstellt am']]

    issue_details = []
    full_path = os.path.join(path, ".mbt")
    if os.path.isdir(full_path) and os.access(path, os.W_OK):
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.R_OK):
            try:
                with open(os.path.join(full_path, id)) as fh:
                    issue = json.load(fh)
            except:
                return {'rc': 1, 'msg': "Vorgang "+id+" konnte nicht gelesen werden"}

            for i in fields:
                if i[0] in issue:
                    field_name = i[1]+" ("+i[0]+"): "
                    if issue[i[0]] != None:
                        issue_details.extend([[field_name, issue[i[0]]]])
                    else:
                        issue_details.extend([[field_name, "---"]])

            return { 'rc': 0, 'msg': tabulate(issue_details) }
        else:
            return { 'rc': 1, 'msg': "Der Vorgang existiert nicht oder ist nicht lesbar" }
    else:
        return { 'rc': 1, 'msg': "Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar" }

def edit_issue(id, key, value, path):
    modifiable = ['summary', 'description', 'priority' ]
    full_path = os.path.join(path, ".mbt")

    if key == 'priority' and value != 'high' and value != 'medium' and value != 'low':
        return { 'rc': 1, 'msg': "Fuer priority sind nur die Werte hight, medium, low gueltig" }

    if key in modifiable:
        if os.path.isdir(full_path) and os.access(path, os.W_OK):
            if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.W_OK) and os.access(os.path.join(full_path, id), os.R_OK):
                try:
                    with open(os.path.join(full_path, id)) as fh:
                        issue = json.load(fh)
                except:
                    return {'rc': 1, 'msg': "Vorgang " + id + " konnte nicht gelesen werden"}

                issue[key]=value

                try:
                    with open(os.path.join(full_path, new_id), 'w') as fh:
                        json.dump(issue_structure, fh)
                except:
                    return {'rc': 1, 'msg': "Vorgang " + id + " konnte nicht gelesen werden"}

                return {'rc': 0, 'msg': "Vorgang "+id+" wurde erfolgreich aktualisiert"}
            else:
                return {'rc': 1, 'msg': "Der Vorgang existiert nicht oder ist nicht lesbar"}
        else:
            return {'rc': 1, 'msg': "Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar"}
    else:
        return { 'rc': 1, 'msg': "Es sind nur folgende Felder bearbeitbar: "+', '.join(modifiable) }

def list_issue(path):
    full_path = os.path.join(path, ".mbt")
    issues_list = []


    if os.path.isdir(full_path) and os.access(path, os.R_OK):
        for f in os.listdir(full_path):
            try:
                with open(os.path.join(full_path, f)) as fh:
                     issue = json.load(fh)

                if len(issue['summary']) > 20:
                    summary = issue['summary'][:17]+"..."
                else:
                    summary = issue['summary']

                issues_list.extend([[issue['id'], summary, issue['type'], issue['status']]])

            except:
                continue

        return {'rc': 0, 'msg': tabulate(issues_list, headers=['ID', 'Titel', 'Type', 'Status'])}

    else:
        return {'rc': 1, 'msg': "Ticket-Verzeichnis ist nicht lesbar"}


def status_issue(id, status, path):
    full_path = os.path.join(path, ".mbt")

    if os.path.isdir(full_path) and os.access(path, os.W_OK):
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.W_OK) and os.access(os.path.join(full_path, id), os.R_OK):
            with open(os.path.join(full_path, id)) as fh:
                issue = json.load(fh)

            if issue['status'] in configuration['workflow']:
                if status in configuration['workflow'][issue['status']]:
                    issue['status']=status

                    try:
                        with open(os.path.join(full_path, id), 'w') as fh:
                            json.dump(issue, fh)
                    except:
                        return {'rc': 1, 'msg': "Der Vorgang konnte nicht aktualisiert werden"}

                    return {'rc': 0, 'msg': "Vorgang wurde erfolgreich aktualisiert"}

                else:
                    return {'rc': 1, 'msg': "Ungueltiger Zielzustand, erlaubt sind nur: "+', '.join(configuration['workflow'][issue['status']])}
            else:
                return {'rc': 1, 'msg': "Der Vorgang hat einen ungueltigen Zustand"}

        else:
            return {'rc': 1, 'msg': "Der Vorgang existiert nicht oder ist nicht lesbar"}
    else:
        return {'rc': 1, 'msg': "Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar"}


def generateID(n):
    return ''.join([random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for i in range(n)])
