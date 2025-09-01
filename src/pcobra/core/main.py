"""Punto de entrada mínimo para ejecutar un saludo de prueba."""

from dotenv import load_dotenv

# Carga variables de entorno desde un archivo .env si existe
load_dotenv()


def main():
    """Imprime un mensaje de bienvenida."""
    print("¡Hola desde Cobra!")


if __name__ == '__main__':
    main()
