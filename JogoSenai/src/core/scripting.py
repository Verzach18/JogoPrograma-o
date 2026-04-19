import traceback
import threading
from config import *

class ScriptExecutor:
    def __init__(self, drone, progression):
        self.drone = drone
        self.progression = progression
        self.drone.progression = progression # Link for internal checks
        self.thread = None
        self.stop_event = threading.Event()
        self.globals = {
            "drone": self.drone,
            "Entities": Entities,
            "Direction": Direction,
            "print": self.drone.log
        }

    def stop(self):
        self.stop_event.set()
        self.drone.stop() # Signal drone to stop waiting
        if self.thread:
            self.thread.join(timeout=0.1)
        self.drone.log("Script Stopped")

    def execute(self, code: str):
        self.stop() # Stop any existing script
        self.stop_event.clear()
        self.drone.reset_sync()

        # Security/Progression Check
        if "while" in code or "for" in code:
            if not self.progression.can_use("loops"):
                self.drone.log("ERROR: Loops not unlocked!")
                return False
        
        if "if " in code:
            if not self.progression.can_use("if_statements"):
                self.drone.log("ERROR: Conditionals not unlocked!")
                return False

        if "def " in code:
            if not self.progression.can_use("functions"):
                self.drone.log("ERROR: Functions not unlocked!")
                return False

        def run_script():
            try:
                exec(code, self.globals.copy())
                self.drone.log("Script Finished")
            except Exception as e:
                if not self.stop_event.is_set():
                    msg = traceback.format_exc().splitlines()[-1]
                    self.drone.log(f"PYTHON ERROR: {msg}")

        self.thread = threading.Thread(target=run_script, daemon=True)
        self.thread.start()
        self.drone.log("Script Started")
        return True
