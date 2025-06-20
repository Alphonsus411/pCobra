from setuptools import setup, find_packages

setup(
    name='Cobra',
    version='0.1',
    author='Adolfo González Hernández',
    author_email='adolfogonzal@gmail.com',
    description='Un lenguaje de programación en español para simulaciones y más.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Alphonsus411/pCobra',  # Reemplaza con tu URL de GitHub
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pytest>=7.0',  # Requerimientos según requirements.txt
        'numpy>=1.22.0',
        'scipy>=1.7.0',
        'matplotlib>=3.5.0',
        'pandas>=1.3.0',
        'tensorflow>=2.6.0',
        'dask>=2021.09.0',
        'DEAP>=1.3.1',
        # Agrega más requisitos según sea necesario
    ],
    entry_points={
        'console_scripts': [
            'cobra=src.cli.cli:main',
        ],
    },

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
