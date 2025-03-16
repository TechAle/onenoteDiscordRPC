import os
from pathlib import Path


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
