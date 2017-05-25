import requests


default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko)Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0',
                   'Encoding': 'UTF-8'}

session = requests.session()
session.headers.update(default_headers)
