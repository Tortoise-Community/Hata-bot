import json

with open("config.json") as fp:
    config = json.load(fp)

with open('website/src/index.html', 'r') as fp:
    INDEX_HTML = fp.read()

with open('website/src/header/header.html', 'r') as fp:
    HEADER_HTML = fp.read()

with open('website/src/header/header.css', 'r') as fp:
    HEADER_CSS = fp.read()

with open('website/src/index.js', 'r') as fp:
    INDEX_JS = fp.read()

with open('website/src/home/home.html', 'r') as fp:
    HOME_HTML = fp.read()

with open('website/src/home/home.css', 'r') as fp:
    HOME_CSS = fp.read()

with open('website/src/documentation/documentation.html', 'r') as fp:
    DOCUMENTATION_HTML = fp.read()

with open('website/src/documentation/documentation.css', 'r') as fp:
    DOCUMENTATION_CSS = fp.read()

with open('website/scripts/jquery.js', 'r') as fp:
    JQUERY_JS = fp.read()

with open('website/assets/cinnamon.png', 'rb') as fp:
    CINNAMON_IMAGE = fp.read()

class WebApp:
    SERVER_SETUP = config.get('WEB_APP')

class Header:
    HTML = HEADER_HTML
    CSS = HEADER_CSS

class Index:
    HTML = INDEX_HTML
    JAVASCRIPT = INDEX_JS

class Home:
    HTML = HOME_HTML
    CSS = HOME_CSS

class Documentation:
    HTML = DOCUMENTATION_HTML
    CSS = DOCUMENTATION_CSS

class Scripts:
    JQUERY = JQUERY_JS

class Assets:
    CINNAMON = CINNAMON_IMAGE