import random
import sys
import socket
import time
import math
import struct

class BarkobaClient:
    def __init__(self, address, port):
        #kliens socket létrehozása
        server_address = (address, port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(server_address)

        #saját adatok inicializálása
        self.amount = 2 #valószínűségeket befolyásoló szorzó
        self.iteration = 1 #hanyadik tippje a kliensnek
        self.limits = {"min" : 0, "max" : 101} # 0 < number < 101 [1..100]
        self.ratios = {"=" : [0,0], "<" : [1,50], ">" : [51,100]} #kezdeti ráták a relációsjelekre
        self.thinking_time = 0
        self.server_msg = ''
        self.relation = ''
        self.guessed_number = 0
        self.CLOSING_MESSAGE = ['Y', 'K', 'V']

        print(f"[STARTING RANGE: {self.limits['min']} < winning number < {self.limits['max']}]")

    def changeLimits(self):
        if self.server_msg == 'I': #ha sikeres a tipp
            if self.relation == '<':
                self.limits["max"] = self.guessed_number
            else:
                self.limits["min"] = self.guessed_number
        elif self.server_msg == 'N':
            if self.relation == '<':
                self.limits["min"] = self.guessed_number-1
            else:
                self.limits["max"] = self.guessed_number+1
        print(f"[NEW RANGE: {self.limits['min']} < winning number < {self.limits['max']}]")

    def changeRatios(self):
        #korlátok megváltoztatása:
        self.ratios["="][1] += (self.iteration*self.amount)
        self.ratios["<"][0] = self.ratios["="][1] + 1
        self.ratios["<"][1] += math.floor((self.iteration*self.amount)/2)
        self.ratios[">"][0] = self.ratios["<"][1] + 1
        if self.iteration == 1:
            self.ratios["="][0] = 1
        elif self.ratios["="][1] >= 100:
            self.ratios["="][1] = 100
            self.ratios["<"][0], self.ratios["<"][1] = 0, 0
            self.ratios[">"][0], self.ratios[">"][1] = 0, 0
        self.iteration += 1

    def getRelation(self):
        if (self.guessed_number-1 == self.limits["min"] and self.guessed_number+1 == self.limits["max"]) or (self.relation >= self.ratios["="][0] and self.relation <= self.ratios["="][1]):
            return "="
        elif self.relation >= self.ratios["<"][0] and self.relation <= self.ratios["<"][1]:
            if self.guessed_number-1 == self.limits["min"]:
                return ">"
            else:
                return "<"
        else:
            if self.guessed_number+1 == self.limits["max"]:
                return "<"
            else:
                return ">"
        
    def handleMessageFromBarkobaServer(self):
        self.server_msg = self.client.recv(1024)
        self.server_msg = self.server_msg.strip()
        if self.server_msg:
            self.server_msg, server_num = struct.unpack('ci', self.server_msg)
            self.server_msg = self.server_msg.decode()
        else: 
            self.server_msg = 'V'
        print(f"[SERVER] {self.server_msg}")
        if self.server_msg in self.CLOSING_MESSAGE:
            if server_num == 0: #normális kilépés, nem történt szerver shutdown, vagyis kliensnek kell először kilépnie
                self.client.sendall(b"") # ekkor küldjön üres "visszaigazoló" üzenetet a szervernek, hogy az is bonthatja a kapcsolatot
            sys.exit()

    def makeGuess(self):
        if self.server_msg != '' and self.relation != '' and self.guessed_number != 0: #azaz a szervertől már kapott választ
            #tippelési tartomány módosítása
            self.changeLimits()
        #tippelés
        self.thinking_time = random.randint(1,5)
        print(f"[KLIENS] gondolkodik {self.thinking_time} másodpercet...")
        time.sleep(self.thinking_time) #"gondolkodik" random 1-5 másodpercet
        self.guessed_number = self.limits["min"] + math.floor((self.limits["max"]-self.limits["min"])/2)
        self.relation = random.randint(1,100)
        self.relation = self.getRelation()
        print(f"[TIPP] {self.relation} {self.guessed_number}")
        pack = (self.relation.encode(),
                self.guessed_number)
        guess = struct.pack('ci', *pack)
        self.client.sendall(guess) #tipp elküdése

        self.changeRatios()

    def play(self):
        while True:
            try:
                self.makeGuess()
                self.handleMessageFromBarkobaServer()
            except KeyboardInterrupt:
                print("\nClient disconnected.")
                self.client.sendall(b"")
                sys.exit()

BarkobaClient = BarkobaClient(sys.argv[1], int(sys.argv[2]))
BarkobaClient.play()