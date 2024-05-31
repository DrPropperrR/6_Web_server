import socket
from datetime import datetime
from os.path import join, isfile
from threading import Thread

HOST = '127.0.0.1'
PORT = 80
DIRECTORY = 'base'
BUFFER_SIZE = 8192
DEFAULT_PATH = 'base.html'
ALLOWED_TYPES = ('html', 'css', 'js', 'png', 'jpg', 'mp4')
CODES = {200: 'OK', 403: 'Forbidden', 404: 'Not found'}
TYPES = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'mp4': 'video/mp4'
}
RESPONSE_PATTERN = '''HTTP/1.1 {} {}
Date: {}
Server: SelfMadeServer v0.0.1
Content-Type: {};charset=utf-8
Content-Length: {}
Connection: keep-alive

'''


def read_file(path):
    return open(path, 'rb').read()


def generate_path(request):
    path = request.split('\n')[0].split(' ')[1][1:]
    if not path:
        path = DEFAULT_PATH
    return join(DIRECTORY, path)


def get_extension(path):
    return path.split('.')[-1]


def get_code(path, extension):
    if not isfile(path):
        return 404
    elif extension not in ALLOWED_TYPES:
        return 403
    else:
        return 200


def get_date():
    return datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')


def process(request, addr):
    path = generate_path(request)
    extension = get_extension(path)
    code = get_code(path, extension)
    date = get_date()
    body = b''
    if code == 200:
        body = read_file(path)
    else:
        extension = 'html'
    response = RESPONSE_PATTERN.format(code, CODES[code], date, TYPES[extension], len(body)).encode() + body
    return response


def handle(conn: socket.socket, addr):
    with conn:
        request = conn.recv(BUFFER_SIZE).decode()
        print(request)
        if request:
            response = process(request, addr)
            conn.send(response)


def accept(sock):
    while True:
        conn, addr = sock.accept()
        print(f'Connected by {addr}')
        Thread(target=handle, args=(conn, addr)).start()


def main():
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(10)
    accept(sock)


if __name__ == '__main__':
    main()