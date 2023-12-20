import sys
import socket
import random
import select
import struct


class BarkobaServer:
    def __init__(self, address, port, timeout=1):
        # szerver socket létrehozása
        self.server = self.setupBarkobaServer(address, port)
        self.inputs = [self.server]
        self.timeout = timeout

        # játékhoz
        self.winning_number = random.randint(1, 100)
        self.FOUND = False
        print(f"[SERVER] A nyerő szám: {self.winning_number}")

    def setupBarkobaServer(self, address, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (address, port)
        server.bind(server_address)
        server.listen(999)
        return server

    def runServer(self):
        while self.inputs:  # amíg a szerver fut
            try:
                self.runGame()
            except KeyboardInterrupt:
                print("\nClosing the Barkoba game.")
                msg = ('V'.encode(), 1)
                pack = struct.pack('ci', *msg)
                for client in self.inputs:
                    if client != self.server:
                        client.sendall(pack)
                        self.inputs.remove(client)
                        client.close()
                self.inputs = []

    def runGame(self):
        # amíg egy játék session fut (nem találták ki a számot)
        while not self.FOUND:
            for sock in self.inputs:
                if sock.fileno() == -1:
                    self.inputs.remove(sock)
            readable, writable, exceptional = select.select(
                self.inputs, [], self.inputs, self.timeout)
            if not (readable or writable or exceptional):
                continue

            self.manageInputs(readable)
            self.manageExceptionalCondition(exceptional)

        # kapcsolat bontása a többi klienssel:
        print('===============================')
        msg = ('V'.encode(), 0)
        packk = struct.pack('ci', *msg)

        while len(self.inputs) > 1: #amíg nem csak a szerver van benne
            readable, writable, exceptional = select.select(self.inputs, [], self.inputs, self.timeout)
            if not (readable or writable or exceptional):
                continue
            for read in readable:
                if read == self.server:
                    self.joinNewPlayer(read)
                data = read.recv(1024).strip()
                if data:
                    read.sendall(packk)
                else:
                    self.inputs.remove(read)
                    read.close()

        # következő sessionre új  számot generál
        self.winning_number = random.randint(1, 100)
        print(f"[SERVER] Az új nyerő szám: {self.winning_number}")
        self.FOUND = False
        self.runGame()  # új session indítása

    def manageInputs(self, readable):
        for socket in readable:
            if socket is self.server:  # ha socket a főszerver --> akkor új kapcsolat akar létrejönni
                self.joinNewPlayer(socket)
            else:  # egyébként már egy meglévő kapcsolat kezelése
                self.evaluateGuess(socket)

    def manageExceptionalCondition(self, exceptional):
        for socket in exceptional:
            print(f'Exception occured for {socket.getpeername()}')
            self.inputs.remove(socket)
            socket.close()

    def joinNewPlayer(self, socket):
        if self.FOUND is False:
            connection, _ = socket.accept()
            connection.setblocking(0)
            self.inputs.append(connection)

    def evaluateGuess(self, socket):
        client_guess = socket.recv(1024)
        feedback = ""
        temp_num = 0

        if client_guess:  # ha érkezett üzenet
            client_guess = client_guess.strip()
            guessed_relation, guessed_number = struct.unpack('ci', client_guess)
            guessed_relation = guessed_relation.decode()
            print(f"[CLIENT <{socket.getpeername()}>] {guessed_relation} {guessed_number}")
            if guessed_relation == '=':
                if int(guessed_number) == self.winning_number:  # ha kitalálta az adott kliens
                    feedback = 'Y'
                    print(f"A játéknak vége! A számot kitalálta: <{socket.getpeername()}>")
                    self.FOUND = True
                else:
                    feedback = 'K'
                    print(f"<{socket.getpeername()}> című kliens kiesett")
            elif guessed_relation == '<':
                # tippelt számnál kisebb
                if self.winning_number < int(guessed_number):
                    feedback = 'I'
                else:
                    feedback = 'N'
            else:  # '>'
                # tippelt számnál nagyobb
                if self.winning_number > int(guessed_number):
                    feedback = 'I'
                else:
                    feedback = 'N'
            # visszajelzés küldése a szervernek
            print(f"[SERVER] feedback: {feedback}")
            msg = (feedback.encode(), temp_num)
            pack = struct.pack('ci', *msg)
            socket.sendall(pack)

        else:  # kliens megszakította a kapcsolatot
            self.inputs.remove(socket)
            socket.close()


BarkobaServer = BarkobaServer(sys.argv[1], int(sys.argv[2]))
BarkobaServer.runServer()
