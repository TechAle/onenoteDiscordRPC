import os
import glob
import time

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


# Directory da controllare
search_dir =  os.path.expanduser("~") + "/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application Support/Microsoft User Data/OneNote/15.0/cache/"

# Trova tutti i file nella directory
lastFile = None
while True:
    files = list(filter(os.path.isfile, glob.glob(os.path.join(search_dir, "*"))))
    files.sort(key=lambda x: os.path.getmtime(x))

    # Prendi gli ultimi 5 file (escludendo l'ultimo) e inverti l'ordine
    files = files[-8:-1][::-1]

    # Analizza ogni file
    for file in files:
        if (found := cercaNome(file)) is not None:
            if found != lastFile:
                print(found)
            lastFile = found
            break

    time.sleep(1)

# 000006V3.bin
'''
    000006V3.bin
    Questo file contiene il database di onenote
    E' un semplice "id-corrente"
    Idea: prendo l'id più alto/grande
        NotebookUrl è il modo per trovare il padre più alto
    E poi vado ricorsivamente in basso, creando una struttura ad albero
    
    Documents_en-IT
    Questo contiene i notebook ben formattati
'''

'''
    001C0DC1 8C521004 01000000 0F000000
    001CDD34 0088982C 54501004 01000000 0A000000
    001CBACA D0541004 01000000 1D000000
    001CDD34 0088F049 433D0904 01000000 0E000000
    001CC81C 001CFFC8 6D491004 01000000 18000000
    001CB2E7 02551004 01000000 02000000
    
    
    
    {75AAD487-052E-3E4A-A805-CFADD19B35EC}{59}
    {75AAD487-052E-3E4A-A805-CFADD19B35EC}{65}
    
    Idea:
    Vado nella cache, estraggo il nome, cerco il nome nel database, 
    Cerco il padre ricorsivamente, così creo il path
'''
