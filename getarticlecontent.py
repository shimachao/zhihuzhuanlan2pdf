# -*-coding:utf-8-*-

""" 获取一个知乎专栏中的一篇文章，以供后续分析
"""

import requests
import json
import jinja2


class ZhuanlanSession:
    """ 维护和知乎服务器之间的连接"""

    def __int__(self):
        self.s = requests.session()
        self.default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                                              '(KHTML, like Gecko)Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0',
                                'Encoding': 'UTF-8'}
        self.img_path = './img'  # 图片的保存路径

    def get_one_article(self, slug):
        """ 获取 slug 指定的一篇知乎专栏文章
        slug 是知乎专栏文章的唯一识别码
        返回一个字典对象，里面包括文章标题、作者、发布时间、文章内容等
        """
        self.s.headers.update(self.default_headers)
        url = 'https://zhuanlan.zhihu.com/api/posts/' + slug

        json_obj = json.loads(self.s.get(url=url).text, encoding='utf-8')
        article = dict()
        article['title'] = json_obj['title']
        article['title_image_url'] = json_obj['titleImage']
        article['author_name'] = json_obj['author']['name']

        # 获取作者头像url
        author_avatar_template = json_obj['author']['avatar']['template']
        avatar_id = json_obj['author']['avatar']['id']
        author_avatar_url = author_avatar_template[:author_avatar_template.rfind('/')+1] + avatar_id + '_xs.jpg'
        article['author_avatar_url'] = author_avatar_url
        # 发布时间
        article['publishedTime'] = json_obj['publishedTime']

        # 文章内容
        article['content'] = json_obj['content']

        # 该文章的评论列表url
        article['comments_links'] = 'https://zhuanlan.zhihu.com' + json_obj['links']['comments']
        # 评论数
        article['comments_count'] = json_obj['pageCommentsCount']

        return article

    def img_download(self, url):
        """ 下载 url 指定的图片并保存到本地，并返回本地路径"""
        # 提取 url 中图片的名称
        name = url[url.rfind('/')+1:]
        binary_content = self.s.get(url=url).content
        path = self.img_path + '/' + name
        with open(file=path, mode='wb') as f:
            f.write(binary_content)

        return path

    def images_to_local(self, article):
        """ 将 article 中引用到的所有图片下载到本地，并将 url 指向本地图片，方便后面转成 pdf
        需要处理的图片url包括文章标题中的图片，作者头像，以及正文中的图片"""
        article['title_image_url'] = self.img_download(url=article['title_image_url'])
        article['author_avatar_url'] = self.img_download(url=article['author_avatar_url'])

        # 处理文章正文中的图片链接

    @staticmethod
    def render_article_to_html(article):
        """ 将字典对象表示的 article 用模板引擎渲染成一个html页面
        返回 HTMl 源码
        """
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='./', encoding='utf-8'))
        template = env.get_template('article.html')

        return template.render(article=article)

