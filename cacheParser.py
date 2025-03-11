import os
import glob

def cerca_sequenza(file_path, target_sequence) -> str | None:
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

            # Cerca la sequenza nel buffer
            index = buffer.find(target_sequence)
            if index != -1:

                # Leggi il blocco successivo per estrarre il nome del file
                block = file.read(block_size)
                buffer += block

                # Estrai il nome del file (fino al primo byte nullo \x00)
                buffer = buffer[index + len(target_sequence):]
                nome_file = buffer[:buffer.find(b'\x00')]

                # Stampa il nome del file

                return nome_file.decode('utf-8')

            # Se la sequenza non è stata trovata, controlla se potrebbe essere spezzata
            # Mantieni solo gli ultimi (len(target_sequence) - 1) byte nel buffer
            buffer = buffer[-(len(target_sequence) - 1):]

            # Aggiorna la posizione
            position += len(block)


# Sequenza da cercare (in esadecimale: 55 10 04 01 00 00 00)
toCheck = b'U\x10\x04\x01\x00\x00\x00\x0C\x00\x00\x00'

# Directory da controllare
search_dir = "/Users/alessandrocondello/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application Support/Microsoft User Data/OneNote/15.0/cache/"

# Trova tutti i file nella directory
files = list(filter(os.path.isfile, glob.glob(os.path.join(search_dir, "*"))))
files.sort(key=lambda x: os.path.getmtime(x))

# Prendi gli ultimi 5 file (escludendo l'ultimo) e inverti l'ordine
files = files[-5:-1][::-1]

# Analizza ogni file
for file in files:
    if (found := cerca_sequenza(file, toCheck)) is not None:
        print(f"Nome del file: {found}")
        break