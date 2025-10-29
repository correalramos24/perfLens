
from perfLens.args import parse_args
from perfLens.parserManager import ParserManager
from utils.utils_print import MyLogger
from utils.utils_py import stringfy

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

    p_manager = ParserManager(mode)

    # 1. EXPLORE BASED ON THE MODE SELECTED
    if explore:
        MyLogger.info("Exploring folder(s) @", stringfy(inputs))
        _ = [p_manager.explore(i) for i in inputs]
        MyLogger.debug("Found", stringfy(p_manager.list_paths()))
    else:
        p_manager.add_inputs(inputs)

    # 2. LIST AVAILABLE RESULTS (BASED ON THE FILES FOUND)
    if list_res:
        MyLogger.info("Listing results found...", mode)
        p_manager.list_results()
        MyLogger.success("Finishing perfLens...")
        exit(0)

    # 3. PARSE & SHOW/SAVE
    if show or save:
        p_manager.parse()
    if show:
        p_manager.show_results(show)

    if save:
        pass

if __name__ == "__main__":
    main()
