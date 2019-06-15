"""My Little Bugtracker

Usage:
mbt.py init [--path=<path>]
mbt.py new --summary=<summary> [--description=<description>] [--path=<path>]
mbt.py show --id=<issue-id> [--path=<path>]
mbt.py list [--path=<path>]
mbt.py close --id=<issue-id> --solution=<solution> [--path=<path>]
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
        issue_handler.initialize_bugtracker(path)

    elif arguments['new'] == True:
        issue_handler.new_issue(arguments['--summary'], arguments['--description'], path)

    elif arguments['show'] == True:
        issue_handler.show_issue(arguments['--id'], path)

    elif arguments['list'] == True:
        issue_handler.list_issue(path)

    elif arguments['status'] == True:
        issue_handler.close_issue()


if __name__ == '__main__':
    main()