from perfLens.parserManager import ParserManager

from utils.utils_print import MyLogger
from utils.utils_bash import execute_command_get_ouput

from pathlib import Path
import argparse

VERSION="Alpha"

def parse_args():
    parser = argparse.ArgumentParser(
        description="perfLens - A gather performance information tool",
        usage="paramirar.py mode input [input2] [inputN]... [other flags] ",
        epilog=f"VERSION: {VERSION}"
    )

    parser.add_argument('mode', choices=ParserManager.available(),
                nargs='?', default=None, help="Select the desired analyzer")
    parser.add_argument('input', nargs="*", help="Input(s) files, rundirs, etc..")

    parser.add_argument('--explore', help="Search for running dirs", action='store_true')
    parser.add_argument('--list', help="Show available results", action='store_true')

    parser.add_argument('--show', nargs="*",help="Print the results to the CMD line")
    parser.add_argument('--cols', help="Show only a certain columns", default=None, nargs="*")
    parser.add_argument('--sort', nargs="*", help="Sort the records of show")
    parser.add_argument('--desc', help="Sort descending", action="store_false", default=True)

    parser.add_argument('--save', default=None,help="Save the results to a csv file")

    parser.add_argument('--version', help="Print paramirar version", action='store_true')
    parser.add_argument('--dev-version', help="Print perfLens info", action='store_true')

    parsed = parser.parse_args()

    if parsed.dev_version:
        pLens_home = Path(__file__).parent
        print("perfLens installed at", pLens_home)
        br = execute_command_get_ouput("git rev-parse --abbrev-ref HEAD", pLens_home)
        cm = execute_command_get_ouput("git rev-parse --short HEAD", pLens_home)
        #tg = execute_command_get_ouput("git describe --tags --abbrev=0", pLens_home)
        print(f"VERSION: {VERSION} => BRANCH: {br} @ COMMIT: {cm}")
    if parsed.version:
        print(f"VERSION: {VERSION}")
    if parsed.version or parsed.dev_version:
        exit(0);

    if not parsed.mode:
        MyLogger.error("mode is a required argument!")
        parser.print_usage()
        exit(1)

    if not parsed.input:
        MyLogger.error("input(s) is(are) a required argument(s)!")
        parser.print_usage()
        exit(1)

    return parser.parse_args()
