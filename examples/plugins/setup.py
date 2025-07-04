from setuptools import setup

setup(
    name="ejemplo-plugin-cobra",
    version="1.0",
    py_modules=["saludo_plugin", "md2cobra_plugin", "demo_transpiler"],
    entry_points={
        "cobra.plugins": [
            "saludo = saludo_plugin:SaludoCommand",
            "md2cobra = md2cobra_plugin:MarkdownToCobraCommand",
        ],
        "cobra.transpilers": [
            "demo = demo_transpiler:DemoTranspiler",
        ],
    },
)
