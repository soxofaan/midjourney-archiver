#!/usr/bin/env bash
echo "These instructions are for a Chromium-based browser"
echo "like Chrome or Edge:"
echo "1. Open https://www.midjourney.com/app/"
echo "2. Sign in"
echo "3. Open the developer tools (F12)"
echo "4. Go to Network > Fetch/XHR"
echo "5. Find an entry like ?user_id=NNNNNNNN&public=false"
echo "6. Copy the NNNNNNNN value and paste it below, then press Enter:"
read MIDJOURNEY_USER_ID
echo "7. Go to Application > Cookies > https://www.midjourney.com"
echo "8. Find the entry __Secure-next-auth.session-token"
echo "9. Copy its value and paste it below, then press Enter:"
read MIDJOURNEY_SESSION_TOKEN 
./mj-metadata-archiver.py
./mj-downloader.py
