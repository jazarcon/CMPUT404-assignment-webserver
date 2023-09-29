#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# TODO:
# 
# [ ] The webserver can return index.html from directories (paths that end in /)

# [ ] The webserver can pass all the tests in not-free-tests.py (you only have part of this one, I reserve the right to add tests)

# [ ] I can check out the source code via an HTTP git URL

import http.server
import http
import string
import os

class MyWebServer(socketserver.BaseRequestHandler):   
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        # break down resquest string
        request_str = self.data.decode('utf-8')         # decode binary
        request_lines = request_str.split('\r\n')       # split into individual lines
        request_method = request_lines[0].split()[0]    # get method
        request_path = request_lines[0].split()[1]      # get path


        if request_method == 'GET':
            if request_path == '/':
                # Serve index.html page
                html_content = open('./www/index.html', 'rb').read()
                response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html_content
                self.request.sendall(response)
            

            elif not request_path.endswith('/'):
                new_path= request_path + '/'
                self.request.sendall(f"HTTP/1.1 301 Moved Permenately\r\n Location:{new_path}\r\n\r\n".encode())

                print(new_path)
                print('html' not in request_path)
                if 'html' not in request_path:
                    new_content= open('www' + new_path + "index.html")
                else:
                    new_content= open('www' + new_path)

                data= new_content.read()
                self.request.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + data.encode('utf-8'))


            else:
                # Serve CSS files
                file_path = './www' + request_path
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        content = file.read()
                        content_type = 'text/css' if request_path.endswith('.css') else 'text/plain'
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode() + content
                        self.request.sendall(response)
                
                else:
                    # Return a 404 error if the file does not exist
                    self.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
            


        elif request_method == 'POST' or request_method == 'PUT' or request_method == 'DELETE':
            # Handle for other methods that cannot be handled
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")

        else:
            # Handle other request methods or return a 404 error
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")


if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C

    try:
        print("Server started at localhost:" + str(PORT))
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
