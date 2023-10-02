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

# [ ] The webserver can pass all the tests in not-free-tests.py (you only have part of this one, I reserve the right to add tests)

import os

class MyWebServer(socketserver.BaseRequestHandler):   
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        # break down resquest string
        request_str= self.data.decode('utf-8')          # decode binary
        request_lines= request_str.split('\r\n')        # split into individual lines
        request_method= request_lines[0].split()[0]     # get method
        request_path= request_lines[0].split()[1]       # get path

        # root directory
        rootDir= './www'
        file_path= os.path.join(rootDir, request_path.lstrip('/'))

        if request_method == 'GET':
            if not request_path.endswith('/') and os.path.isdir(file_path):
                # does not have / and is a directory
                slash_path= request_path + '/'
                response= f"HTTP/1.1 301 Moved Permanently\r\n Location: {slash_path}\r\n\r\n".encode()
                self.request.sendall(response) 

                new_file_path= os.path.join(rootDir, slash_path.lstrip('/'))
                self.serveDirect(new_file_path)
            
            if os.path.isdir(file_path):
                # if path leads to a directory
                self.serveDirect(file_path)

            elif os.path.isfile(file_path):
                # if path leads to just a file
                self.serveFile(file_path)

            else:
                self.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

        elif request_method== 'POST' or request_method == 'PUT' or request_method == 'DELETE':
            # for any other method ( Ex. POST, PUT, DELETE)
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
        
        else: 
                # does not have / and is a directory
                slash_path= request_path + '/'
                response= f"HTTP/1.1 301 Moved Permanently\r\n Location: {slash_path}\r\n\r\n".encode()
                self.request.sendall(response) 

                new_path= os.path.join(rootDir, slash_path.lstrip('/'))

                if os.path.isfile(new_path):
                    self.serveFile(new_path)
                elif os.path.isdir(new_path):
                    self.serveDirect(new_path)
                else:
                    self.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    

    
    # function as part of cleanned up refactory code from ChatGPT, 
    # 'which parts of the code i sent before are repeating' 2023-09-29
    def serveFile(self, file_path):
        # find content type- support mime types
        if file_path.endswith('.html'):
            content_type= 'text/html'
        elif file_path.endswith('.css'):
            content_type= 'text/css'
        else: 
            # if not html or css
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n") 

        with open(file_path, 'rb') as file:
                # read whats in the file then send response
                content = file.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode() + content
                self.request.sendall(response)  

    # function as part of cleanned up refactory code from ChatGPT, 
    # 'which parts of the code i sent before are repeating' 2023-09-29    
    def serveDirect(self, file_path):
        # go to directory's index.html
        index_path= os.path.join(file_path, 'index.html')
        if os.path.exists(index_path):
             # to serve index.html content
             self.serveFile(index_path)
        else:
            # if directory doesn't have index.html (not in this case but im paranoid)
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n") 


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
