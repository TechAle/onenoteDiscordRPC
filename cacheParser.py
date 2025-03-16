import heapq
import json
import os
import glob
import sqlite3
import subprocess
import threading
import time
from urllib.parse import unquote

import tool
from discordRPC import DiscordRPC


def processExists(name="OneNote.app") -> bool:
    for process in os.popen('ps aux'):
        if process.__contains__(name):
            return True
    return False


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
    # Esegui il comando shell per ottenere i 15 file più recenti
    # Aggiungi virgolette al percorso per gestire spazi e caratteri speciali
    command = f'ls -lt "{cache_dir}" | awk \'NR>1 {{print $9}}\' | head -15'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    files = [os.path.join(cache_dir, file) for file in result.stdout.splitlines()]

    newIndex = -1
    for index, file in enumerate(files):
        if "tmp" in file:
           newIndex = index
           break

        # Se è stato trovato un file con "tmp", rimuovilo dall'array
    if newIndex != -1:
        files.pop(newIndex)

        # Aggiungi tutti i file dalla directory "tmp" (se esiste)
        tmp_dir = os.path.join(cache_dir, "tmp")
        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            # Ottieni tutti i file nella directory "tmp" con la loro data di modifica
            tmp_files = [
                (os.path.join(tmp_dir, f), os.path.getmtime(os.path.join(tmp_dir, f)))
                for f in os.listdir(tmp_dir)
                if os.path.isfile(os.path.join(tmp_dir, f))
            ]

            # Ordina i file di "tmp" in base alla data di modifica (dal più recente al più vecchio)
            tmp_files.sort(key=lambda x: x[1], reverse=True)

            # Aggiungi i file di "tmp" all'array `files` con le loro date di modifica
            files_with_mtime = [
                (file, os.path.getmtime(file)) for file in files
            ]
            files_with_mtime.extend(tmp_files)

            # Ordina l'array combinato in base alla data di modifica
            files_with_mtime.sort(key=lambda x: x[1], reverse=True)

            # Estrai solo i percorsi dei file (senza la data di modifica)
            files = [file[0] for file in files_with_mtime]


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


discord = None


def openDiscord():
    global discord
    discord = DiscordRPC("1084765396344782868", threading.current_thread())
    discord.start_rpc()
    discord.modify_presence(
        state="...",
        details="Caricamento...",
        large_image="pic",
        large_text="Made with tears",
        start=time.time(),  # Timestamp di inizio
        buttons=[{"label": "Github", "url": "https://github.com/TechAle/onenoteDiscordRPC"}]
    )


def closeDiscord():
    if type(discord) == DiscordRPC:
        # noinspection PyUnresolvedReferences
        discord.close_rpc()


openedBefore = False


def checkOneNote():
    global openedBefore
    if not processExists():
        if openedBefore:
            closeDiscord()
            print("OneNote è stato chiuso.")
            openedBefore = False
        return False
    if not openedBefore:
        openDiscord()
        print("OneNote è stato aperto.")
        openedBefore = True
    return True


# Directory da controllare
cache_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                       "Support/Microsoft User Data/OneNote/15.0/cache/")
data_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                      "Support/Microsoft/Office/16.0/ResourceInfoCache/data.json")
dom_dir = os.path.expanduser("~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                             "Support/Microsoft User Data/OneNote/15.0/FullTextSearchIndex/")

# Trova tutti i file nella directory
while True:
    if not checkOneNote():
        time.sleep(1)
        continue
    cartella = getCartella()
    file = getFile()
    if file != lastFile:
        cartella = getPath(cartella, file)
        lastFile = file
        print(f"Cartella: {cartella}")
        # noinspection PyUnresolvedReferences
        discord.modify_presence(
            state='/'.join(cartella[:-1]),
            details='Scrivendo ' + cartella[-1],
        )
    time.sleep(1)
