from bs4 import BeautifulSoup
import pandas as pd
import regex as re
import warnings
import pathlib
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64

class WebBotParser:

    def __init__(self, engine = None, queries = [], result_selector = '',
                 metadata_extractor = lambda soup, file: {},
                 extract_images = False, extract_images_to_dir = 'extracted_images',
                 extract_images_prefix = '', extract_images_format = 'JPEG'):
        """To use the WebBotParser, either specify one of the supported engines,
 or specify your own list of queries and/or a metadata extractor function.
\nThe currently supported engines and result types are are:
 'Google Text', 'Google News', 'Google Images', 'Google Videos',
 'DuckDuckGo Text', 'DuckDuckGo News', 'DuckDuckGo Images', 'DuckDuckGo Videos',
 'Yahoo Text', 'Yahoo News', 'Yahoo Images',
 'Baidu Text', and 'Baidu News'."""

        self.extract_images = extract_images
        self.extract_images_to_dir = extract_images_to_dir
        self.extract_images_prefix = extract_images_prefix
        self.extract_images_format = extract_images_format
        
        if engine is None and len(queries) == 0 and len(metadata_extractor(None, None)) == 0:
            raise Exception(self.__init__.__doc__)
        if engine is not None:
            if engine == 'Google Text':
                self.result_selector = GoogleParser.google_text_result_selector
                if extract_images: self.queries = GoogleParser.google_text_queries_with_images
                else: self.queries = GoogleParser.google_text_queries
                self.metadata_extractor = GoogleParser.google_metadata
            elif engine == 'Google News':
                self.result_selector = GoogleParser.google_news_result_selector
                if extract_images: self.queries = GoogleParser.google_news_queries_with_images
                else: self.queries = GoogleParser.google_news_queries
                self.metadata_extractor = GoogleParser.google_metadata
            elif engine == 'Google Images':
                self.result_selector = GoogleParser.google_images_result_selector
                if extract_images: self.queries = GoogleParser.google_images_queries_with_images
                else: self.queries = GoogleParser.google_images_queries
                self.metadata_extractor = GoogleParser.google_images_metadata
            elif engine == 'Google Videos':
                self.result_selector = GoogleParser.google_videos_result_selector
                if extract_images: self.queries = GoogleParser.google_videos_queries_with_images
                else: self.queries = GoogleParser.google_videos_queries
                self.metadata_extractor = GoogleParser.google_metadata
            elif engine == 'DuckDuckGo Text':
                self.result_selector = DuckDuckGoParser.duckduckgo_text_result_selector
                self.queries = DuckDuckGoParser.duckduckgo_text_queries
                self.metadata_extractor = DuckDuckGoParser.duckduckgo_metadata
            elif engine == 'DuckDuckGo News':
                self.result_selector = DuckDuckGoParser.duckduckgo_news_result_selector
                if extract_images: self.queries = DuckDuckGoParser.duckduckgo_news_queries_with_images
                else: self.queries = DuckDuckGoParser.duckduckgo_news_queries
                self.metadata_extractor = DuckDuckGoParser.duckduckgo_metadata
            elif engine == 'DuckDuckGo Images':
                self.result_selector = DuckDuckGoParser.duckduckgo_images_result_selector
                if extract_images: self.queries = DuckDuckGoParser.duckduckgo_images_queries_with_images
                else: self.queries = DuckDuckGoParser.duckduckgo_images_queries
                self.metadata_extractor = DuckDuckGoParser.duckduckgo_metadata
            elif engine == 'DuckDuckGo Videos':
                self.result_selector = DuckDuckGoParser.duckduckgo_videos_result_selector
                if extract_images: self.queries = DuckDuckGoParser.duckduckgo_videos_queries_with_images
                else: self.queries = DuckDuckGoParser.duckduckgo_videos_queries
                self.metadata_extractor = DuckDuckGoParser.duckduckgo_metadata
            elif engine == 'Yahoo Text':
                self.result_selector = YahooParser.yahoo_text_result_selector
                self.queries = YahooParser.yahoo_text_queries
                self.metadata_extractor = YahooParser.yahoo_metadata
            elif engine == 'Yahoo News':
                self.result_selector = YahooParser.yahoo_news_result_selector
                if extract_images: self.queries = YahooParser.yahoo_news_queries_with_images
                else: self.queries = YahooParser.yahoo_news_queries
                self.metadata_extractor = YahooParser.yahoo_metadata
            elif engine == 'Yahoo Images':
                self.result_selector = YahooParser.yahoo_images_result_selector
                if extract_images: self.queries = YahooParser.yahoo_images_queries_with_images
                else: self.queries = YahooParser.yahoo_images_queries
                self.metadata_extractor = YahooParser.yahoo_image_metadata
            elif engine == 'Baidu Text':
                self.result_selector = BaiduParser.baidu_text_result_selector
                self.queries = BaiduParser.baidu_text_queries
                self.metadata_extractor = BaiduParser.baidu_metadata
            elif engine == 'Baidu News':
                self.result_selector = BaiduParser.baidu_news_result_selector
                self.queries = BaiduParser.baidu_news_queries
                self.metadata_extractor = BaiduParser.baidu_metadata
            else:
                raise Exception('Engine not supported')
        elif result_selector == '':
            raise Exception('A result_selector string is required to discriminate individual results on each page.')
        else:
            self.result_selector = result_selector
            self.queries = queries
            self.metadata_extractor = metadata_extractor




    def get_metadata(self, file):
        """Only extract the metadata from an archived search results page."""
        soup = self.__get_soup(file)
        return self.metadata_extractor(soup, file)
    
    
    def get_results(self, file, with_metadata = True):
        """Extract the search results and optionally metadata from an archived search results page."""

        soup = self.__get_soup(file)
        results = self.__evaluate_soup(soup)

        metadata = {}
        if with_metadata: metadata = self.metadata_extractor(soup, file)
        
        return (metadata, results)


    def get_results_from_dir(self, dir):
        """Extract search results from all archived search result pages in a given directory.\
 All pages should share the same search terms, engine, and result type.\
 This function helps in combining results spread over multiple pages, e.g. Google News results."""
        
        metadata = {}
        results = pd.DataFrame()

        # get the results for all pages
        dir = pathlib.Path(dir)
        for file in dir.glob('*.html'):
            if file.is_file():
                _metadata, _results = self.get_results(str(file))
                if len(metadata) > 0 and (_metadata['engine'] != metadata['engine'] or _metadata['query'] != metadata['query'] \
                                           or _metadata['result type'] != metadata['result type']):
                    warnings.warn('Results from multiple engines, result types, or search terms detected.\
 It is recommended to run this function on seperate folders, one for each search term,\
 and properly initialized for each engine and result type.', UserWarning)
                _results['date'] = _metadata['date']
                _results['page'] = _metadata['page']
                del _metadata['page']
                del _metadata['date']
                metadata = _metadata

                results = pd.concat([results, _results])

        # reset the index such that it reflects the actual result's number
        results = results.reset_index().sort_values(by=['page', 'index'])
        results['position'] = results['index']
        results = results.drop('index', axis=1).reset_index(drop=True)

        return (metadata, results)




    ### utility functions
    def __get_soup(self, file):
        with open(file) as fp:
            soup = BeautifulSoup(fp, "lxml") # the integrated html parser had some problems with tables...
        return soup

    
    def __evaluate_soup(self, soup):
        result_soups = soup.select(self.result_selector)
        _results = []
        for i, _soup in enumerate(result_soups):
            #print(i)
            result = {}
            for query in self.queries:
                result[query['name']] = self.__evaluate_query(query, _soup)
            _results.append(result)
        return pd.DataFrame(_results)


    def __extract_inline_image(self, bytecode, file):
        img = bytecode.split(',')[-1] # remove format information
        # https://stackoverflow.com/a/6966225/15164646
        image = Image.open(BytesIO(base64.b64decode(str(img)))) # decode the base64 inline image a create a Pillow Image object
        image.save(file, self.extract_images_format)
        return file

    
    def __evaluate_query(self, query, result_soup):
        if (query['type'] == 'custom'):
                return query['function'](result_soup)
        else:
            _res = result_soup.select(query['selector'])

            if (query['type'] == 'exists'):
                return len(_res) > 0
            
            elif (query['type'] == 'image'):
                if (len(_res) > 0):
                    if 'title_label_selector' in query:
                        title = self.__evaluate_query(
                            {'name': 'image_title', 'type': 'attribute', 'selector': query['title_label_selector'], 'attribute': 'aria-label'}
                            , result_soup)
                    else:
                        title = self.__evaluate_query({'name': 'image_title', 'type': 'text', 'selector': query['title_selector']}, result_soup)
                    title = "".join(x for x in title if x.isalnum()) # make it a valid filename
                    file = f'{self.extract_images_to_dir}/{self.extract_images_prefix}_{title}.{self.extract_images_format.lower()}'
                    try:
                        return self.__extract_inline_image(_res[0]['src'], file) # some images might have coding issues
                    except: return None
                else: return None

            elif (len(_res) == 0): warnings.warn("CSS selector for '" + query['name'] + "' didn't match.", UserWarning, stacklevel=2)
            elif (len(_res) > 1): warnings.warn("CSS selector for '" + query['name'] + "' returned multiple matches.", UserWarning, stacklevel=2)

            elif (query['type'] == 'text'):
                return _res[0].get_text()
            
            elif (query['type'] == 'attribute'):
                return _res[0][query['attribute']]




class GoogleParser:

    google_text_result_selector = 'div.g > div' #div[jscontroller="SC7lYd"] is too deep to check for indentation
    google_text_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'div.yuRUbf > a > h3'},
        {'name': 'link', 'type': 'attribute', 'selector': 'div.yuRUbf > a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'div.VwiC3b'},
        # the following fails on text previews with author info: div.VwiC3b > span:not(.MUxGbd), div.VwiC3b:not(:has(span))
        # for now, we handle dates and authors as part of the preview text
        {'name': 'has_image', 'type': 'exists', 'selector': 'div.Z26q7c img'},
        {'name': 'is_indented', 'type': 'exists', 'selector': 'ul.FxLDp'},
    ]
    google_text_queries_with_images = google_text_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'div.Z26q7c img', 'title_selector': 'div.yuRUbf > a > h3'}
    ]

    google_news_result_selector = 'div.SoaBEf'
    google_news_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'div.mCBkyc'},
        {'name': 'link', 'type': 'attribute', 'selector': 'a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'div.GI74Re'},
        {'name': 'source', 'type': 'text', 'selector': 'div.CEMjEf'},
        {'name': 'has_image', 'type': 'exists', 'selector': 'div.FAkayc img'},
        {'name': 'published', 'type': 'text', 'selector': 'div.OSrXXb'}
    ]
    google_news_queries_with_images = google_news_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'div.FAkayc img', 'title_selector': 'div.mCBkyc'}
    ]

    google_images_result_selector = 'div.isv-r.PNCib.MSM1fd.BUooTd'
    google_images_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h3'},
        {'name': 'link', 'type': 'attribute', 'selector': 'a.VFACy', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'div.dmeZbb'}
    ]
    google_images_queries_with_images = google_images_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'div.bRMDJf > img', 'title_selector': 'h3'}
    ]

    @staticmethod
    def get_date(_soup):
        date = _soup.select('div.P7xzyf > span:last-child')[0].get_text()
        try: date = pd.to_datetime(date, format="%d.%m.%Y")  # some dates are relative, we ignore them for now
        except: date = None
        return date

    @staticmethod
    def get_duration(_soup):
        duration = _soup.select('div.J1mWY')
        if len(duration) == 1: # some videos don't have a duration
            min_sec = duration[0].get_text().split(':')
            return pd.to_timedelta(int(min_sec[0])*60 + int(min_sec[1]), unit='seconds')
        return None
    
    google_videos_result_selector = 'div.MjjYud'
    google_videos_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h3'},
        {'name': 'link', 'type': 'attribute', 'selector': 'div.ct3b9e > a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'div.Uroaid'},
        {'name': 'source', 'type': 'text', 'selector': 'span.Zg1NU'},
        {'name': 'published', 'type': 'custom', 'function': get_date},
        {'name': 'duration', 'type': 'custom', 'function': get_duration}
    ]
    google_videos_queries_with_images = google_videos_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'g-img > img', 'title_selector': 'h3'}
    ]

    @staticmethod
    def google_metadata(soup, file):
        file = pathlib.Path(file).name
        _result_type = file.split('_')[-5]
        _engine = file.split('_')[0].split('/')[-1]
        _query = file.split('_')[1]
        _page = int(soup.select('td.YyVfkd')[0].get_text())
        _date = pd.to_datetime(file[-24:-5], format="%Y-%m-%d_%H_%M_%S")
        # extract all numbers from the result-stats, primitively remove any dots and commas, and return the largest number
        _result_stats = soup.select('#result-stats')[0].get_text()
        _total_results = max([int(re.sub(r"[^\d]+", '', _stat)) for _stat in re.findall(r"[\d]+(?:[,\.]\d\d\d)*[,\.]?\d*", _result_stats)])
        return {'result type': _result_type, 'engine': _engine, 'query': _query, 'page': _page, 'date': _date, 'total results': _total_results}

    @staticmethod
    def google_images_metadata(soup, file):
        file = pathlib.Path(file).name
        _result_type = file.split('_')[-5]
        _engine = file.split('_')[0].split('/')[-1]
        _query = file.split('_')[1]
        _date = pd.to_datetime(file[-24:-5], format="%Y-%m-%d_%H_%M_%S")
        return {'result type': _result_type, 'engine': _engine, 'query': _query, 'date': _date}


class DuckDuckGoParser:

    duckduckgo_text_result_selector = "article[id|='r1']" # some of the other <articles> are ads
    duckduckgo_text_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h2'},
        {'name': 'link', 'type': 'attribute', 'selector': 'h2 > a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'article > div:nth-child(3) span:last-child'}, # remove the date by selecting the last <span>
    ]

    duckduckgo_news_result_selector = 'div.result__body'
    duckduckgo_news_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h2.result__title'},
        {'name': 'link', 'type': 'attribute', 'selector': 'a.result__a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'div.result__snippet'},
        {'name': 'source', 'type': 'text', 'selector': 'a.result__url'},
        {'name': 'has_image', 'type': 'exists', 'selector': 'div.result__image'},
        {'name': 'published', 'type': 'text', 'selector': 'span.result__timestamp'}
    ]
    duckduckgo_news_queries_with_images = duckduckgo_news_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'div.result__image img', 'title_selector': 'h2.result__title'},
    ]

    duckduckgo_images_result_selector = 'div.tile--img:not(.is-hidden)'
    duckduckgo_images_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'span.tile--img__title'},
        {'name': 'link', 'type': 'attribute', 'selector': 'a.tile--img__sub', 'attribute': 'href'},
        {'name': 'dimensions', 'type': 'text', 'selector': 'div.tile--img__dimensions > em'}
    ]
    duckduckgo_images_queries_with_images = duckduckgo_images_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'img.tile--img__img', 'title_selector': 'span.tile--img__title'},
    ]

    duckduckgo_videos_result_selector = 'div.tile--vid'
    duckduckgo_videos_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h6.tile__title'},
        {'name': 'link', 'type': 'attribute', 'selector': 'h6.tile__title > a', 'attribute': 'href'},
        {'name': 'source', 'type': 'text', 'selector': 'span.video-source'},
        {'name': 'views', 'type': 'text', 'selector': 'span.tile__count'},
        {'name': 'duration', 'type': 'text', 'selector': 'span.image-labels__label'}
    ]
    duckduckgo_videos_queries_with_images = duckduckgo_videos_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'img.tile__media__img', 'title_selector': 'h6.tile__title'}
    ]

    @staticmethod
    def duckduckgo_metadata(soup, file):
        file = pathlib.Path(file).name
        _result_type = file.split('_')[-5]
        _engine = file.split('_')[0].split('/')[-1]
        _query = file.split('_')[1]
        _date = pd.to_datetime(file[-24:-5], format="%Y-%m-%d_%H_%M_%S")
        return {'result type': _result_type, 'engine': _engine, 'query': _query, 'date': _date}


class YahooParser:

    yahoo_text_result_selector = 'li > div.dd.algo'
    yahoo_text_queries = [
            {'name': 'title', 'type': 'text', 'selector': 'h3.title'},
            {'name': 'link', 'type': 'attribute', 'selector': 'h3.title > a', 'attribute': 'href'},
            {'name': 'text', 'type': 'text', 'selector': 'div.compText.aAbs'},
        ]
    
    yahoo_news_result_selector = 'li > div.dd.NewsArticle'
    yahoo_news_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h4.s-title'},
        {'name': 'link', 'type': 'attribute', 'selector': 'h4.s-title > a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'p.s-desc'},
        {'name': 'source', 'type': 'text', 'selector': 'span.s-source'},
        {'name': 'has_image', 'type': 'exists', 'selector': 'a img'},
        {'name': 'published', 'type': 'text', 'selector': 'span.fc-2nd.s-time.mr-8'}
    ]
    yahoo_news_queries_with_images = yahoo_news_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'a img', 'title_selector': 'h4.s-title'},
    ]

    yahoo_images_result_selector = "li[id^='resitem']:not(.dud)"
    yahoo_images_queries = [
        {'name': 'title', 'type': 'attribute', 'selector': 'a.img', 'attribute': 'aria-label'},
        {'name': 'link', 'type': 'attribute', 'selector': 'a.img', 'attribute': 'href'}
    ]
    yahoo_images_queries_with_images = yahoo_images_queries + [
        {'name': 'image', 'type': 'image', 'selector': 'a img', 'title_label_selector': 'a.img'},
    ]

    @staticmethod
    def yahoo_metadata(soup, file):
        file = pathlib.Path(file).name
        _result_type = file.split('_')[-5]
        _engine = file.split('_')[0].split('/')[-1]
        _query = file.split('_')[1]
        _page = int(soup.select('div.pages > strong')[0].get_text())
        _date = pd.to_datetime(file[-24:-5], format="%Y-%m-%d_%H_%M_%S")
        return {'result type': _result_type, 'engine': _engine, 'query': _query, 'page': _page, 'date': _date}
    
    @staticmethod
    def yahoo_image_metadata(soup, file):
        file = pathlib.Path(file).name
        _result_type = file.split('_')[-5]
        _engine = file.split('_')[0].split('/')[-1]
        _query = file.split('_')[1]
        _date = pd.to_datetime(file[-24:-5], format="%Y-%m-%d_%H_%M_%S")
        return {'result type': _result_type, 'engine': _engine, 'query': _query, 'date': _date}


class BaiduParser:

    @staticmethod
    def get_date(_soup):
        dates = _soup.select('span.c-color-gray2')
        try: # some results don't have a date
            date = dates[0].get_text().split(': ')[-1][:-1] # some dates have additional information
            date = pd.to_datetime(date, format="%Y年%m月%d日")
        except: date = None
        return date

    baidu_text_result_selector = 'div.result'
    baidu_text_queries = [
            {'name': 'title', 'type': 'text', 'selector': 'h3'},
            {'name': 'link', 'type': 'attribute', 'selector': 'h3 > a', 'attribute': 'href'},
            {'name': 'text', 'type': 'text', 'selector': 'span.content-right_8Zs40, div.c-span9 p:nth-child(2)'},
            {'name': 'source', 'type': 'text', 'selector': 'div.source_1Vdff > a, span.c-showurl'},
            {'name': 'has_image', 'type': 'exists', 'selector': '.c-img3'},
            {'name': 'published', 'type': 'custom', 'function': get_date}
        ]

    @staticmethod
    def get_news_date(_soup):
        dates = _soup.select('span.c-color-gray2')
        try: # try an absolute date
            date = pd.to_datetime(dates[0].get_text(), format="%Y年%m月%d日")
        except:
            date = None
            try: # try a relative date
                date = str(datetime.now().year) + '年' + dates[0].get_text()
                date = pd.to_datetime(date, format="%Y年%m月%d日")
            except: date = None
        return date
    
    baidu_news_result_selector = 'div.c-container'
    baidu_news_queries = [
        {'name': 'title', 'type': 'text', 'selector': 'h3'},
        {'name': 'link', 'type': 'attribute', 'selector': 'h3 > a', 'attribute': 'href'},
        {'name': 'text', 'type': 'text', 'selector': 'div.content-wrapper_1SuJ0 > div > span:nth-child(2), div.content_BL3zl > span:nth-child(2)'},
        {'name': 'source', 'type': 'text', 'selector': 'div.news-source_Xj4Dv'},
        {'name': 'has_image', 'type': 'exists', 'selector': '.c-img3'},
        {'name': 'published', 'type': 'custom', 'function': get_news_date}
    ]

    @staticmethod
    def baidu_metadata(soup, file):
        file = pathlib.Path(file).name
        _result_type = file.split('_')[-5]
        _engine = file.split('_')[0].split('/')[-1]
        _query = file.split('_')[1]
        _page = int(soup.select('div#page strong')[0].get_text())
        _date = pd.to_datetime(file[-24:-5], format="%Y-%m-%d_%H_%M_%S")
        return {'result type': _result_type, 'engine': _engine, 'query': _query, 'page': _page, 'date': _date}
