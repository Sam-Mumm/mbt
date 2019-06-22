#!/usr/bin/env python
"""My Little Bugtracker

Usage:
mbt.py init [--path=<path>]
mbt.py new --summary=<summary> [--type=<type>] [--description=<description>] [--path=<path>]
mbt.py show --id=<issue-id> [--path=<path>]
mbt.py edit --id=<issue-id> --key=<field>  --value=<value> [--path=<path>]
mbt.py list [<field_1>:<value> ... <field_n>:<value>] [--path=<path>]
mbt.py state --id=<issue-id> --status=<status> [--path=<path>]
mbt.py comment --id=<issue-id> --user=<user> --comment=<comment> [--path=<path>]
mbt.py -h|--help
mbt.py -v|--version

Options:
-h --help                           Anzeigen der Hilfe
-v --version                        Anzeige der Version
--path=<path>                       Pfad zum Daten-Verzeichnis
--id=<issue-id>                     Vorgangs-ID
--summary=<summary>                 Titel des Vorgangs
--type=<type>                       Vorgangstyp (Standardmaessig: Bug)
--description=<description>         Beschreibung des Vorgangs
--status=<status>                   Zielstatus des Vorgangs
--key=<field>                       Feld des Vorgangs
--value=<value>                     Neuer Wert des Feldes
"""

from docopt import docopt
import issue_handler
import os

def main():
    arguments = docopt(__doc__, version='My Little Bugtracker 0.1')

    if arguments['--path']:
        path = arguments['--path']
    else:
        path = os.getcwd()

    # Fallunterscheidung fuer...
    # ...die initialiseren vom Bugtracker
    if arguments['init'] == True:
        return issue_handler.initialize_bugtracker(path)

    # ...die Erstellung von einem neuen Vorgang
    elif arguments['new'] == True:
        return issue_handler.new_issue(arguments['--summary'], arguments['--description'], arguments['--type'], path)

    # ... das Anzeigen einem Vorgang
    elif arguments['show'] == True:
        return issue_handler.show_issue(arguments['--id'], path)

    # ...das bearbeiten von einem Vorgang
    elif arguments['edit'] == True:
        return issue_handler.edit_issue(arguments['--id'], arguments['--key'], arguments['--value'], path)

    # ...das Auflisten der vorhandenen Vorgaenge
    elif arguments['list'] == True:
        return issue_handler.list_issue(path)

    # ...die Ausfuehrung einer Transition
    elif arguments['state'] == True:
        return issue_handler.status_issue(arguments['--id'], arguments['--status'], path)

    # ...das Hinzufuegen von einem Kommentar zu einem Vorgang
    elif arguments['comment'] == True:
        return issue_handler.addComments(arguments['--id'], arguments['--user'], arguments['--comment'], path)




if __name__ == '__main__':
    if main():
        exit(0)
    else:
        exit(1)