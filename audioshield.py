import os
import time
import subprocess
import sqlite3
import shutil
from pathlib import Path

# Configuración dinámica para cualquier usuario Linux
HOME = str(Path.home())
BASE_DIR = os.path.join(HOME, ".local/share/audioshield")
UPLOADS = os.path.join(BASE_DIR, "watch_folder")
DESTINO = os.path.join(HOME, "Desktop/Music_Cleaned")
DB_PATH = os.path.join(BASE_DIR, "history.db")

def setup():
    for folder in [UPLOADS, DESTINO, os.path.dirname(DB_PATH)]:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, name TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.close()

def get_clean_name(path):
    try:
        cmd = ["exiftool", "-s3", "-Artist", "-Title", path]
        res = subprocess.check_output(cmd).decode('utf-8').splitlines()
        if len(res) >= 2:
            return f"{res[0]} - {res[1]}".replace("/", "-")
    except:
        return None
    return None

def start_engine():
    setup()
    print(f"[*] AudioShield Lite activo. Vigilando: {UPLOADS}")
    while True:
        if os.path.exists(UPLOADS):
            files = [f for f in os.listdir(UPLOADS) if f.lower().endswith(('.mp3', '.ogg', '.wav', '.flac'))]
            for f in files:
                origin = os.path.join(UPLOADS, f)
                tag_name = get_clean_name(origin)
                ext = os.path.splitext(f)[1]
                final_name = f"{tag_name}{ext}" if tag_name else f
                target = os.path.join(DESTINO, final_name)
                try:
                    shutil.move(origin, target)
                    subprocess.run(["exiftool", "-all=", "-overwrite_original", target], capture_output=True)
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO events (name) VALUES (?)", (final_name,))
                    conn.commit()
                    conn.close()
                    print(f"[OK] Procesado y Limpiado: {final_name}")
                except Exception as e:
                    print(f"[Error] {e}")
        time.sleep(2)

if __name__ == "__main__":
    start_engine()
