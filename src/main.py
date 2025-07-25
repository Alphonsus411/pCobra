from dotenv import load_dotenv

# Carga las variables de entorno antes de importar otros módulos
load_dotenv()

from src.core.main import main

if __name__ == "__main__":
    main()
