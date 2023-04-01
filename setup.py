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
    version='1.0.5',
    description='MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets',
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords='mkdoxy, python, open-source, documentation, mkdocs, doxygen, multilanguage, code-snippets, code, snippets, documentation-generator',
    url='https://github.com/JakubAndrysek/MkDoxy',
    author='Jakub Andrýsek',
    author_email='email@kubaandrysek.cz',
    license='MIT',
    python_requires='>=3.8',
    install_requires=requirements(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
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
