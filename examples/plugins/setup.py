from setuptools import setup

setup(
    name='ejemplo-plugin-cobra',
    version='1.0',
    py_modules=['saludo_plugin'],
    entry_points={
        'cobra.plugins': [
            'saludo = saludo_plugin:SaludoCommand',
        ],
    },
)
