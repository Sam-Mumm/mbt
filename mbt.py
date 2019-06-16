"""My Little Bugtracker

Usage:
mbt.py init [--path=<path>]
mbt.py new --summary=<summary> [--type=<type>] [--description=<description>] [--path=<path>]
mbt.py show --id=<issue-id> [--path=<path>]
mbt.py edit --id=<issue-id> --key=<field>  --value=<value> [--path=<path>]
mbt.py list [<field_1>:<value> ... <field_n>:<value>] [--path=<path>]
mbt.py state --id=<issue-id> --status=<status> [--path=<path>]
mbt.py -h|--help
mbt.py -v|--version

Options:
-h --help  Show this screen.
-v --version  Show version.
--option1  option1
--option2  option2
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

    if arguments['init'] == True:
        rv = issue_handler.initialize_bugtracker(path)

        print(rv['msg'])

    elif arguments['new'] == True:
        rv = issue_handler.new_issue(arguments['--summary'], arguments['--description'], arguments['--type'], path)

        print(rv['msg'])

    elif arguments['show'] == True:
        rv = issue_handler.show_issue(arguments['--id'], path)

        print(rv['msg'])

    elif arguments['edit'] == True:
        rv = issue_handler.edit_issue(arguments['--id'], arguments['--key'], arguments['--value'], path)

        print(rv['msg'])

    elif arguments['list'] == True:
        rv = issue_handler.list_issue(path)

        print(rv['msg'])

    elif arguments['state'] == True:
        rv = issue_handler.status_issue(arguments['--id'], arguments['--status'], path)

        print(rv['msg'])

    return rv['rc']

if __name__ == '__main__':
    rc = main()

    exit(rc)