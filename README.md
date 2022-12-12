# Midjourney Archiver

This is a command line tool to download/archive your whole
Midjourney history (images + full prompts).

### Alpha software warning

This is just a couple of Python scripts written in an afternoon to scratch my own itch. Here be dragons.

## Installation

1. Make sure you have Python 3.9 or newer.
2. Download [the ZIP file](./archive/refs/heads/main.zip) and place it in a folder. In this folder, the tool will create an `mj-archive` subfolder, where it will place the downloaded items. 
3. Unzip the downloaded ZIP file.

## Usage

### Mac or Linux

Run `mj-download.sh` and follow the instructions. These instructions are for a Chromium-based browser like Chrome or Edge. 

1. Open https://www.midjourney.com/app/
2. Sign in
3. Open the browser developer tools: View > Developer > Developer Tools
4. Go to Network > Fetch/XHR
5. Find an entry like `?user_id=NNNNNNNN&public=false`
6. Copy the `NNNNNNNN` value and paste it when asked, then press Enter.
7. Go to Application > Cookies > https://www.midjourney.com
8. Find the entry `__Secure-next-auth.session-token`
9. Copy its value and paste it when asked, then press Enter. 

### On Windows, or alternative on other platforms

1. Get the `user_id` and `__Secure-next-auth.session-token` values as described above.
2. Assign the value of `user_id` to the `MIDJOURNEY_USER_ID` environment variable.
3. Assign the value of `__Secure-next-auth.session-token` to the `MIDJOURNEY_SESSION_TOKEN` environment variable.
4. Crawl your history and download each job's metadata  as JSON file and text file with prompt: `./mj-metadata-archiver.py`
5. Walk through that downloaded metadata archive and download the referenced images: `./mj-downloader.py`

## License

[MIT License](./LICENSE.txt)

