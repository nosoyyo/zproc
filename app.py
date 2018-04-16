# kapua req
import json
from apistar import http, Include, Route
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls

from zproc import ZProc_REQ
from config import Config

# init
z = ZProc_REQ(Config)


def reverseDict(dic):
    keys = list(reversed([key for key in dic.keys()]))
    values = list(reversed([value for value in dic.values()]))
    rd = {}
    for i in range(len(keys)):
        rd[keys[i]] = values[i]
    return rd


def set_lang(lang='zh'):
    return z.REQ(lang, 'string', 'string')


def search(query, sug=False):
    j = json.dumps((query, sug))
    return z.REQ(j, 'json', 'json')


def suggest(query):
    return z.REQ(query, 'string', 'string')


def getKwargs(kwargs: http.QueryParams) -> dict:
    return dict(kwargs)


def summary(kwargs: http.QueryParams) -> dict:
    query = kwargs['query']
    if len(kwargs) > 1:
        j = reverseDict(kwargs._dict)
        j.pop('query')
        params = json.dumps({'p': query, 'd': j})
        method = 'json'
        arg_type = 'pd'
    else:
        params = query
        method = 'string'
        arg_type = 'normal'

    result = z.REQ(params, method, 'string', arg_type=arg_type)
    return result


def page(kwargs: http.QueryParams) -> dict:
    '''
        wikipedia.page(title=None, pageid=None, auto_suggest=True,
        redirect=True, preload=False)
    '''
    j = reverseDict(kwargs._dict)
    result = z.REQ(j, 'json', 'pyobj').__dict__
    return result


def geosearch(kwargs: http.QueryParams) -> dict:
    '''
        wikipedia.geosearch(latitude, longitude, title=None,
        results=10, radius=1000)
    '''
    j = reverseDict(kwargs._dict)
    return z.REQ(j, 'json', 'json')


def random(page=1):
    return z.REQ(str(page), 'string', 'string')


routes = [
    Route('/msu/wiki/set_lang', 'POST', set_lang),
    Route('/msu/wiki/search', 'POST', search),
    Route('/msu/wiki/suggest', 'POST', suggest),
    Route('/msu/wiki/summary', 'POST', summary),
    Route('/msu/wiki/page', 'POST', page),
    Route('/msu/wiki/geosearch', 'POST', geosearch),
    Route('/msu/wiki/random', 'GET', random),
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]

app = App(routes=routes)


if __name__ == '__main__':
    app.main()
