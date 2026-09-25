from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello from Python CI/CD Pipeline on Kubernetes!")

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    print("Python server started on port 8080")
    server.serve_forever()