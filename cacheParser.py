import json
import os
import glob
import sqlite3
import time
from urllib.parse import unquote

import tool

sequenzaInizio = b'\x1c'

def cercaNome(file_path) -> str | None:
    """
    Cerca la sequenza target_sequence nel file specificato.
    Se trovata, stampa la posizione e il nome del file associato.
    """
    # Dimensione del blocco di lettura
    block_size = 1024

    # Verifica se il file esiste
    if not os.path.isfile(file_path):
        print(f"Il file {file_path} non esiste.")
        return

    # Apri il file in modalità binaria
    with open(file_path, 'rb') as file:
        position = 0  # Tieni traccia della posizione nel file
        buffer = b''  # Buffer per memorizzare i dati tra i blocchi

        while True:
            # Leggi un blocco di dati
            block = file.read(block_size)
            if not block:
                # Fine del file raggiunta
                break

            # Aggiungi il blocco corrente al buffer
            buffer += block

            '''
                Tutto il codice di sopra avrà la funzione
                Di trovare la seguente sequenza: 
                7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C DD340088 5D578950 10040100 00000800 0000
                Nota che, ci sono parti fisse e parti variabili in questa sequenza
                Per questo che sono necessari così tanti if
            '''
            index = buffer.find(b"\x7a\x1d\x00\x14\x2c\x34\x00\x20\xb4\x1c\x00\x88")
            if index != -1:
                buffer = buffer[index:]
                # Leggi il blocco successivo per estrarre il nome del file
                block = file.read(block_size)
                buffer += block

                newIndex = buffer.find(b"\x98\x34")
                if newIndex != -1 and newIndex < 50:
                    buffer = buffer[newIndex + 4:]
                    newIndex = buffer.find(b"\x00\x00\x00")
                    if newIndex != -1:
                        buffer = buffer[newIndex + 3:]
                        newIndex = buffer.find(b"\x00\x00\x00")
                        if newIndex != -1:
                            newIndex = 0
                            buffer = buffer[newIndex + 3:]
                            while not tool.is_printable_ascii(buffer[newIndex]):
                                newIndex += 1
                            buffer = buffer[newIndex:]
                            buffer = buffer[:buffer.find(b"\x00")]
                            return buffer.decode("latin-1", errors="ignore")

            # Se la sequenza non è stata trovata, controlla se potrebbe essere spezzata
            # Mantieni solo gli ultimi (len(target_sequence) - 1) byte nel buffer
            if len(buffer) > block_size:
                buffer = buffer[block_size:]

            # Aggiorna la posizione
            position += len(block)


'''
    Questo commento serve come preghiera per tutte le lacrime che il programmatore, io, ho versato
    per via di questo codice. Che sia benedetto e che non debba mai più essere modificato.
    Un messaggio per gli sviluppatori di OneNote: vi prego, create un'API. Vi prego, non create incosistenze.
    VI PREGO, NON FATEMI PIANGERE DINUOVO.
'''
def getCartella():
    with open(data_dir, 'r') as file:
        data = json.load(file)

    # Trova l'URL con il LastAccessedAt più recente
    latest_entry = max(data["ResourceInfoCache"], key=lambda x: x["LastAccessedAt"])
    return unquote(latest_entry["Url"].replace("%5eL", "^").split("/")[5])


lastFile = None


def getFile():
    files = list(filter(os.path.isfile, glob.glob(os.path.join(cache_dir, "*"))))
    files.sort(key=lambda x: os.path.getmtime(x))

    # Prendi gli ultimi 5 file (escludendo l'ultimo) e inverti l'ordine
    files = files[::-1]

    # Analizza ogni file
    for file in files:
        if (found := cercaNome(file)) is not None:
            return found

def getPath(cartella, file):
    allDicts = tool.getFiles(".db", dom_dir)
    checkDb = None
    for currentDict in allDicts:
        conn = sqlite3.connect(str(currentDict.absolute()))
        c = conn.cursor()
        c.execute("SELECT Title FROM `Entities` WHERE `Type` = 4;")
        if (name := c.fetchone()) is not None and name[0] == cartella:
            checkDb = currentDict
            break
        conn.close()

    dbFile = None
    if checkDb is not None:
        allItems = c.execute("SELECT * FROM 'Entities' WHERE Type = 1")
        for item in allItems.fetchall():
            if item[13] == file:
                dbFile = item
                break
    if dbFile is None:
        dbFile = c.execute(
            "SELECT * FROM 'Entities' WHERE RecentTime != 0 AND Type = 1 ORDER BY LastModifiedTime DESC").fetchone()
        print("Rimedio")

    if dbFile is not None:
        parents = dbFile[5]
        path = []
        while True:
            c.execute(f"SELECT * FROM 'Entities' WHERE GOID = '{parents}'")
            parent = c.fetchone()
            if parent is None:
                break
            path.append(parent[13])
            parents = parent[5]
        path = path[::-1]
        c.close()
        path.append(file)
        return path
    else:
        c.close()
        return [cartella, file]


# Directory da controllare
cache_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                       "Support/Microsoft User Data/OneNote/15.0/cache/")
data_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                      "Support/Microsoft/Office/16.0/ResourceInfoCache/data.json")
dom_dir = os.path.expanduser("~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                             "Support/Microsoft User Data/OneNote/15.0/FullTextSearchIndex/")


# Trova tutti i file nella directory
while True:
    cartella = getCartella()
    file = getFile()
    if file != lastFile:
        cartella = getPath(cartella, file)
        lastFile = file
        print(f"Cartella: {cartella}")
    time.sleep(1)

'''
    7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C FDDC4352 10040100 00001A00 0000

    7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C 0B1A4D52 10040100 00000900 0000
    7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C 57EC1653 10040100 00000A00 0000
    7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C DD340088 97D5334F 00000C00 0000
    7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C 6CC00154 10040100 00000600 0000
    7A1D0014 2C340020 B41C0088 FE1C0010 131E0024 9834001C DD340088 E05BBC4A 00002800 0000
'''