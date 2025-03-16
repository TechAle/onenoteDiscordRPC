import json
import os
from urllib.parse import unquote

data_dir = os.path.expanduser("~") + ("/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application "
                                      "Support/Microsoft/Office/16.0/ResourceInfoCache/data.json")

def getCartella():
    with open(data_dir, 'r') as file:
        data = json.load(file)

    # Trova l'URL con il LastAccessedAt più recente
    latest_entry = max(data["ResourceInfoCache"], key=lambda x: x["LastAccessedAt"])
    return unquote(latest_entry["Url"].replace("%5eL", "^").split("/")[5])

print(getCartella())