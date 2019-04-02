import json
import re
import requests
import socket
from threading import Thread

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class MockServerRequestHandler(BaseHTTPRequestHandler):
    HARVEST_SRC_PATTERN = re.compile(r'/harvest_source')
    response_content = ''
    response_status_code = requests.codes.OK

    def do_GET(self):
        if re.search(self.HARVEST_SRC_PATTERN, self.path):

            self.send_response(self.response_status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            self.wfile.write(self.response_content.encode('utf-8'))


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    _, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    mock_server = HTTPServer(('localhost', port), MockServerRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()

    return mock_server


class TestMockServer(object):

    @classmethod
    def setup_class(self):
        self.mock_server_port = get_free_port()
        self.mock_server = start_mock_server(self.mock_server_port)
