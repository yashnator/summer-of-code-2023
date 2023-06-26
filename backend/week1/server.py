from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3

class requestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path.startswith('/redirect')):
            self.send_response(302, message="Found")
            short_url = self.path.split('/')[-1]
            self.send_header("content-type", "text/plain")
            self.end_headers()
            full_url = cur.execute(f"SELECT * FROM {table_name} WHERE short_url='{short_url}'")
            self.wfile.write(f"{full_url.fetchone()}".encode(encoding='utf-8'))
            cur.execute(f"UPDATE {table_name} SET visits = visits + 1 WHERE short_url='{short_url}'")
        elif(self.path == '/'):
            self.send_response(200)
            self.send_header("content-type", 'text/plain')
            self.end_headers()
            self.wfile.write(b"Welcome to URL Shortner")
        else:
            self.send_response(400, message="Invalid request")
            self.send_header("content-type", "text/plain") 
            self.end_headers()
            
    def do_POST(self):
        self.send_response(201, message="Created")
        self.send_header("content-type", "text/plain")
        self.end_headers()
        args = self.path.split('/')
        full_url = args[-1]
        short_url = args[-2]
        cur.execute(f"""
                    INSERT OR IGNORE INTO {table_name} VALUES
                    ('{short_url}', '{full_url}', 0)
                    """)
        con.commit()
        self.wfile.write(b"Written to the database")
            
if __name__ == "__main__":
    # Connect to server
    PORT = 8080
    server_address = ('localhost', PORT)
    server = HTTPServer(server_address, requestHandler)
    print(f'Server is running on {PORT}')
    # Connect to db
    con = sqlite3.connect('shorturls.db')
    cur = con.cursor()
    table_name = 'urls'
    cur.execute(f"DROP TABLE {table_name}") 
    cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name}
                (short_url TEXT NOT NULL, 
                full_url TEXT NOT NULL UNIQUE, 
                visits INTEGER DEFAULT 0)
                """)
    print(f'Connected to db')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server closed')
        print(cur.execute(f"SELECT * FROM {table_name}").fetchall())
        exit()