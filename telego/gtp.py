import contextlib
import socket
from enum import Enum, auto


class GTP(contextlib.AbstractContextManager):
    """ Go Text Protocol connection

    """

    def __init__(self, host, port):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.settimeout(8)
        self._host = host
        self._port = port

    def connect(self):
        self._s.connect((self._host, self._port))

    def close(self):
        self._s.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def send_command(self, command):
        cmd = bytes(Command(command))
        print('send cmd:', cmd)
        self._s.send(cmd)
        # XXX assume only one command is sent.
        # XXX assume response size is not larger than 4096
        return Response(self._s.recv(4096))


class Command:
    """GTP command

    Format specific command into GTP command format.
    """

    def __init__(self, command):
        if '/n' in command:
            raise ValueError("Cannot have newline character in command")
        self._command = command

    def __str__(self):
        return "{}\n".format(self._command)

    def __bytes__(self):
        return str(self).encode('utf8')


class Response:
    """GTP command response

    """

    def __init__(self, response):
        response = response.decode('utf8')
        self._parse(response)

        self._response = response
        self._type = None
        self._content = None

    def _parse(self, response):
        if '\n' in response.strip():
            raise ValueError("Response is empty or contain mutiple responses")

        if response.startswith('?'):
            self._type = ResponseType.ERROR
        elif response.startswith('='):
            self._type = ResponseType.SUCCESS
        elif response.isspace():
            self._type = ResponseType.EMPTY
            self._content = None
            return
        else:
            raise ValueError('Unknown response type')

        try:
            self._content = response.strip().split(maxsplit=1)[1]
        except IndexError:
            self._content = ''

    @property
    def type(self):
        return self._type

    @property
    def content(self):
        return self._content

    def __repr__(self):
        return self._response


class ResponseType(Enum):
    SUCCESS = auto()
    ERROR = auto()
    EMPTY = auto()


if __name__ == '__main__':
    cmds = ['boardsize 9'] + ['genmove b', 'genmove w'] * 50
    with GTP('192.168.234.100', 4413) as gtp:
        res = [gtp.send_command(cmd) for cmd in cmds]
