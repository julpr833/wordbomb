from colorama import init, Fore

# Initialize Colorama
init(autoreset=True)

def log(title: str, msg: str) -> None: 
    print(f"{Fore.YELLOW}[{title}]{Fore.RESET} {msg}")