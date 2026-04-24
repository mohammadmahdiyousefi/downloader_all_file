import os
import sys
import requests
from urllib.parse import unquote, urlparse
from pathlib import Path

def get_filename_from_url(url, response=None):
    # اول سعی می‌کنیم اسم فایل رو از هدر Content-Disposition بگیریم
    if response and 'Content-Disposition' in response.headers:
        import re
        content_disposition = response.headers['Content-Disposition']
        fname = re.findall("filename\*=UTF-8''(.+)", content_disposition)
        if not fname:
            fname = re.findall("filename=(.+)", content_disposition)
        if fname:
            return unquote(fname[0].strip('"\''))

    # در غیر این صورت از آخر URL استفاده کن
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded_file'
    return filename

def download_file(url, folder):
    # ساخت پوشه اگر وجود نداشت
    Path(folder).mkdir(parents=True, exist_ok=True)

    try:
        # درخواست GET با استریم برای فایل‌های بزرگ
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            filename = get_filename_from_url(url, r)
            filepath = os.path.join(folder, filename)

            # اگه فایل تکراری بود یه شماره بهش اضافه می‌کنیم
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join(folder, f"{name}_{counter}{ext}")
                counter += 1

            print(f"در حال دانلود: {url} -> {filepath}")
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("دانلود کامل شد.")
            return filepath
    except Exception as e:
        print(f"خطا در دانلود: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download.py <URL> [folder_name]")
        sys.exit(1)

    url = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else "downloads"
    download_file(url, folder)
