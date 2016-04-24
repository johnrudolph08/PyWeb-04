"""
For your homework this week, you'll be creating a new WSGI application.

The MEMEORIZER acquires a phrase from one of two sources, and applies it
to one of two meme images.

The two possible sources are:

  1. A fact from http://unkno.com
  2. One of the 'Top Stories' headlines from http://www.cnn.com

For the CNN headline you can use either the current FIRST headline, or
a random headline from the list. I suggest starting by serving the FIRST
headline and then modifying it later if you want to.

The two possible meme images are:

  1. The Buzz/Woody X, X Everywhere meme
  2. The Ancient Aliens meme (eg https://memegenerator.net/instance/11837275)

To begin, you will need to collect some information. Go to the Ancient
Aliens meme linked above. Open your browser's network inspector; in Chrome
this is Ctrl-Shift-J and then click on the network tab. Try typing in some
new 'Bottom Text' and observe the network requests being made, and note
the imageID for the Ancient Aliens meme.

TODO #1:
The imageID for the Ancient Aliens meme is:

You will also need a way to identify headlines on the CNN page using
BeautifulSoup. On the 'Unnecessary Knowledge Page', our fact was
wrapped like so:

```
<div id="content">
  Penguins look like they're wearing tuxedos.
</div>
```

So our facts were identified by the tag having
* name: div
* attribute name: id
* attribute value: content.

We used the following BeautifulSoup call to isolate that element:

```
element = parsed.find('div', id='content')
```

Now we have to figure out how to isolate CNN headlines. Go to cnn.com and
'inspect' one of the 'Top Stories' headlines. In Chrome, you can right
click on a headline and click 'Inspect'. If an element has a rightward
pointing arrow, then you can click on it to see its contents.

TODO #2:
Each 'Top Stories' headline is wrapped in a tag that has:
* name:
* attribute name:
* attribute value:

NOTE: We used the `find` method to find our fact element from unkno.com.
The `find` method WILL ALSO work for finding a headline element from cnn.com,
although it will return exactly one headline element. That's enough to
complete the assignment, but if you want to isolate more than one headline
element you can use the `find_all` method instead.


TODO #3:
You will need to support the following four requests:

```
  http://localhost:8080/fact/buzz
  http://localhost:8080/fact/aliens
  http://localhost:8080/news/buzz
  http://localhost:8080/news/aliens
```

You can accomplish this by modifying the memefacter.py that we created
in class.

There are multiple ways to architect this assignment! You will probably
have to either change existing functions to take more arguments or create
entirely new functions.

I have started the assignment off by passing `path` into `process` and
breaking it apart using `strip` and `split` on lines 136, 118, and 120.

To submit your homework:

  * Fork this repository (PyWeb-04).
  * Edit this file to meet the homework requirements.
  * Your script should be runnable using `$ python memeorizer.py`
  * When the script is running, I should be able to view your
    application in my browser.
  * Commit and push your changes to your fork.
  * Submit a link to your PyWeb-04 fork repository!

"""

from bs4 import BeautifulSoup
import requests
import random

def meme_it(image, text):
  """Fetches image, overlays text and returns meme"""
  url = 'http://cdn.meme.am/Instance/Preview'
  #dictionary to hold required url parameters to retreive buzz/aliens image
  params = {
    'buzz': {'imageID':2097248, 'text1':text},
    'aliens':{'imageID':"627067", 'text1':text}
  }.get(image)
  response = requests.get(url, params)
  return response.content

def parse_unkno(site_contents):
  """Pulls the random fact displayed from unkno.com"""
  parsed = BeautifulSoup(site_contents, 'html5lib')
  fact = parsed.find('div', id='content')
  return fact.text.strip()

def parse_cnn(site_contents):
  """Pulls a random title from CNN rss top headlines page"""
  parsed = parsed = BeautifulSoup(site_contents, 'html5lib')
  #create a list of all titles in item tags
  fact_list = [item.find('title') for item in parsed.findAll('item')]
  #pick a random title
  fact = random.choice(fact_list)
  return fact.text.strip()

def get_text(text):
  """Determine if fact/news is requested and return related content"""
  site_name = {
    'fact': 'http://unkno.com',
    'news': 'http://rss.cnn.com/rss/cnn_topstories.rss',
  }.get(text)
  response = requests.get(site_name)
  #call parse function based on site name requested
  parse = {
    'http://unkno.com': parse_unkno,
    'http://rss.cnn.com/rss/cnn_topstories.rss': parse_cnn,
  }.get(site_name)  
  return parse(response.text)

def process(path):
    """Get type of text and type of image from url path and return meme"""
    args = path.strip("/").split("/")
    #first item is source of text second item is image
    text_source, image = args[0], args[1]
    #retreive text used for meme
    text = get_text(text_source)
    #overlay text ontop of image
    meme = meme_it(image, text)
    return meme

def application(environ, start_response):
    """Boilerplate HTTP response"""
    headers = [('Content-type', 'image/jpeg')]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError
        body = process(path)
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
