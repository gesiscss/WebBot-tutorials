# WebBot tutorials

This repository contains tutorials for parsing search engine results scraped with [WebBot](https://github.com/gesiscss/WebBot).

## Parsing with Python

You can parse search result pages saved from Google, DuckDuckGo, etc. using our Python package [WebBotParser](https://github.com/gesiscss/WebBotParser) for further analysis.
To install it, use `pip`:
```
pip install git+https://github.com/gesiscss/WebBotParser
```

For examplary usage, see [example.ipynb](./example.ipynb).

## Parsing with R

Refer to [webbotparseR](https://github.com/schochastics/webbotparseR), a similar R package.

## Alternative

[WebSearcher](https://github.com/gitronald/WebSearcher) is a Python package that facilitates obtaining and parsing search results from Google text search. Compared to `webbotparser`, it supports parsing more diverse results (ads, knowledge boxes, etc.), but only Google text results (for now). [websearcher.ipynb](./websearcher.ipynb) illustrates how to utilize WebSearcher's parsing capabilities on search result pages obtained using WebBot.
