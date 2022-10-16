# Midjourney Archiver

This is a command line tool to download/archive your whole
Midjourney history (images + full prompts).


**Alpha software warning**
This is just a couple of Python scripts 
written in an afternoon to scratch my own itch.
Here be dragons.


Two-step procedure:

- Step 0: 
  go to https://www.midjourney.com/app/, log in,
  and get your user id 
  and `__Secure-next-auth.session-token` cookie from
  the API requests in your browser's dev tools. 
  (Set respectively as `MIDJOURNEY_USER_ID` 
  and `MIDJOURNEY_SESSION_TOKEN` env vars)
- Step 1:
  Crawl your history and download each job's metadata 
  as JSON file and text file with prompt.

      ./mj-metadata-archiver.py

- Step 2:
  Walk through that downloaded metadata archive 
  and download the referenced images.

      ./mj-downloader.py

