import json
import os
import glob
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
                            return buffer.decode("utf-8", errors="ignore")

            # Se la sequenza non è stata trovata, controlla se potrebbe essere spezzata
            # Mantieni solo gli ultimi (len(target_sequence) - 1) byte nel buffer
            buffer = buffer[block_size:]

            # Aggiorna la posizione
            position += len(block)


def getCartella():
    with open(data_dir, 'r') as file:
        data = json.load(file)

    # Trova l'URL con il LastAccessedAt più recente
    latest_entry = max(data["ResourceInfoCache"], key=lambda x: x["LastAccessedAt"])
    return unquote(latest_entry["Url"].split("/")[-2])


lastFile = None


def getFile(lastFile):
    files = list(filter(os.path.isfile, glob.glob(os.path.join(cache_dir, "*"))))
    files.sort(key=lambda x: os.path.getmtime(x))

    # Prendi gli ultimi 5 file (escludendo l'ultimo) e inverti l'ordine
    files = files[-8:-1][::-1]

    # Analizza ogni file
    for file in files:
        if (found := cercaNome(file)) is not None:
            return found


# Directory da controllare
cache_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                       "Support/Microsoft User Data/OneNote/15.0/cache/")
data_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                      "Support/Microsoft/Office/16.0/ResourceInfoCache/data.json")

# Trova tutti i file nella directory
while True:
    cartella = getCartella()
    file = getFile(lastFile)
    if file != lastFile:
        print(f"Cartella: {cartella}")
        print(f"File: {file}")
        lastFile = file

    time.sleep(1)