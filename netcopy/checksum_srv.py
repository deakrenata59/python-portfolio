import sys
import time
import socket
import select

class CheckSumServer:
    def createServer(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (ip, port)
        server.bind(server_address)
        server.listen(5)
        return server
    
    def __init__(self, ip, port, timeout=1):
        self.server = self.createServer(ip, int(port))

        #saját adatok:
        self.starting_time = time.time()
        self.file_datas = {} #dict --> kulcs: file azon --> érték: (checksum hossz, checksum, lejárati idő, mikor lett felvéve)
        self.timeout = timeout
        self.inputs = [self.server]

    def manageInputs(self, readable):
        for socket in readable:
            if socket is self.server:
                self.joinNewClient(socket)
            else:
                self.storeOrGiveOut(socket)

    def manageExceptionalCondition(self, exceptional):
        for socket in exceptional:
            print(f'Exception occured for {socket.getpeername()}')
            self.inputs.remove(socket)
            socket.close()

    def joinNewClient(self, socket):
        connection, _ = socket.accept()
        connection.setblocking(0)
        self.inputs.append(connection)

    def storeOrGiveOut(self, socket):
        #üzenetfogadás
        message = socket.recv(1024).strip().decode()
        print(message)
        message = message.split('|')
        if message[0] == "BE": #klienstől kapott üzenetet
            #   self.file_datas[file_azon]   =    (  mp,        checksum_len,    checksum,    berakási idő)
            self.file_datas[int(message[1])] = (int(message[2]), int(message[3]), message[4], time.time())
            socket.sendall(b"OK")
            #kapcsolat bontása
            self.inputs.remove(socket)
            socket.close()
        else: # üzenet "KI" --> szerver üzent
            if (int(message[1]) in self.file_datas.keys()): #ha még el van tárolva
                answer = str(self.file_datas[int(message[1])][1]) + '|' + self.file_datas[int(message[1])][2]
                del self.file_datas[int(message[1])]
            else:
                answer = "0|"
            socket.sendall(answer.encode())
            self.inputs.remove(socket)
            socket.close()       

    def runCheckSumServer(self):
        while self.inputs:
            try:
                #ha már lejárt egy checksum adat, akkor azt kivesszük
                current_time = time.time()
                dict_copy = {}
                if self.file_datas:
                    for key, values in self.file_datas.items():
                        if current_time - values[3] < values[0]:
                            dict_copy[key] = values
                        else:
                            print("DELETED {" + str(key) + " : " + str(dict_copy[key]) + "}")
                    self.file_datas = dict_copy

                for sock in self.inputs:
                    if sock.fileno() == -1:
                        self.inputs.remove(sock)

                readable, writable, exceptional = select.select(self.inputs, [], self.inputs, self.timeout)
                
                if not (readable or writable or exceptional):
                    continue

                self.manageInputs(readable)
                self.manageExceptionalCondition(exceptional)
            except KeyboardInterrupt:
                print("\nClosing the CheckSum server.")
                #üzenet küldése klienseknek!!
                self.inputs = []
                self.server.close()
                sys.exit()

CheckSumServer = CheckSumServer(sys.argv[1], sys.argv[2])
CheckSumServer.runCheckSumServer()