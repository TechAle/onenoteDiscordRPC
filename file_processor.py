import os
import sqlite3
import subprocess
from urllib.parse import unquote
import json

import tool


# TODO prova a comprendere come prendere il nome del file più recente
# Nelle cache ci sono 1000 versione del nome e come è stato cambiato
def cercaNome(file_path) -> str | None:
    block_size = 1024
    if not os.path.isfile(file_path):
        print(f"Il file {file_path} non esiste.")
        return

    with open(file_path, 'rb') as file:
        position = 0
        buffer = b''
        while True:
            block = file.read(block_size)
            if not block:
                break
            buffer += block
            index = buffer.find(b"\x7a\x1d\x00\x14\x2c\x34\x00\x20\xb4\x1c\x00\x88")
            if index != -1:
                buffer = buffer[index:]
                block = file.read(block_size)
                buffer += block
                newIndex = buffer.find(b"\x98\x34")
                if newIndex != -1 and newIndex < 50:
                    buffer = buffer[newIndex + 4:]
                    newIndex = buffer.find(b"\x00\x00\x00")
                    if newIndex != -1 and newIndex < 50:
                        buffer = buffer[newIndex + 3:]
                        newIndex = buffer.find(b"\x00\x00\x00")
                        if newIndex != -1 and newIndex < 50:
                            newIndex = 0
                            buffer = buffer[newIndex + 3:]
                            while not tool.is_printable_ascii(buffer[newIndex]):
                                newIndex += 1
                            buffer = buffer[newIndex:]
                            buffer = buffer[:buffer.find(b"\x00")]
                            return buffer.decode("latin-1", errors="ignore")
            if len(buffer) > block_size:
                buffer = buffer[block_size:]
            position += len(block)

def getCartella(data_dir):
    with open(data_dir, 'r') as file:
        data = json.load(file)
    latest_entry = max(data["ResourceInfoCache"], key=lambda x: x["LastAccessedAt"])
    return unquote(latest_entry["Url"].replace("%5eL", "^").split("/")[5])

def getFile(cache_dir):
    command = f'ls -lt "{cache_dir}" | awk \'NR>1 {{print $9}}\' | head -15'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    files = [os.path.join(cache_dir, file) for file in result.stdout.splitlines()]
    newIndex = -1
    for index, file in enumerate(files):
        if "tmp" in file:
           newIndex = index
           break
    if newIndex != -1:
        files.pop(newIndex)
        tmp_dir = os.path.join(cache_dir, "tmp")
        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            tmp_files = [
                (os.path.join(tmp_dir, f), os.path.getmtime(os.path.join(tmp_dir, f)))
                for f in os.listdir(tmp_dir)
                if os.path.isfile(os.path.join(tmp_dir, f))
            ]
            tmp_files.sort(key=lambda x: x[1], reverse=True)
            files_with_mtime = [
                (file, os.path.getmtime(file)) for file in files
            ]
            files_with_mtime.extend(tmp_files)
            files_with_mtime.sort(key=lambda x: x[1], reverse=True)
            files = [file[0] for file in files_with_mtime]
    for file in files:
        if (found := cercaNome(file)) is not None:
            return found

def getPath(cartella, file, dom_dir):
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