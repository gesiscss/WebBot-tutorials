# WebBotParser

This repository adds basic parsing capabilities for search engine results scraped with [WebBot](https://github.com/gesiscss/WebBot). With this package, you can parse search result pages saved from Google, DuckDuckGo, etc. using WebBot's [download capabilities](https://github.com/gesiscss/WebBot#-saving-search-results), or obtained through a different method for further analysis.

The following engines and search result types are currently supported out of the box: Google Text, Google News, DuckDuckGo Text, and DuckDuckGo News. For examplary usage, see `example.ipynb`.

## Installation

For basic usage, simply clone this repository, or directly download `webbotparser/webbotparser.py` and add this script to your working directory.

### Install the package with pip

If you want to use the WebBotParser over multiple projects/directories, you can also install it as a python package. Clone this repository, navigate to the folder, and run
```
pip install -e .
```
The `webbotparser` package is then available globally in your respective Python installation.

## Usage

For the search engines and result types supported out of the box, simply run
```
from webbotparser import WebBotParser
```
and initialize the WebBotParser for the search engine and result type your are investigating, for example
```
parser = WebBotParser(engine = 'DuckDuckGo News')
```
Then, you can obtain the search results as a pandas DataFrame and metadata as a python dictionary with
```
metadata, results = parser.get_results(file='path/to/the/result_page.html', with_metadata=True)
```
Furthermore, `parser.get_metadata(file)` can be used to only extract the metadata. `parser.get_results_from_dir(dir)` allows to directly extract search results spread over multiple pages, as Google text result are provided for instance. For examples also see `example.ipynb`.

### Custom result types
