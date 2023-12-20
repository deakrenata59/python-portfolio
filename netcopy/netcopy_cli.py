import hashlib
import socket
import sys

class NetCopyClient:
    def createConnection(self, srv_ip, srv_port):
        server_address = (srv_ip, srv_port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        return client

    def __init__(self, srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_azon, file_path):
        #csatlakozás a CheckSum szerverhez
        self.client_CheckSum = self.createConnection(chsum_srv_ip, int(chsum_srv_port))
        #csatlakozás a NetCopy szerverhez
        self.client_NetCopy = self.createConnection(srv_ip, int(srv_port))
        # adatok
        self.file_azon = int(file_azon)
        self.file_path = file_path
        self.timeout = 60
        self.checksum = ""
        self.checksum_len = 0

    def calculateCheckSum(self):
        with open(self.file_path, 'rb') as file:
            #cheksum adatok kinyerése
            data = file.read()
            md5 = hashlib.md5()
            md5.update(data)
            self.checksum = md5.hexdigest()
            self.checksum_len = len(md5.hexdigest())

            #adatnégyes elküldése CheckSumnak
            msg = "BE|" + str(self.file_azon) + "|" + str(self.timeout) + "|" + str(self.checksum_len) + "|" + self.checksum
            self.client_CheckSum.sendall(msg.encode())
            #visszajelzés fogadása checkSum szervertől
            message = self.client_CheckSum.recv(1024).strip().decode()
            print(message)

    def readFile(self, file):
            line = file.readline()
            # méret elküldése
            length = str(len(line)).encode()
            self.client_NetCopy.sendall(length)
            c = self.client_NetCopy.recv(1024).strip().decode()
            if line: #ha beolvasott sikeresen egy sort
                self.client_NetCopy.sendall(line)
                confirm = self.client_NetCopy.recv(1024).strip().decode() #szerver megkapta a sort
                if confirm:
                    return True
            else:
                return False

    def sendData(self):
        try:
            self.calculateCheckSum()
            with open(self.file_path, 'rb') as file:
                not_empty = True
                while not_empty:
                    not_empty = self.readFile(file)
            self.client_NetCopy.sendall(b'OVER') #üres üzenetre tudni fogja a szerver, hogy vége van a fájlnak
            self.client_NetCopy.close()
            self.client_CheckSum.close()
            sys.exit()
        except KeyboardInterrupt:
            print("\nClient disconnected.")
            self.client_NetCopy.sendall(b"OVER")
            self.client_NetCopy.close()
            self.client_CheckSum.close()
            sys.exit()

NetCopyClient = NetCopyClient(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
NetCopyClient.sendData()