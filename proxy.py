import socket
import select
import urllib

from urllib.parse import urlparse


HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8765               # Arbitrary non-privileged port
server_address = (HOST, PORT)


class HTTPRequest:
    charset = 'utf-8'
    configs = {}

    def __init__(self, connection, request):
        self.connection = connection
        self.request = request.decode('utf-8')
        contents = self.request.split('\r\n')
        self.method, url, self.proto = contents[0].split()
        self.url = urlparse(url)
        for config in contents[1:]:
            if not config: continue
            k, v = config.split(':', maxsplit=1)
            self.configs[k] = v.strip()

    def __str__(self):
        return '''
method: {}
url: {}
Accept-Encoding: {}
'''.format(self.method, self.url, self.configs['Accept-Encoding'])


class Proxy:
    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(server_address)
        server.listen(10)
        inputs = [server]

        while True:
            readable, writable, exception = select.select(inputs, [], inputs, 20)
            if not (readable or writable or exception):
                print("Timeout")
                continue
            for s in readable:
                if s is server:
                    conn, addr = server.accept()
                    print('Connected by', addr)
                    conn.setblocking(0)
                    inputs.append(conn)
                else:
                    data = conn.recv(4096)
                    if not data:
                        conn.close()
                        inputs.remove(conn)
                        break
                    request = HTTPRequest(conn, data)
                    # print(data.decode('utf-8'))
                    # request = HTTPRequest(data)
                    # data = self.send(request)
                    # conn.sendall(data)
                    # conn.close()
            for s in exception:
                print('exception on {}'.format(s.getpeername))
                inputs.remove(s)
                s.close()

    def send(self, request):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = request.url
        port = 80
        if ';' in url:
            port = url.split(':')[1]
        # s.connect((url.netloc, port))
        s.connect(('10.74.120.140', 8000))
        msg = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(url.path, url.netloc)
        s.send(msg.encode('utf-8'))
        data = s.recv(4096)
        recv_data = data
        while len(data):
            data = s.recv(4096)
            recv_data += data
        return recv_data


if __name__ == '__main__':
    proxy = Proxy()
    proxy.server()
