# Barkóba játék szimulálása TCP socketekkel
---
## projekt részei
+ server.py:
  - A szerver feladata, hogy kitaláljon egy nyertes számot 1 és 100 között, melynek kitalálása a kliensek feladata.
    Folyamatosan képes fogadni a kliensek tippjeit, illetve azok alapján visszajelzést adni nekik (I : helyes tipp, N : rossz tipp,
    Y : Nyert a kliens, K : Kiesett a kliens, V : a játéknak vége (az egyik kliens sikeresen kitalálta a számot)).
    A szerver egy játék "session"-je addig fut, míg egy kliens ki nem találja azt. Ha ez megtörténik, a jelenlévő klienseket lecsatlakoztatja,
    majd egy új játékot kezd, amire a kliensek újra fel tudnak csatlakozni. Ha a szerver leáll/megszakítják, a kliensek is lekapcsolódnak és
    abbahagyják a tippelgetést.
+ client.py:
  - A kliens feladata, hogy felcsatlakozás után 1-5 másodperc elteltével tegyen egy tippet: tippel egy számot, illetve hogy a nyertes szám ahhoz
    képest nagyobb, kisebb, vagy akár egyenlő-e, pl. > 50. Mivel a program célja a visszajelzés alapján javított tippek szimulálása lenne, így
    a kliens folyamatosan számon tartja azt a jelenlegi intervallumot, amelyben benne lehet a nyertes szám, és logaritmus keresés segítségével
    próbálja meg kitalálni a számot (azaz az intervallum közepét tippeli mindig). Ha =-vel tippel, és eltalálja a számot, akkor nyert, ellenkező
    esetben a szerver kiejti őt, de van lehetősége visszacsatlakozni.

## program futtatása
  - windows környezetben:
    * szerver: py server.py [bind-address] [bind-port]
         * pl.: py server.py localhost 10000
    * (egy) kliens: py client.py [bind-address] [bind-port]
         * pl.: py client.py localhost 10000
  - linux környezetben:
    * szerver: python3 server.py [bind-address] [bind-port]
         * pl.: python3 server.py localhost 10000
    * (egy) kliens: python3 client.py [bind-address] [bind-port]
         * pl.: python3 client.py localhost 10000  
