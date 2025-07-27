from dotenv import load_dotenv

# Carga variables de entorno desde un archivo .env si existe
load_dotenv()

from cobra.cli.cli import main as cli_main


def main(argv=None):
    """Entrada principal que delega en la CLI."""
    return cli_main(argv)


if __name__ == "__main__":
    import sys

    sys.exit(main())

