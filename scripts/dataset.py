"""
Dataset related scripts
"""

import argparse

def scrape_uci():

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dataset related scripts")
    subparsers = parser.add_subparsers(help="available sub-command")

    # parsing UCI dataset repo
    parser_uci = subparsers.add_parser('parse_uci', help="parse UCI ML repo webpage")
    parser_uci.add_argument('input', help="path to input webpage")
    parser_uci.set_defaults(func=scrape_uci)

    args = parser.parse_args()
    args.func()