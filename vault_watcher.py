import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import os

LOG_PATH = "logs/vault_sync.log"

def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {message}\\n")

class VaultChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        write_log(f"🔁 Change detected: {event.src_path}")
        try:
            subprocess.run(["python", "scripts/auto_push_vault.py"], check=True)
            write_log("✅ Vault pushed to GitHub")
            subprocess.run(["python", "rag-backend/embedder.py"], check=True)
            write_log("✅ Vault re-embedded successfully")
        except subprocess.CalledProcessError as e:
            write_log(f"❌ Error during sync: {str(e)}")

if __name__ == "__main__":
    path_to_watch = "vault"
    write_log(f"👀 Starting Vault Watcher on: {path_to_watch}")
    observer = Observer()
    observer.schedule(VaultChangeHandler(), path=path_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
        write_log("🛑 Vault Watcher stopped.")
    observer.join()
