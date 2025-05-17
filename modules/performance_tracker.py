import time


class PerformanceTracker:
    def __init__(self, logger):
        self.logger = logger
        self.timings = {}

    def start(self, section):
        self.timings[section] = time.time()
        self.logger.info(f"⏱️ Початок вимірювання часу для {section}")

    def stop(self, section):
        if section in self.timings:
            duration = time.time() - self.timings[section]
            self.logger.info(f"⏲️ Завершено вимірювання часу для {section}: {duration:.2f} сек.")
        else:
            self.logger.warning(f"⚠️ Спроба зупинити неактивний таймер для {section}.")

    def generate_report(self):
        report = []
        for section, start_time in self.timings.items():
            duration = time.time() - start_time
            report.append(f"🕒 {section} - {duration:.2f} сек.")
        return report
