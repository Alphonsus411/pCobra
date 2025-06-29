from setuptools import setup, find_packages

setup(
    name='cobra-lenguaje',
    version='5.4',
    author='Adolfo González Hernández',
    author_email='adolfogonzal@gmail.com',
    description='Un lenguaje de programación en español para simulaciones y más.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Alphonsus411/pCobra',  # Reemplaza con tu URL de GitHub
    license='MIT',
    packages=find_packages(where='backend/src', include=['*']),
    package_dir={'': 'backend/src'},
    include_package_data=True,
    keywords=['cobra', 'lenguaje', 'cli'],
    project_urls={
        'Documentation': 'https://github.com/Alphonsus411/pCobra#readme',
        'Source': 'https://github.com/Alphonsus411/pCobra',
    },
    install_requires=[
        'pytest>=7.0',  # Requerimientos según requirements.txt
        'numpy>=1.22.0',
        'scipy>=1.7.0',
        'matplotlib>=3.5.0',
        'pandas>=1.3.0',
        'tensorflow>=2.6.0',
        'dask>=2021.09.0',
        'DEAP>=1.3.1',
        'ipykernel>=6.0.0',
        'agix==0.8.3',
        'holobit-sdk',
        'smooth-criminal',
        # Agrega más requisitos según sea necesario
    ],
    tests_require=[
        'pytest-cov',
    ],
    entry_points={
        'console_scripts': [
            'cobra=src.cli.cli:main',
        ],
        'cobra.plugins': [
            # Se registrarán plugins externos aquí
        ],
    },

    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Spanish',
    ],
    python_requires='>=3.6',
)
