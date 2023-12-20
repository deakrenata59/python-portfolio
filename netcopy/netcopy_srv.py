import sys
import hashlib
import socket

class NetCopyServer:
    def createServer(self, srv_ip, srv_port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (srv_ip, srv_port)
        server.bind(server_address)
        server.listen(5)
        return server

    def connectToCheckSum(self, chsum_srv_ip, chsum_srv_port):
        server_address = (chsum_srv_ip, chsum_srv_port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        return client

    def __init__(self, srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_azon, file_path):
        #csatlakozás a CheckSum szerverhez
        self.client_CheckSum = self.connectToCheckSum(chsum_srv_ip, int(chsum_srv_port))
        #saját szerver létrehozása
        self.server_NetCopy = self.createServer(srv_ip, int(srv_port))

        #saját adatok
        self.file_azon = int(file_azon)
        self.file_path = file_path
        self.checksum = ""
        self.checksum_len = 0

    def joinClient(self):
        client, _ = self.server_NetCopy.accept()
        return client

    def copyFile(self, client, copied_file, line_size):
        if line_size == -1:
            file_part = b'OVER'
        else:
        #üzenet fogadása klienstől
            file_part = client.recv(line_size) #ez bináris formátumban van
        if file_part and (file_part != b'OVER'):
            copied_file.write(file_part)
            client.sendall(b"OK")
            return False
        elif file_part == b'OVER':
            client.close()
            return True
        else:
            return False

    def acceptFile(self):
        #klienssel való kapcslat felállítása
        client = self.joinClient()

        with open(self.file_path, 'wb') as copied_file:
            COPY_OVER = False
            while not COPY_OVER:
                line_size = self.acceptLineSize(client)
                COPY_OVER = self.copyFile(client, copied_file, line_size)

        with open(self.file_path, 'rb') as file:
            data = file.read()
            md5 = hashlib.md5()
            md5.update(data)
            self.checksum = md5.hexdigest()
            self.checksum_len = len(md5.hexdigest())
        #lekéri a checksumtól az ellenőrző adatokat
        msg = "KI|" + str(self.file_azon)
        self.client_CheckSum.sendall(msg.encode())
        data = self.client_CheckSum.recv(1024).strip().decode()
        print(data)
        data = data.split('|')
        checksum_len = int(data[0])
        if data[1]:
            checksum = data[1]
        else:
            checksum = "-1"
        if (checksum_len == self.checksum_len) and checksum == self.checksum:
            print("CSUM OK")
        else:
            print("CSUM CORRUPTED")
        
        #terminálás
        self.client_CheckSum.close()
        self.server_NetCopy.close()
        sys.exit()

    def acceptLineSize(self, client):
        size = client.recv(1024).strip().decode()
        if size == 'OVER':
            return -1
        else:
            client.sendall(b"OK")
            return int(size)

NetCopyServer = NetCopyServer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
NetCopyServer.acceptFile()