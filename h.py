from http.server import *
from urllib import parse
import os
import cgi
class GetHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        form = cgi.FieldStorage()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('<meta http-equiv="refresh" content=1; URL=http://127.0.0.1:8080" /><pre>'.encode('utf-8'))
        self.wfile.write(str(os.popen('echo "Last commit details:\n\n" && git show --stat && echo "\n\nFree memory:" && free && echo "\n\nCPU:"&& top -n 1 -b').read()).encode('utf-8'))

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8080), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
