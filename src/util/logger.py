from colorama import Fore, Style, init
from datetime import datetime

# Inicializa colorama (necesario para Windows)
init(autoreset=True)

class Logger:
    def __init__(self, name="App"):
        self.name = name

    def _log(self, level, color, message):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{time}] [{self.name}] [{level}] {Style.RESET_ALL}{message}")

    def info(self, message):
        self._log("*", Fore.CYAN, message)

    def warning(self, message):
        self._log("!", Fore.YELLOW, message)

    def error(self, message):
        self._log("!!", Fore.RED, message)

    def success(self, message):
        self._log("*", Fore.GREEN, message)

    def debug(self, message):
        self._log("**", Fore.MAGENTA, message)

logger = Logger("Wordbomb")