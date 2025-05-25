import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class GameReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_game()

    def start_game(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(['python', 'pacman.py'])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}")
            self.start_game()

def main():
    path = '.'
    event_handler = GameReloader()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()

if __name__ == "__main__":
    main() 