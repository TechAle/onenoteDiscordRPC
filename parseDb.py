import os
import tool
import sqlite3

cartella = "psicologia"
file = "Vino"
dom_dir = os.path.expanduser("~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                             "Support/Microsoft User Data/OneNote/15.0/FullTextSearchIndex/")

allDicts = tool.getFiles(".db", dom_dir)
checkDb = None
for currentDict in allDicts:
    conn = sqlite3.connect(str(currentDict.absolute()))
    c = conn.cursor()
    c.execute("SELECT Title FROM `Entities` WHERE `Type` = 4;")
    if (name := c.fetchone()) is not None and name[0] == file:
        checkDb = currentDict
        break
    conn.close()

if checkDb is not None:
    padreGOID = c.execute("SELECT GOID FROM 'Entities' WHERE `type` = 4")

'''
    Prendo padre GOID = {1A149CFA-707B-7441-B955-DD06E93F5E7B}{48}
    Cerco tutti quelli con ParentGOID = {1A149CFA-707B-7441-B955-DD06E93F5E7B}{48} e con
        GrantparentGOIDs = null
    Poi da questo, nasce il casino.
        ParenGOID deve rimanere lo stesso di sopra
        GrandparentGOIDs invece deve essere uguale a
            Il GOID di quelli di prima 
            Uno concatenati agli altri
            Es. Supponiamo 2 semestre -> APS -> lol -> nuovo
            il grandparent di nuovo è 2 semestre + APS + lol
    
'''