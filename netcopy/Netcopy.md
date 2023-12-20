# Netcopy alkalmazás
---
## program célja
A program célja egy "fájlmásoló", ahol a szerver a kliens által küldött fájlról készít egy másolatot, majd annak helyességét is ellenőrzi.

## projekt részei
+ kliens:
  - A kliens elsőnek csatlakozik a Checksum szerverre, illetve azon szerverre, melynek át akarja küldeni a fájlt (kép/txt/bináris fájl). Csatlakozás után
    készít egy md5 checksumot (ellenörzőkód) a fájlhoz, amit a fájl többi adatával együtt feltölt a Checksum szerverre. Ezt követően
    megkezdi a fájl adatainak folyamatos átküldését a szerver felé. Ha ez a folyamat befejeződött, a kliens leáll.
+ szerver:
  - A szerver szintén csatlakozik a Checksum szerverre, majd ezt követően várja a kliens csatlakozását. Ha a kliens csatlakozott, folyamatosan fogadja
    és egy másolatba menti a kliens által küldött fájl adatait. Ha ez befejeződött, lekéri a Checksum szerverről a fájlhoz tartozó ellenőrző kódot,
    majd ő maga generál a másolat alapján egyet, és a két md5 checksumot összeveti egymással. Ha egyeznek, akkor a fájlávitel sikeres, ellenkező esetben
    a fájlátvitel sikertelen, a fájl korruptált, ezeknek státuszát jelzi is a program végén. Ezt követően a szerver leáll.
+ checksum:
  - A szerver a fájlok adatainak (fájl azonosító, fájl elérési útja, checksum hossz, checksum) ideiglenes tárolására szolgál. A kliensek ide tudják
    feltölteni a fájlok adatait, a szerverek pedig innen tudják lekérni. Az adatokat 60 másodpercig tárolja. Egyszerre képes több klienssel is kommunákálni.

## futtatási sorrend
+ 1.) Checksum szerver futtatása - minden kliens és szerver erre fel kell, hogy csatlakozzon
+ 2.) szerverek futtatása
+ 3.) kliensek futtatása

## program futtatása
  - windows környezetben:
    * checksum: py checksum_srv.py [bind-address] [bind-port]
         * pl.: py checksum_srv.py localhost 10000
    * (egy) kliens: py netcopy_cli.py [server-bind-address] [server-bind-port] [checksum-bind-address] [checksum-bind-port] [file-azon] [file-path]
         * pl.: py netcopy_cli.py localhost 10001 localhost 10000 1 C:\Users\User\Desktop\picture.jpg
    * (egy) szerver: py netcopy_srv.py [server-bind-address] [server-bind-port] [checksum-bind-address] [checksum-bind-port] [file-azon] [file-path]
         * pl.: py netcopy_srv.py localhost 10001 localhost 10000 1 C:\Users\User\Desktop\picturecopy.jpg
  - linux környezetben:
    * checksum: python3 checksum_srv.py [bind-address] [bind-port]
         * pl.: python3 checksum_srv.py localhost 10000
    * (egy) kliens: python3 netcopy_cli.py [server-bind-address] [server-bind-port] [checksum-bind-address] [checksum-bind-port] [file-azon] [file-path]
         * pl.: python3 netcopy_cli.py localhost 10001 localhost 10000 1 C:\Users\User\Desktop\picture.jpg
    * (egy) szerver: python3 netcopy_srv.py [server-bind-address] [server-bind-port] [checksum-bind-address] [checksum-bind-port] [file-azon] [file-path]
         * pl.: python3 netcopy_srv.py localhost 10001 localhost 10000 1 C:\Users\User\Desktop\picturecopy.jpg 
