# OneNote Discord RPC

This project, while it may seem simple, is far from it. I created this script with a lot of effort and frustration. It creates a Discord Rich Presence (RPC) for OneNote, displaying the current page you're working on and its path.

**Note:** This script is currently designed to work only on macOS. It might be possible to adapt it for Windows and Linux by changing the file paths.

## Installation

- **Tested on Python 3.12**
- Install the required dependencies by running:
  ```
  pip install -r requirements.txt
  ```
- Run the script:
  ```
  python main.py
  ```
- Enjoy!

## How It Works

### Understanding OneNote's Data Structure

To understand how the script works, let's first look at how OneNote manages its data on macOS.

All OneNote data on macOS is stored in:
```
~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application Support/
```

Within this directory, two folders are particularly important for our purposes:

1. **Microsoft User Data**: This folder contains local data, such as cache, backups, and the content of notebooks.
2. **Microsoft**: This folder contains various data, but most importantly, it holds the links to remote notebooks.

### Cache Files

OneNote's cache contains data that hasn't yet been uploaded to the cloud. All cache files are located in:
```
/Microsoft User Data/OneNote/15.0/cache
```

While it would be interesting to parse all cache files, it's beyond the scope of this project. Instead, I focused on one specific task: determining whether a cache file contains the title of a page.

After extensive analysis, I discovered a pattern: the title of one of the page versions follows this structure:
- `\x7a\x1d\x00\x14\x2c\x34\x00\x20\xb4\x1c\x00\x88`
- Followed by a variable number of bytes (usually between 10 and 50 in hexadecimal)
- Then `\x00\x00\x00`
- Followed by another variable number of bytes (usually 1 or 3-4 in hexadecimal)
- Then `\x00\x00\x00`
- Followed by `\x00` until the start of one of the versions of the title
- The title ends with `\x00`

Yes, it's a mess, but it's the only way I found after days of work to identify the current page being edited. When you edit a page, the corresponding cache file is updated, so I can determine the current page by checking the last modified cache file.

However, there's a catch: since the cache file contains one of the versions of the title, it might not always reflect the latest title. This is still an issue with the script. I assume that the "random bytes" before the title correlate with the version, but I haven't fully figured this out yet. For now, I don't consider it a major issue because the first version of the title is usually the one I stick with until the end. Additionally, after closing and reopening OneNote, the old versions are removed from the cache.

### Notebooks

Now that we have the name of the file being edited, we need to determine its path. Unfortunately, the cache files don't provide this information directly. There are some cache files that contain notebook information, but OneNote sometimes updates the caches of notebooks you're not actively working on. I have no idea why it does this, so my hours of work trying to understand the cache patterns went to waste.

Instead, I found another way to get the file path. Every time you modify a file, OneNote saves a record in a file indicating that the user updated the notebook. This file is located at:
```
Microsoft/Office/16.0/ResourceInfoCache/data.json
```

My assumption is that OneNote saves this information to update the remote notebook later. Using this file, we can extract the path of the file being edited.

But there's another problem: this file doesn't update while you're editing a page. It only updates after you switch to another page. This means that the path we get is for the last file you edited, not the current one. While this is frustrating, the root notebook information is still correct. So, we at least know which notebook you're working in.

There's still a minor issue: when you switch between notebooks, the notebook file might not immediately reflect the correct notebook. However, in practice, this isn't a big deal because it's rare to switch notebooks and stay on the "default page."

### Paths

Now that we have the file name and the notebook, we need to figure out the intermediate path. Luckily, OneNote stores all its content in a SQLite database located at:
```
~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application Support/Microsoft User Data/OneNote/15.0/FullTextSearchIndex/
```

From here, it's just a matter of running some SQL queries to retrieve the full path of the file. This part of the project was relatively straightforward compared to the rest.

## Conclusion

Please, do not dive into OneNote's cache files. I have suffered enough for all of us. If possible, consider converting your notes to Obsidian using some scripts and work with Obsidian instead. This project has convinced me to abandon OneNote once I'm done with university.