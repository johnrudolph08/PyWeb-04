"""
A Mashup that takes "facts" from http://www.unkno.com/ and adds them
to memes using https://imgflip.com/memegenerator

This base code is a copy of our initial pseudo calculator code; we will
modify it to our purpose.
"""
from bs4 import BeautifulSoup
import requests

def meme_it(fact):
    url = 'http://cdn.meme.am/Instance/Preview'
    params ={
        'imageID':2097248,
        'text1': fact
    }
    response = requests.get(url, params)

    return response.content

def parse_fact(body):
    parsed = BeautifulSoup(body, 'html5lib')
    fact = parsed.find('div', id='content')
    return fact.text.strip()

def get_fact():
    response = requests.get('http://unkno.com')
    return parse_fact(response.text)

def process():
    fact = get_fact()

    meme = meme_it(fact)

    return meme

def application(environ, start_response):
    headers = [('Content-type', 'image/jpg')]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError
        body = process()
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1> Internal Server Error</h1>"
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
