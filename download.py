import os
import sys
import requests
from urllib.parse import unquote, urlparse
from pathlib import Path

def get_filename_from_url(url, response=None):
    if response and 'Content-Disposition' in response.headers:
        import re
        cd = response.headers['Content-Disposition']
        fname = re.findall("filename\*=UTF-8''(.+)", cd)
        if not fname:
            fname = re.findall("filename=(.+)", cd)
        if fname:
            return unquote(fname[0].strip('"\''))
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)
    if not filename or filename == '/':
        filename = 'downloaded_file'
    return filename

def download_file(url, folder):
    Path(folder).mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, stream=True, timeout=60, headers={'User-Agent': 'Mozilla/5.0'}) as r:
            r.raise_for_status()
            filename = get_filename_from_url(url, r)
            filepath = os.path.join(folder, filename)
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join(folder, f"{name}_{counter}{ext}")
                counter += 1
            print(f"Downloading to {filepath}")
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete")
            return filepath
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download.py <URL> [folder]")
        sys.exit(1)
    url = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else "downloads"
    download_file(url, folder)
