
import psutil
import time
import threading


class ResourceMonitor:
    def __init__(self, interval=0.5):
        self.interval = interval
        self.running = False
        self.thread = None
        self.samples = []

    def _monitor(self):
        while self.running:
            memory = psutil.virtual_memory()

            sample = {
                "timestamp": time.time(),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "ram_percent": memory.percent,
                "ram_used_mb": memory.used / (1024 ** 2),
                "ram_available_mb": memory.available / (1024 ** 2)
            }

            self.samples.append(sample)
            time.sleep(self.interval)

    def start(self):
        self.samples = []
        psutil.cpu_percent(interval=None)
        self.running = True

        self.thread = threading.Thread(
            target=self._monitor,
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        return self.get_summary()

    def get_summary(self):
        if not self.samples:
            return {
                "cpu_avg_percent": 0,
                "cpu_max_percent": 0,
                "ram_avg_percent": 0,
                "ram_max_percent": 0,
                "ram_max_mb": 0
            }

        return {
            "cpu_avg_percent": round(
                sum(s["cpu_percent"] for s in self.samples)
                / len(self.samples), 2
            ),
            "cpu_max_percent": round(
                max(s["cpu_percent"] for s in self.samples), 2
            ),
            "ram_avg_percent": round(
                sum(s["ram_percent"] for s in self.samples)
                / len(self.samples), 2
            ),
            "ram_max_percent": round(
                max(s["ram_percent"] for s in self.samples), 2
            ),
            "ram_max_mb": round(
                max(s["ram_used_mb"] for s in self.samples), 2
            )
        }
