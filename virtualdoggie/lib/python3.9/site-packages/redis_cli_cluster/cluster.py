import sys

import rediscluster


class StrictRedisCluster(rediscluster.StrictRedisCluster):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        try:
            super().__init__(host=host, port=port, decode_responses=True)
        except rediscluster.exceptions.RedisClusterException:
            print('(error) ERR could not connect to redis at {}:{}'.format(
                host, port),
                  file=sys.stderr)
            sys.exit(1)

    def prompt(self):
        return '{}:{}> '.format(self.host, self.port)

    def repl(self):
        while True:
            try:
                data = input(self.prompt())
            except (EOFError, KeyboardInterrupt):
                print()
                return

            self.run(data.split())

    def run(self, payload):
        cmd, *args = payload
        cmd = cmd.lower()
        if cmd == 'del':
            cmd = 'delete'

        try:
            fx = getattr(self, cmd)
            if cmd == 'cluster':
                ret = fx(args[0], *args[1:])
            else:
                ret = fx(*args)

            if ret is True:
                print('OK')
            elif isinstance(ret, str):
                print('"{}"'.format(ret))
            else:
                for idx, item in enumerate(ret):
                    print('{}) "{}"'.format(idx + 1, item))
        except AttributeError:
            print("(error) ERR unknown command '{}'".format(cmd),
                  file=sys.stderr)
        except (IndexError, TypeError):
            print("(error) ERR wrong number of arguments for '{}' "
                  'command'.format(cmd), file=sys.stderr)
