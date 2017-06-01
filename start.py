# -*-coding:utf-8-*-

from zhuanlan import ZhuanLan
from session import session as s
import pdfkit
import platform
from io import StringIO


def correct_filename(filename):
    """修正文件名
    例如Windows下的文件名不能包含英文符号< > / \ | : " * ?
    :return: 合格的文件名
    """
    replace_table = {':': '：', '?': '？', '<': '', '>': '', '/': '', '\\': '',
                     '"': '“', '|': ' ', '*': ''}
    if platform.system() == 'Windows':
        f = StringIO()
        for c in filename:
            f.write(replace_table.get(c, c))

        return f.getvalue()

    return filename


def zhuanlan_to_pdf(slug):
    """ 爬取专栏并保存为pdf
    """
    zl = ZhuanLan(s=s, slug=slug)
    cover, article_list = zl.get_result()
    # 保存为文件
    # 保存文件之前要检查文件名是否合格，
    zl.name = correct_filename(zl.name)

    with open(file='./out/'+zl.name+'_cover.html', mode='wb') as f:
        f.write(cover)

    for index, article in enumerate(article_list):
        with open(file='./out/'+zl.name+'_'+str(index)+'.html', mode='wb') as f:
            f.write(article)

    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    options = {'outline-depth': 1}
    pdfkit.from_file(input=['./out/'+zl.name+'_'+str(index)+'.html' for index in range(len(article_list))],
                     cover='./out/'+zl.name+'_cover.html',
                     output_path='./out/'+zl.name+'.pdf',
                     configuration=config,
                     options=options)


if __name__ == '__main__':
    import sys
    slug = sys.argv[1][sys.argv[1].rfind('/')+1:]
    zhuanlan_to_pdf(slug)
