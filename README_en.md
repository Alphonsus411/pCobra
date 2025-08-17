# Cobra Project
[![Codecov](https://codecov.io/gh/Alphonsus411/pCobra/branch/work/graph/badge.svg)](https://codecov.io/gh/Alphonsus411/pCobra/branch/work)
[![Stable release](https://img.shields.io/github/v/release/Alphonsus411/pCobra?label=stable)](https://github.com/Alphonsus411/pCobra/releases/latest)

Version 10.0.9

Cobra is a programming language designed in Spanish, aimed at creating tools, simulations and analyses in fields such as biology, computing and astrophysics. This project includes a lexer, parser and transpilers to Python, JavaScript, assembly, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab, Mojo, LaTeX, C and WebAssembly, allowing greater versatility when running and deploying Cobra code.

## Table of Contents

- Project Description
- Installation
- Project Structure
- Main Features
- Usage
- Tokens and lexical rules
- Usage Example
- Tests
- Generate documentation
- CodeQL analysis
- [CobraHub](frontend/docs/cobrahub.rst)
- Milestones and Roadmap
- Contributions
- [Contribution Guide](CONTRIBUTING.md)
- [Propose extensions](frontend/docs/rfc_plugins.rst)
- VS Code extension
- [Community](docs/comunidad.md)
- License
- [Cobra Manual](MANUAL_COBRA.md)
- [Cobra Manual in reStructuredText](docs/MANUAL_COBRA.rst)
- [Cobra Manual in PDF](https://alphonsus411.github.io/pCobra/proyectocobra.pdf)
- [Basic guide](docs/guia_basica.md)
- [Technical specification](docs/especificacion_tecnica.md)
- [Cheatsheet](docs/cheatsheet.tex) – compile it to PDF with LaTeX
- [Real use cases](docs/casos_reales.md)
- [Node sandbox limitations](docs/limitaciones_node_sandbox.md)
- Example notebooks and real cases
- Try Cobra online
- [Changelog](CHANGELOG.md)

## Examples

Demo projects are available in [cobra-ejemplos](https://github.com/Alphonsus411/pCobra/tree/work/examples). This repository includes basic examples in the `examples/` folder, for instance `examples/funciones_principales.co` which shows conditionals, loops and function definitions in Cobra. For interactive examples check the notebooks in `notebooks/casos_reales/`.

### Advanced examples

Inside [examples/avanzados/](examples/avanzados/) you can find programs that delve into Cobra with exercises of control flow, recursive functions and class interaction. Each topic has its own folder:

- [examples/avanzados/control_flujo/](examples/avanzados/control_flujo/)
- [examples/avanzados/funciones/](examples/avanzados/funciones/)
- [examples/avanzados/clases/](examples/avanzados/clases/)

## Example notebooks

The `notebooks/` folder includes `ejemplo_basico.ipynb` with a basic example of using Cobra. The notebooks in `notebooks/casos_reales/` show how to run the advanced examples. To open it run:

```bash
cobra jupyter --notebook notebooks/ejemplo_basico.ipynb
```
If you omit the ``--notebook`` argument, Jupyter Notebook opens normally and you can choose the file from the web interface.

## Try Cobra online

You can experiment with Cobra directly in your browser:

- [Replit](https://replit.com/github/Alphonsus411/pCobra)
- [Binder](https://mybinder.org/v2/gh/Alphonsus411/pCobra/HEAD?labpath=notebooks/playground.ipynb)
- [GitHub Codespaces](https://codespaces.new/Alphonsus411/pCobra)

## Project Description

Cobra is designed to make programming in Spanish easier, allowing developers to use a more accessible language. Through its lexer, parser and transpilers, Cobra can analyze, execute and convert code to other languages, providing support for variables, functions, control structures and data structures such as lists, dictionaries and classes. For a step-by-step tutorial check the [Cobra Manual](docs/MANUAL_COBRA.rst). The full language specification is available in [SPEC_COBRA.md](SPEC_COBRA.md).

## Installation

To install the project, follow these steps:

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Alphonsus411/pCobra.git
   ```

2. Enter the project directory:

```bash
cd pCobra
```

If you prefer to automate the process, run:

```bash
./install.sh            # install from PyPI
./install.sh --dev      # install in editable mode
```

3. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # Unix
.\.venv\Scripts\activate  # Windows
```

4. Install the project dependencies using the provided script:

```bash
./scripts/install_dev.sh
```

   This will install both runtime and development requirements needed for running the tests.

5. Install the package in editable mode to use the CLI and obtain the dependencies declared in ``pyproject.toml``:

```bash
pip install -e .
```

Optionally, you may run ``pip install -e .[dev]`` to include the development extras.

6. Copy ``.env.example`` to ``.env`` and customize the paths or keys if necessary. These variables will be loaded automatically thanks to ``python-dotenv``:

```bash
cp .env.example .env
# Edit .env with your favorite editor
```

7. Run a test program to verify the installation:

```bash
echo "imprimir('Hola Cobra')" > hola.co
cobra ejecutar hola.co
```

### PYTHONPATH and PyCharm

For the imports `from src...` to work from the console and PyCharm, add the directory `src` to `PYTHONPATH` or install the package in editable mode with `pip install -e .`:

```bash
export PYTHONPATH=$PWD/src
# or
pip install -e .
```

In PyCharm mark the folder `src` as *Sources Root* so that the imports resolve correctly.
You can verify the configuration by running in the console:

```bash
PYTHONPATH=$PWD/src python -c "from src.core.main import main; main()"
```

### Installation with pipx

[pipx](https://pypa.github.io/pipx/) is a tool to install and run Python applications in isolation and requires Python 3.9 or higher. To install Cobra with pipx run:

```bash
pipx install cobra-lenguaje
```

If you prefer to install Cobra directly from PyPI without using `pipx`, run:

```bash
pip install cobra-lenguaje
```

## Build the Docker image

You can create the image using the script `docker/scripts/build.sh` or the CLI subcommand:

```bash
cobra contenedor --tag cobra
```

This internally runs ``docker build`` and generates an image called `cobra` in your Docker system.

## Binary downloads

Precompiled executables for Cobra are published in the repository's [Releases](https://github.com/Alphonsus411/pCobra/releases) section.

| Version | Platform | Link |
| --- | --- | --- |
| 10.0.9 | Linux x86_64 | [cobra-linux](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.9/cobra-linux) |
| 10.0.9 | Windows x86_64 | [cobra.exe](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.9/cobra.exe) |
| 10.0.9 | macOS arm64 | [cobra-macos](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.9/cobra-macos) |

To verify the integrity of the downloaded file, compute its SHA256 hash and compare it with the published value:

```bash
sha256sum cobra-linux
```

On Windows use:

```powershell
CertUtil -hashfile cobra.exe SHA256
```

Creating a `vX.Y.Z` tag on GitHub triggers automatic publication to PyPI and updates the Docker image.

If you prefer to generate the executable manually run from the repository root on your system (Windows, macOS or Linux):

```bash
pip install pyinstaller
cobra empaquetar --output dist
```
The binary name can be adjusted with `--name`. You can also use your own `.spec` file or add additional data via ``--spec`` and ``--add-data``:

```bash
cobra empaquetar --spec build/cobra.spec \
  --add-data "all-bytes.dat;all-bytes.dat" --output dist
```

## Build an executable with PyInstaller

If you want to compile Cobra manually follow these steps:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use .\\.venv\\Scripts\\activate
```

Install the published package and PyInstaller:

```bash
pip install cobra-lenguaje
pip install pyinstaller
```

Generate the binary with:

```bash
pyinstaller --onefile src/cli/cli.py -n cobra
```

You can also execute the new ``cobra-init`` script which loads the same
entry point automatically.

```bash
cobra-init
```

The executable will be placed inside the `dist/` directory.

# Project Structure

The project is organized into the following folders and modules:

- `src/`: Contains the Python logic of the project.
- `frontend/docs/` and `frontend/build/`: Folders where the documentation is generated and stored. The file `frontend/docs/arquitectura.rst` describes the internal structure of the language.
- `src/tests/`: Unit tests to ensure correct behaviour of the code.
- `README.md`: Project documentation.
- `requirements.txt`: Lists the project dependencies.
- `pyproject.toml`: Also defines dependencies in the ``project.dependencies`` and ``project.optional-dependencies`` sections.

# Main Features

- Lexer and Parser: Implementation of a lexer to tokenize the source code and a parser to build an abstract syntax tree (AST).
- Transpilers to Python, JavaScript, assembly, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab, Mojo, LaTeX, C and WebAssembly: Cobra can convert code to these languages, facilitating integration with external applications.
- Support for advanced structures: declaration of variables, functions, classes, lists and dictionaries, as well as loops and conditionals.
- Native modules with I/O functions, math utilities and data structures ready to use from Cobra.
- Runtime package installation via the `usar` instruction.
- Error handling: the system captures and reports syntax errors, easing debugging.
- Visualization and debugging: detailed output of tokens, AST and syntax errors for simpler development.
- Performance decorators: the ``smooth-criminal`` library offers functions such as ``optimizar`` and ``perfilar`` to improve and measure Python code executed from Cobra.
- Benchmarking: full performance measurement examples are available in `frontend/docs/benchmarking.rst`.
- Code and documentation examples: practical examples illustrating the lexer, parser and transpilers.
- Advanced examples: see `frontend/docs/ejemplos_avanzados.rst` to learn about classes, threads and error handling.
- Unicode identifiers: you can name variables and functions using characters like `á`, `ñ` or `Ω` for greater flexibility.

## Performance

Recent benchmarks were run with `scripts/benchmarks/compare_backends.py` to compare several backends. The approximate time was **0.68 s** for Cobra and Python, **0.07 s** for JavaScript and **0.04 s** for Rust, without significant memory usage.

Run the script with:

```bash
python scripts/benchmarks/compare_backends.py --output bench_results.json
```

The file [bench_results.json](bench_results.json) is saved in the current directory and can be analyzed with the notebook [notebooks/benchmarks_resultados.ipynb](notebooks/benchmarks_resultados.ipynb).

To compare thread performance run `cobra benchthreads`:

```bash
cobra benchthreads --output threads.json
```

The result contains three entries (sequential, cli_hilos and kernel_hilos) with the times and CPU usage.

# Usage

To run the project directly from the repository you can use the `run.sh` script. It loads the variables defined in `.env` if that file exists and then calls `python -m src.main` passing all received arguments. Use it as follows:

```bash
./run.sh [options]
```

For advanced options of safe mode see `frontend/docs/modo_seguro.rst`. Performance measurement examples are available in `frontend/docs/benchmarking.rst`.

To run unit tests use pytest:

```bash
PYTHONPATH=$PWD pytest src/tests --cov=src --cov-report=term-missing \
  --cov-fail-under=95
```

You can also run specific suites located in `src/tests`:

```bash
python -m tests.suite_cli           # CLI tests only
python -m tests.suite_core          # Lexer, parser and interpreter tests
python -m tests.suite_transpiladores  # Transpiler tests
```

## Tokens and lexical rules

The lexer converts code into tokens according to the regular expressions defined in `lexer.py`. The following table describes all available tokens:

| Token | Description |
|-------|-------------|
| DIVIDIR | Keyword or instruction "dividir" |
| MULTIPLICAR | Keyword or instruction "multiplicar" |
| CLASE | Keyword "clase" |
| DICCIONARIO | Keyword "diccionario" |
| LISTA | Keyword "lista" |
| RBRACE | Symbol "}" |
| DEF | Keyword "def" |
| IN | Keyword "in" |
| LBRACE | Symbol "{" |
| FOR | Keyword "for" |
| DOSPUNTOS | Symbol ":" |
| VAR | Keyword "var" |
| FUNC | Keyword "func" or "definir" |
| SI | Keyword "si" |
| SINO | Keyword "sino" |
| MIENTRAS | Keyword "mientras" |
| PARA | Keyword "para" |
| IMPORT | Keyword "import" |
| USAR | Keyword "usar" |
| MACRO | Keyword "macro" |
| HOLOBIT | Keyword "holobit" |
| PROYECTAR | Keyword "proyectar" |
| TRANSFORMAR | Keyword "transformar" |
| GRAFICAR | Keyword "graficar" |
| TRY | Keyword "try" or "intentar" |
| CATCH | Keyword "catch" or "capturar" |
| THROW | Keyword "throw" or "lanzar" |
| ENTERO | Integer number |
| FLOTANTE | Decimal number |
| CADENA | String literal |
| BOOLEANO | Boolean literal |
| IDENTIFICADOR | Variable or function name |
| ASIGNAR | Symbol "=" |
| SUMA | Operator "+" |
| RESTA | Operator "-" |
| MULT | Operator "*" |
| DIV | Operator "/" |
| MAYORQUE | Operator ">" |
| MENORQUE | Operator "<" |
| MAYORIGUAL | Operator ">=" |
| MENORIGUAL | Operator "<=" |
| IGUAL | Operator "==" |
| DIFERENTE | Operator "!=" |
| AND | Logical operator "&&" |
| OR | Logical operator "||" |
| NOT | Operator "!" |
| MOD | Operator "%" |
| LPAREN | Symbol "(" |
| RPAREN | Symbol ")" |
| LBRACKET | Symbol "[" |
| RBRACKET | Symbol "]" |
| COMA | Symbol "," |
| RETORNO | Keyword "retorno" |
| FIN | Keyword "fin" |
| EOF | End of file |
| IMPRIMIR | Keyword "imprimir" |
| HILO | Keyword "hilo" |
| ASINCRONICO | Keyword "asincronico" |
| DECORADOR | Symbol "@" |
| YIELD | Keyword "yield" |
| ESPERAR | Keyword "esperar" |
| ROMPER | Keyword "romper" |
| CONTINUAR | Keyword "continuar" |
| PASAR | Keyword "pasar" |
| AFIRMAR | Keyword "afirmar" |
| ELIMINAR | Keyword "eliminar" |
| GLOBAL | Keyword "global" |
| NOLOCAL | Keyword "nolocal" |
| LAMBDA | Keyword "lambda" |
| CON | Keyword "con" |
| FINALMENTE | Keyword "finalmente" |
| DESDE | Keyword "desde" |
| COMO | Keyword "como" |
| SWITCH | Keyword "switch" or "segun" |
| CASE | Keyword "case" or "caso" |

The regular expressions are grouped in `especificacion_tokens` and processed in order to find matches. Keywords use patterns like `\bvar\b` or `\bfunc\b`, numbers use `\d+` or `\d+\.\d+` and strings are detected with `"[^\"]*"` or `'[^']*'`. Identifiers allow Unicode characters via `[^\W\d_][\w]*`. Operators and symbols use direct patterns like `==`, `&&` or `\(`. Before analysis, line and block comments are removed with `re.sub`.

## Module loading example

You can split the code into several files and load them with `import`:

```cobra
# modulo.co
var saludo = 'Hola desde módulo'

# programa.co
import 'modulo.co'
imprimir(saludo)
```

When running `programa.co`, `modulo.co` is processed first and then `Hola desde módulo` is printed.

## `usar` statement for dynamic dependencies

The statement `usar "paquete"` tries to import a Python module. If the package is not available, Cobra will run `pip install paquete` to install it and then load it at runtime. The module is registered in the environment under the same name for later use. To restrict which dependencies can be installed use the variable `USAR_WHITELIST` defined in `src/cobra/usar_loader.py`.

## Module mapping file

Transpilers look up `cobra.mod` to resolve imports. This file follows a simple YAML schema where each key is the path of the Cobra module and its values indicate the paths of the generated files.

Example format:

```yaml
modulo.co:
  version: "1.0.0"
  python: modulo.py
  js: modulo.js
```

If an entry is not found, the transpiler will load the file indicated in the `import` instruction. To add or modify routes just edit `cobra.mod` and run the tests again.

## Calling the transpiler

The folder [`src/cobra/transpilers/transpiler`](src/cobra/transpilers/transpiler) contains the implementation of the transpilers to Python, JavaScript, assembly, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab, Mojo, LaTeX, C and WebAssembly. Once the dependencies are installed you can call the transpiler from your own script like this:

```python
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.core import Parser

codigo = "imprimir('hola')"
parser = Parser(codigo)
arbol = parser.parsear()
transpiler = TranspiladorPython()
resultado = transpiler.generate_code(arbol)
print(resultado)
```

For other languages you can invoke the additional transpilers like this:

```python
from cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
from cobra.transpilers.transpiler.to_pascal import TranspiladorPascal
from cobra.transpilers.transpiler.to_ruby import TranspiladorRuby
from cobra.transpilers.transpiler.to_php import TranspiladorPHP
from cobra.transpilers.transpiler.to_perl import TranspiladorPerl
from cobra.transpilers.transpiler.to_visualbasic import TranspiladorVisualBasic
from cobra.transpilers.transpiler.to_kotlin import TranspiladorKotlin
from cobra.transpilers.transpiler.to_swift import TranspiladorSwift
from cobra.transpilers.transpiler.to_matlab import TranspiladorMatlab
from cobra.transpilers.transpiler.to_mojo import TranspiladorMojo
from cobra.transpilers.transpiler.to_latex import TranspiladorLatex

codigo_cobol = TranspiladorCOBOL().generate_code(arbol)
codigo_fortran = TranspiladorFortran().generate_code(arbol)
codigo_pascal = TranspiladorPascal().generate_code(arbol)
codigo_ruby = TranspiladorRuby().generate_code(arbol)
codigo_php = TranspiladorPHP().generate_code(arbol)
codigo_perl = TranspiladorPerl().generate_code(arbol)
codigo_visualbasic = TranspiladorVisualBasic().generate_code(arbol)
codigo_kotlin = TranspiladorKotlin().generate_code(arbol)
codigo_swift = TranspiladorSwift().generate_code(arbol)
codigo_matlab = TranspiladorMatlab().generate_code(arbol)
codigo_mojo = TranspiladorMojo().generate_code(arbol)
codigo_latex = TranspiladorLatex().generate_code(arbol)
```

After obtaining the code with ``generate_code`` you can save it using ``save_file``:

```python
transpiler.save_file("salida.py")
```

This requires the package to be installed in editable mode along with all dependencies from `requirements.txt`. If you need to generate files from Cobra modules check the mapping defined in `cobra.mod`.

## Concurrency example

It is possible to launch functions in threads with the keyword `hilo`:

```cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
```

Generating code for these functions creates `asyncio.create_task` calls in Python and `Promise.resolve().then` in JavaScript.

## CLI usage

Once the package is installed, the `cobra` tool offers several subcommands. The README in Spanish contains a complete list of commands and examples.

The CLI also includes a safe mode (`--seguro`), a sandbox option (`--sandbox`), support for multiple languages via `--lang` and the ability to generate documentation, packages and executables. See the Spanish README for detailed examples.

## Tests and development

Tests are located in the `src/tests/` folder and use pytest. First install the dependencies with `./scripts/install_dev.sh` and then run all tests with:

```bash
PYTHONPATH=$PWD pytest
```

There are also instructions for running linters (`make lint`), type checking (`make typecheck`) and searching for secrets (`make secrets`).

## Contributions and community

Contributions are welcome! Check [CONTRIBUTING.md](CONTRIBUTING.md) for style conventions and pull request guidelines. Join our community via Discord, Telegram or Twitter to get involved.
## VS Code extension

The extension is located in [`frontend/vscode`](frontend/vscode). Install the dependencies with `npm install`. Press `F5` in VS Code to launch an Extension Development Host or run `vsce package` to create the `.vsix` file. See [frontend/vscode/README.md](frontend/vscode/README.md) for more information.


## License

This project is released under the [MIT License](LICENSE).
