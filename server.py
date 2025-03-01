import http.server  # Importing module to create a basic HTTP server
import socketserver  # Importing module for handling server connections
import urllib.parse  # Module for parsing URL-encoded data
import json  # Module for handling JSON data
import sqlite3  # Module for interacting with SQLite database

PORT = 8000  # Defining port number for the server
DB_FILE = "bloodbankdb.db"  # Defining database file name

# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DB_FILE)  # Connect to SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    
    # Create donors table if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        blood_group TEXT,
        address TEXT
    )
    """)
    
    # Create requests table if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_name TEXT,
        blood_group TEXT
    )
    """)
    
    conn.commit()  # Save changes
    conn.close()  # Close connection

init_db()  # Initialize database

# Class to handle HTTP requests
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    
    # Method to handle POST requests
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))  # Get content length
        post_data = self.rfile.read(content_length).decode("utf-8")  # Read and decode POST data
        parsed_data = urllib.parse.parse_qs(post_data)  # Parse form data
        
        # Handling donor registration
        if self.path == "/register.html":
            name = parsed_data.get("name", [""])[0]  # Get name
            mobile = parsed_data.get("mobile", [""])[0]  # Get mobile number
            blood_group = parsed_data.get("blood_group", [""])[0]  # Get blood group
            address = parsed_data.get("address", [""])[0]  # Get address
            
            conn = sqlite3.connect(DB_FILE)  # Connect to database
            cursor = conn.cursor()
            
            # Insert donor details into database
            cursor.execute("INSERT INTO donors (name, mobile, blood_group, address) VALUES (?, ?, ?, ?)", 
                           (name, mobile, blood_group, address))
            conn.commit()  # Save changes
            conn.close()  # Close connection
            
            self.send_response(200)  # Send HTTP 200 response
            self.send_header("Content-Type", "application/json")  # Set response type
            self.send_header("Access-Control-Allow-Origin", "*")  # Allow cross-origin requests
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Registration successful!"}).encode("utf-8"))  # Send JSON response
        
        # Handling blood request
        elif self.path == "/request.html":
            requester_name = parsed_data.get("name", [""])[0]  # Get requester's name
            blood_group = parsed_data.get("blood_group", [""])[0]  # Get requested blood group
            
            conn = sqlite3.connect(DB_FILE)  # Connect to database
            cursor = conn.cursor()
            
            # Store the blood request
            cursor.execute("INSERT INTO requests (requester_name, blood_group) VALUES (?, ?)", 
                           (requester_name, blood_group))
            conn.commit()
            
            # Fetch matching donors
            cursor.execute("SELECT name, mobile, address FROM donors WHERE blood_group = ?", (blood_group,))
            donors = cursor.fetchall()
            conn.close()
            
            response = {
                "message": "Blood available ✅" if donors else "Blood not available ❌",
                "donors": [{"name": donor[0], "mobile": donor[1], "address": donor[2]} for donor in donors]
            }
            
            self.send_response(200)  # Send HTTP 200 response
            self.send_header("Content-Type", "application/json")  # Set response type
            self.send_header("Access-Control-Allow-Origin", "*")  # Allow cross-origin requests
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))  # Send JSON response

handler = RequestHandler

# Start the server
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"🚀 Server running on http://localhost:{PORT}")  # Print server start message
    httpd.serve_forever()  # Keep server running