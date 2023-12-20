# Áramkör működésének szimulálása
---
## Program célja
A program leszimulálja az áramkörbeli erőforrások lefoglalását és felszabadítását a JSON fájlban megadott topológia, kapacitások
és igények alapján.

## projekt részei
+ client.py:
  - A kliens feladata, hogy a kapott json fájl alapján leszimulálja megfelelő sorrendben a lefoglalásokat és felszabadításokat. A JSONben adottak
    a megengedett útvonalak két végpont között, így ha van olyan útvonal, ami még lefoglalható - illetve bír mág annyi terhelést -,
    akkor azt lefoglalja, egyéb esetben a lefoglalás sikertelen. A megfelelő sorrendben feloldja a lefoglalt áramköröket.
+ cs1.json:
  - Tartalmazza a végpontokat, a switcheket, a lehetséges útvonalakat, illetve a lefoglalandó és felszabadítandó útvonalakat azok terhelésével
    együtt.

## program futtatása
  - windows környezetben:
    * kliens: py client.py [json-file]
         * pl.: py client.py cs1.json
  - linux környezetben:
    * kliens: python3 client.py [json-file]
         * pl.: python3 client.py cs1.json 
