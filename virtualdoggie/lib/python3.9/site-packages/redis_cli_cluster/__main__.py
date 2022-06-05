"""redis-cli-cluster

Usage:
  redis-pi-cluster [options] [<command>]...

Options:
  -h <hostname>      Server hostname (default: 127.0.0.1).
  -p <port>          Server port (default: 6379).

  --help             Show this screen.
  --version          Show version.
"""
import sys

import docopt

from . import __version__
from .cluster import StrictRedisCluster


def main():
    args = docopt.docopt(__doc__, help=False, version=__version__)
    if args['--help']:
        print(__doc__, file=sys.stderr)
        return

    args['-h'] = args['-h'] or '127.0.0.1'
    args['-p'] = args['-p'] or '6379'
    client = StrictRedisCluster(host=args['-h'], port=args['-p'])

    if args['<command>']:
        client.run(args['<command>'])
        return

    client.repl()


if __name__ == '__main__':
    main()
