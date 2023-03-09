# WebBotParser

This repository adds basic parsing capabilities for search engine results scraped with [WebBot](https://github.com/gesiscss/WebBot). With this package, you can parse search result pages saved from Google, DuckDuckGo, etc. using WebBot's [download capabilities](https://github.com/gesiscss/WebBot#-saving-search-results), or obtained through a different method for further analysis.

The following engines and search result types are currently supported out of the box:
- Google Text
- Google News
- Google Video
- DuckDuckGo Text
- DuckDuckGo News
- Baidu Text
- Baidu News

For examplary usage, see `example.ipynb`.

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
metadata, results = parser.get_results(file='path/to/the/result_page.html')
```
Furthermore, `parser.get_metadata(file)` can be used to only extract the metadata. `parser.get_results_from_dir(dir)` allows to directly extract search results spread over multiple pages, as Google text result are provided for instance. For examples also see `example.ipynb`.

## Custom result types

WebBotParser out of the box only provides support for some search engines and result types. Even these parsers might stop working if the search engine providers decide to change their layout. However, WebBotParser can still be used in these cases by defining a custom `result_selector`, `queries`, and optionally a `metadata_extractor` function. In this case, a WebBotParser is initiated with these instead of with the `engine` attribute
```
parser = WebBotParser(queries, result_selector, metadata_extractor)
```

Under the hood, WebBotParser uses [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/index.html) to

1. Parse the search result page's HTML via LXML
2. Disciminate the individual results on each page using a [CSS selector](https://beautiful-soup-4.readthedocs.io/en/latest/index.html#css-selectors) called `result_selector` that matches a list of search results
3. For each of those results, extract available information through a list of queries

See the below example for available types of queries and their usage
```
queries = [
    # extract the text from inside a matched element, getting all the text over all its children
    {'name': 'abc', 'type': 'text', 'selector': 'h3'},
    
    # extract the value of an attribute of a matched element
    {'name': 'def', 'type': 'attribute', 'selector': 'a', 'attribute': 'href'},
    
    # whether or not a CSS selector matches, returns a Boolean
    {'name': 'ghi', 'type': 'exists', 'selector': 'ul'},
    
    # pass a custom query function
    {'name': 'jkl', 'type': 'custom', 'function': my_function},
]
```

You can optionally provide a `metadata_extractor(soup, file)` function to extract metadata alongside the search results, or import one of the existing extractors, e.g. with
```
from webbotparser import GoogleParser
metadata_extractor = GoogleParser.google_metadata
```