from setuptools import setup

setup(
    author='Georg Ahnert',
    description='Basic parsing capabilities for search engine results scraped with WebBot',
    name='webbotparser',
    version='0.1.0',
    packages=['webbotparser'],
    install_requires=[
         'pandas>=1.5.3',
         'regex>=2022.10.31',
         'beautifulsoup4>=4.11.2',
         'lxml>=4.9.2'
    ], 
    python_requires='>=3.8'
)