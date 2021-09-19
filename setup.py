from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='mkdocs-doxygen-snippets-plugin',
    version='0.1.0',
    description='MkDocs Doxygen snippets plugin to create easy documentation',
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords='mkdocs',
    url='https://github.com/JakubAndrysek/mkdocs-doxygen-snippets-plugin',
    author='Jakub Andrýsek',
    author_email='email@kubaandrysek.cz',
    license='MIT',
    python_requires='>=3',
    install_requires=[
        'mkdocs>=1.0.4',
        'pprint',
        'mkdocs',
        'Jinja2',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'doxygen-snippets = doxygen_snippets.plugin:DoxygenSnippets'
        ]
    }
)
