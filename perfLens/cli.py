import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from perfLens import __version__
from perfLens.core import gather, get_parsers, select
from perfLens.parsers import PARSERS
from perfLens.utils import logger, setup_logging


def build_arg_parser() -> argparse.ArgumentParser:
    modes = "\n".join(f"  {name:<9} {p.__doc__.splitlines()[0]}"
                      for name, p in PARSERS.items())
    parser = argparse.ArgumentParser(
        prog="perfLens",
        description="Gather performance metrics from rundirs.",
        epilog=f"modes:\n{modes}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("mode", choices=list(PARSERS), help="parser to use")
    parser.add_argument("inputs", nargs="+", metavar="input",
                        help="rundir(s), or root folder(s) with --explore")
    parser.add_argument("-e", "--explore", action="store_true",
                        help="search the inputs recursively for rundirs")
    parser.add_argument("-l", "--list", action="store_true",
                        help="list the rundirs found and their available results")
    parser.add_argument("-s", "--show", nargs="+", metavar="KEY",
                        help="results to show (default: all)")
    parser.add_argument("-c", "--cols", nargs="+", metavar="COL",
                        help="columns to show")
    parser.add_argument("--sort", nargs="+", metavar="COL",
                        help="sort the rows by these columns")
    parser.add_argument("--desc", action="store_true",
                        help="sort in descending order")
    parser.add_argument("-o", "--save", metavar="DIR",
                        help="also save each result to DIR/<key>.csv")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="only print warnings and errors")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="print debug messages")
    parser.add_argument("-V", "--version", action="version",
                        version=f"perfLens {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    setup_logging(logging.DEBUG if args.debug else
                  logging.WARNING if args.quiet else logging.INFO)

    parsers = get_parsers(args.mode, args.inputs, args.explore)
    if not parsers:
        logger.error("No rundirs found for mode '%s'", args.mode)
        return 1

    if args.list:
        for p in parsers:
            print(f"{p.rundir}: {', '.join(p.available()) or '-'}")
        return 0

    tables = gather(parsers)
    for key in args.show or list(tables):
        if key not in tables:
            logger.warning("No '%s' results, available: %s",
                           key, ", ".join(tables) or "-")
            continue
        df = select(tables[key], args.cols, args.sort, args.desc)
        print(f"# {key}")
        print(df.to_string(index=False))
        if args.save:
            out = Path(args.save) / f"{key}.csv"
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(str(out), index=False)
            logger.info("Saved %s", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
