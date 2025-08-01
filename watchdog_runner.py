from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess

class VaultChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory: return
        print(f"Vault updated: {event.src_path}")
        subprocess.run(["python", "embedder.py"])

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(VaultChangeHandler(), path="../vault", recursive=True)
    observer.start()
    print("Watching vault for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
