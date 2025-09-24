import pkgutil
import importlib
from util import logger
from colorama import Fore

__all__: list[str] = []

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    logger.log("API", f"Route {Fore.CYAN}{module_name}{Fore.RESET} loaded succesfully.")
    globals()[module_name] = module
    __all__.append(module_name)