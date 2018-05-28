import contextlib
import subprocess
from enum import Enum, auto


class GTP(contextlib.AbstractContextManager):
    """ Go Text Protocol connection

    """

    def __init__(self, cmd):
        self._cmd = cmd

    def open(self):
        self._p = subprocess.Popen(self._cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def close(self):
        self._p.terminate()

    def is_alive(self):
        return self._p.poll() is None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def recv_response(self, ignore_empty=True):
        response = Response(self._p.stdout.readline())
        if ignore_empty and response.type == ResponseType.EMPTY:
            return self.recv_response(ignore_empty=ignore_empty)
        return response

    def send_command(self, command):
        if not self.is_alive():
            raise GTPConnectionBrokenException()
        if not isinstance(command, Command):
            command = Command(command)
        cmd = bytes(command)
        self._p.stdin.write(cmd)
        self._p.stdin.flush()


class GTPConnectionBrokenException(Exception):
    pass


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
        self._response = response
        self._type = None
        self._content = None
        self._parse(response)

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
    cmds = ['boardsize 9', 'komi 5.5'] + ['genmove b', 'genmove w', 'final_score'] * 50
    with GTP('pachi') as gtp:
        res = [gtp.send_command(cmd) for cmd in cmds]
