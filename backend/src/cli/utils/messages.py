RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


def mostrar_error(msg):
    """Muestra un mensaje de error en rojo."""
    print(f"{RED}Error: {msg}{RESET}")


def mostrar_info(msg):
    """Muestra un mensaje informativo en verde por stdout."""
    print(f"{GREEN}{msg}{RESET}")
