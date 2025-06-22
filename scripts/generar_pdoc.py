import subprocess
from pathlib import Path

OUTPUT_DIR = Path('frontend/build/pdoc')


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'pdoc',
        'backend/src',
        '--output-dir', str(OUTPUT_DIR)
    ], check=True)


if __name__ == '__main__':
    main()
