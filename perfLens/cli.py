from perfLens.args import parse_args
from perfLens.parserManager import ParserManager

from utils.utils_print import MyLogger
from utils.utils_py import *

def main():
    app_args = parse_args()

    mode     : str = app_args.mode
    inputs   : list[str] = app_args.input
    list_res : bool = app_args.list
    explore  : bool = app_args.explore

    show     : None|list[str] = app_args.show
    cols     : None|list[str] = app_args.cols
    sort_res : None|list[str] = app_args.sort
    sort_desc: bool           = app_args.desc
    save     : None|list[str] = app_args.save

    if list_res:
        MyLogger.success("Listing results for", mode)
        exit(0)
    if explore:
        MyLogger.info("Exploring folder(s) at", stringfy(inputs))

        pass

    if show:
        pass

    if save:
        pass


if __name__ == "__main__":
    main()
