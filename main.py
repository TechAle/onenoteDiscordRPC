import os
import time

from discordRPC import DiscordRPC
from file_processor import getCartella, getFile, getPath
from tool import checkOneNote

# Directory da controllare
cache_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                       "Support/Microsoft User Data/OneNote/15.0/cache/")
data_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                      "Support/Microsoft/Office/16.0/ResourceInfoCache/data.json")
dom_dir = os.path.expanduser("~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                             "Support/Microsoft User Data/OneNote/15.0/FullTextSearchIndex/")

openedBefore = False
lastFile = None
global discord

while True:
    openedBefore, _ = checkOneNote(openedBefore)
    if not openedBefore:
        time.sleep(30)
        continue
    cartella = getCartella(data_dir)
    file = getFile(cache_dir)
    if file != lastFile:
        cartella = getPath(cartella, file, dom_dir)
        lastFile = file
        DiscordRPC.discord.modify_presence(
            state='/'.join(cartella[:-1]),
            details='Scrivendo ' + cartella[-1],
        )
    time.sleep(30)