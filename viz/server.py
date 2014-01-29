import CGIHTTPServer
import BaseHTTPServer
class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
    cgi_directories = ["/scripts"]
PORT = 6477
httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()
