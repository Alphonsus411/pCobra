from pCobra.cli import main as cli_main


def main() -> int:
    """Envoltorio para la función principal de la CLI de Cobra."""
    return cli_main()


if __name__ == "__main__":
    import sys

    sys.exit(main())
