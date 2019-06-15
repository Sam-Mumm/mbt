from tabulate import tabulate
import os
import random
import string
import json

issue_structure = {
    "id": None,
    "status": "open",
    "summary": None,
    "description": None,
    "priority": "medium",
    "created_by": None,
    "created_at": None
}

def initialize_bugtracker(path):
    if not os.path.isdir(os.path.join(path, ".mbt")) and not os.path.exists(os.path.join(path, ".mbt")):
        try:
            os.mkdir(os.path.join(path, ".mbt"))
        except OSError as e:
            print(str(e)+"Verzeichnis .mbt konnte nicht erstellt werden")
    else:
        print("Initialisierung fehlgeschlagen: Verzeichnis .mbt existiert bereits")

def new_issue(summary, description, path):
    full_path=os.path.join(path, ".mbt")
    if os.path.isdir(full_path) and os.access(path, os.W_OK):

        while True:
            new_id = generateID(10)

            if not os.path.isfile(os.path.join(full_path, new_id)):
                break

        issue_structure['id']=new_id
        issue_structure['summary']=summary

        with open(os.path.join(full_path, new_id), 'w') as fh:
            json.dump(issue_structure, fh)

        print("Es wurde ein neues Ticket mit der ID: \""+new_id+"\" erstellt")
    else:
        print("Das Verzeichnis "+path+" existiert nicht oder ist nicht schreibbar")

def show_issue(id, path):
    fields=[['id', 'ID:'],
            ['status', 'Status:'],
            ['summary','Titel:'],
            ['description', 'Beschreibung:'],
            ['priority','Prioritaet:'],
            ['created_by', 'Erstellt von:'],
            ['created_at', 'Erstellt am:']]

    issue_details = []
    full_path = os.path.join(path, ".mbt")
    if os.path.isdir(full_path) and os.access(path, os.W_OK):
        if os.path.isfile(os.path.join(full_path, id)) and os.access(os.path.join(full_path, id), os.R_OK):
            with open(os.path.join(full_path, id)) as fh:
                issue = json.load(fh)

            for i in fields:
                if i[0] in issue:
                    if issue[i[0]] != None:
                        issue_details.extend([[i[1], issue[i[0]]]])
                    else:
                        issue_details.extend([[i[1], "---"]])

            print(tabulate(issue_details))
        else:
            print("Der Vorgang existiert nicht oder ist nicht lesbar")
    else:
        print("Das Verzeichnis " + path + " existiert nicht oder ist nicht schreibbar")


def list_issue(path):
    print("list issues")

def close_issue(id, solution):
    print("close issue")

def generateID(n):
    return ''.join([random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for i in range(n)])
