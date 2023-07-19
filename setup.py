from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

# https://pypi.org/project/mkdoxy/
setup(
    name='mkdoxy',
    version='1.1.5',
    description='MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets',
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords='mkdoxy, python, open-source, documentation, mkdocs, doxygen, multilanguage, code-snippets, code, snippets, documentation-generator',
    url='https://github.com/JakubAndrysek/MkDoxy',
    author='Jakub Andrýsek',
    author_email='email@kubaandrysek.cz',
    license='MIT',
    python_requires='>=3.9',

    project_urls={
        'Source': 'https://github.com/JakubAndrysek/MkDoxy',
        'Documentation': 'https://mkdoxy.kubaandrysek.cz/',
        'Tracker': 'https://github.com/JakubAndrysek/MkDoxy/issues',
        'Funding': 'https://github.com/sponsors/jakubandrysek',
    },

    install_requires=['mkdocs', 'ruamel.yaml'],
    extras_require={
        "dev": [
            "mkdocs-material==9.1.18",
            "Jinja2~=3.1.2",
            "ruamel.yaml~=0.17.32",
            "mkdocs-open-in-new-tab~=1.0.2",
            "pathlib~=1.0.1",
            "path~=16.7.1",
            ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    package_data={'mkdoxy': ['templates/*.jinja2']},
    entry_points={
        'mkdocs.plugins': [
            'mkdoxy = mkdoxy.plugin:MkDoxy'
        ]
    }
)
