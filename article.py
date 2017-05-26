# -*-coding:utf-8-*-

""" 获取一个知乎专栏中的一篇文章，保持原来的排版，去掉不需要的内容，最终渲染成 html，以便后面转成 pdf
"""

import json
import re
from mako.template import Template
from bs4 import BeautifulSoup
import arrow


class Article:
    """ 爬取单篇文章"""

    def __init__(self, session):
        self.session = session
        self.img_path = './out/img'  # 图片的保存路径
        self.pattern = r'\"[0-9a-zA-Z\-.]{8,64}?\.(jpg|png)\"'

        self.article_template = Template(filename='./template/article.html')

    @staticmethod
    def utc_to_local(utc):
        """ 将一个UTC格式的时间字符串转为本地时间字符串"""
        utc = arrow.get(utc)
        return utc.format('YYYY-MM-DD HH:mm')

    def get_one_article_dict(self, url):
        """ 获取 url 指定的一篇知乎专栏文章
        slug 是知乎专栏文章的唯一识别码
        返回一个字典对象，里面包括文章标题、作者、发布时间、文章内容等
        """

        json_obj = self.session.get(url=url).json()[0]
        article = dict()
        article['title'] = json_obj['title']
        article['title_image_url'] = json_obj['titleImage']
        article['author_name'] = json_obj['author']['name']

        # 获取作者头像url
        author_avatar_template = json_obj['author']['avatar']['template']
        avatar_id = json_obj['author']['avatar']['id']
        author_avatar_url = author_avatar_template.replace('{id}', avatar_id).replace('{size}', 'xs')
        article['author_avatar_url'] = author_avatar_url
        # 发布时间
        article['publishedTime'] = self.utc_to_local(json_obj['publishedTime'])

        # 文章内容
        article['content'] = json_obj['content']

        # 该文章的评论列表url
        article['comments_links'] = 'https://zhuanlan.zhihu.com' + json_obj['links']['comments']
        # 评论数
        article['comments_count'] = json_obj['commentsCount']

        return article

    def _img_download(self, url):
        """ 下载 url 指定的图片并保存到本地，并返回本地路径"""
        # 提取 url 中图片的名称
        if url is None or len(url) == 0:
            return ''
        if url.find('https') < 0:
            url = 'https://pic1.zhimg.com/' + url
            print('66:', url)
        name = url[url.rfind('/')+1:]
        binary_content = self.session.get(url=url).content
        path = self.img_path + '/' + name
        with open(file=path, mode='wb') as f:
            f.write(binary_content)

        return path

    def images_to_local(self, article):
        """ 将 article 中引用到的所有图片下载到本地，并将 url 指向本地图片，方便后面转成 pdf
        需要处理的图片url包括文章标题中的图片，作者头像，以及正文中的图片"""
        article['title_image_url'] = self._img_download(url=article['title_image_url'])
        article['author_avatar_url'] = self._img_download(url=article['author_avatar_url'])

        # 处理文章正文中的图片链接
        def replace(match):
            return self._img_download(match.group(0).strip('\"'))

        article['content'] = re.sub(pattern=self.pattern, repl=replace, string=article['content'])
        # TODO:将正则表达式的模式编译成正则表达式对象，可以提高效率

    @staticmethod
    def handle_lazy_img(article):
        """ 处理正文中的惰性加载图片。因为惰性加载图片是用空白图片占位，后用js代码动态请求图片再替换。
        自己爬取的话，无法执行js代码，所以得自己处理一下"""
        soup = BeautifulSoup(article['content'], 'html5lib')
        noscript_blocks = soup.find_all(name='noscript')
        # 将所有noscript块中的图片地址提取出来，赋值给该块下一个兄弟块的img src属性
        for noscript_block in noscript_blocks:
            # 找到img 子节点
            img_node = noscript_block.find('img')
            if img_node:
                # 修改惰性加载的图片src
                for tag in noscript_block.next_elements:
                    if tag.name == 'img':
                        tag['src'] = img_node['src']
                        break
            # noscript 块不再需要
            noscript_block.decompose()

        article['content'] = str(soup)

    def render_article_to_html(self, article):
        """ 将字典对象表示的 article 用模板引擎渲染成一个html页面
        返回 HTMl 源码
        """
        return self.article_template.render(article=article).encode('utf-8')

    def get_article_html(self, url):
        """ 获取一篇文章最后的HTML源码"""
        article = self.get_one_article_dict(url=url)
        self.images_to_local(article=article)
        self.handle_lazy_img(article=article)
        return self.render_article_to_html(article=article)


if __name__ == '__main__':
    from session import session as s
    a = Article(s)

    with open('out2.html', 'wb') as f:
        f.write(a.get_article_html(url='https://zhuanlan.zhihu.com/api/columns/kls-software-arch-world/posts?limit=1&offset=2'))
