from setuptools import setup

setup(
    name='ejemplo-plugin-cobra',
    version='1.0.0',
    description='Plugin de ejemplo para Cobra',
    author='Tu Nombre',
    author_email='tu@email.com',
    url='https://github.com/usuario/ejemplo-plugin-cobra',
    py_modules=['saludo_plugin', 'md2cobra_plugin', 'hora_plugin', 'transpiler_demo'],
    install_requires=[
        'cobra-core>=1.0.0',  # Ajusta según la versión mínima requerida
    ],
    entry_points={
        'cobra.plugins': [
            'saludo = saludo_plugin:SaludoCommand',
            'md2cobra = md2cobra_plugin:MarkdownToCobraCommand',
            'hora = hora_plugin:HoraCommand',
        ],
        'cobra.transpilers': [
            'demo = transpiler_demo:TranspiladorDemo',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)