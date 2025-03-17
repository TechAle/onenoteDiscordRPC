import os
import subprocess
from pathlib import Path

from discordRPC import closeDiscord, openDiscord


def hex_string_to_bytes(hex_string, format_output='bytes'):
    # Dividi la stringa in una lista di valori esadecimali
    hex_values = hex_string.split()

    # Converti ogni valore esadecimale in un intero e crea un oggetto bytes
    byte_sequence = bytes(int(hex_value, 16) for hex_value in hex_values)

    # Formatta l'output in base al parametro format_output
    if format_output == 'bytes':
        return byte_sequence
    elif format_output == 'hex':
        # Restituisci una stringa esadecimale continua
        return byte_sequence.hex()
    elif format_output == 'escaped':
        # Restituisci una stringa con ogni byte rappresentato come \xHH
        return ''.join(rf'\x{byte:02x}' for byte in byte_sequence)
    else:
        raise ValueError("format_output deve essere 'bytes', 'hex', o 'escaped'.")


def is_printable_ascii(byte):
    return 32 <= byte <= 126


def byteExists(byte, buffer):
    return buffer.find(byte) != -1


def getFiles(extension, directory, sortDate=False):
    files = [f for f in Path(directory).iterdir() if f.suffix == extension]
    return max(files, key=lambda x: x.stat().st_mtime) if sortDate else files

def processExists(name="OneNote.app") -> bool:
    # Esegui il comando 'ps aux' e cattura l'output
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)

    # Cerca il nome del processo nell'output
    if name in result.stdout:
        return True
    return False


def checkOneNote(openedBefore):
    if not processExists():
        if openedBefore:
            closeDiscord()
            openedBefore = False
        return False, openedBefore
    if not openedBefore:
        openDiscord()
        openedBefore = True
    return True, openedBefore
