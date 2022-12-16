# Midjourney Archiver

This is a command line tool to download/archive your whole
Midjourney history (images + full prompts).

> **Warning**
> Alpha software: this is just a couple of Python scripts written in an afternoon to scratch my own itch.
> Here be dragons.

## Set up

- Make sure you have [Python](https://www.python.org/) to execute the scripts.
  Preferably Python 3.9 or higher, although lower versions might also work.
- Preferably (and if you are familiar with that): work in a virtual environment.
  For example using a tool like [venv](https://docs.python.org/3/library/venv.html), virtualenv, conda, ...
- Install the requirements, e.g. using  `python -m pip install -r requirements.txt`
- Get the Python scripts (`mj-metadata-archiver.py` and `mj-downloader.py`) from this repository:
  for example, use `git clone`
  or download it as [a ZIP file](archive/refs/heads/main.zip).

## Usage

Usage is a multistep process.
It starts with an annoying part to obtain your user_id and a working session token.
But when that works out, the remaining parts should work smoothly and automatically.


### 1. Preparation (get credentials)

The `mj-metadata-archiver.py` script downloads your history
by acting as the Midjourney web app running in your browser.
To make that possible, it needs your user id
and an authentication token from your browser cookies:

1. Browse to https://www.midjourney.com/app/ and log in.
2. Open the browser developer tools:
   - in Firefox: Tools Menu > Browser Tools > Web Developer Tools
   - in Chrome: View Menu > Developer > Developer Tools
   - or quick trick in most browsers: right click somewhere on the page and select "Inspect"
3. Go to the "Network" tab in the dev tools.
4. Enter "userId" in the filter widget to find URLs that contain your user id.
   You might have to scroll the Midjourney home page a bit to trigger these requests.
5. Extract your user id from such a URL.
   For example, if the URL is something like
   `https://www.midjourney.com/.../recent-jobs/?...pleted&userId=386228643&toDa....`,
   extract the number between `userId=` and the next `&`,
   which gives `386228643` in this example.
6. Obtain the value of the `__Secure-next-auth.session-token` cookie:

   - in Firefox dev tools: go to Storage > Cookies > `https://www.midjourney.com`
   - in Chrome dev tools: go to Application tab > Cookies > `https://www.midjourney.com`

   Find `__Secure-next-auth.session-token` in the table
   and copy the token value (it's a long, gibberish string of thousands of characters).

Keep this user id number and long session token string handy for the next steps.

### 2. Download metadata history

Run the metadata download script
to crawl your history and download each job's metadata
as JSON file and text file with prompt:

    python mj-metadata-archiver.py

When running it like this, the script will ask for your user id
and session token interactively.
Instead, you can also first define environment variables
to pass your credentials.
For example

    export MIDJOURNEY_USER_ID=386228643
    export MIDJOURNEY_SESSION_TOKEN=yfcQufiDtGKQIw1uY9ONFlx3FY....
    python mj-metadata-archiver.py

When everything goes right, a folder new `mj-archive` will be created,
containing your Midjourney job metadata history as JSON and text files,
organised per date.

### 3. Download referenced images

Walk through the downloaded metadata archive
and download the full referenced images of (upscale) jobs:

      python mj-downloader.py


## License

[MIT License](./LICENSE.txt)
