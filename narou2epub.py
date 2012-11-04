#-*- coding: utf-8 -*-
import sys
import fileinput

def create_archive(url):
    import lxml.html
    import urllib2
    import uuid
    import os
    import time
    import shutil
    import zipfile
    import string
    from mako.template import Template

    html_list = urllib2.urlopen(url).read()
    time.sleep(2)
    root = lxml.html.fromstring(html_list)
    uuid = uuid.uuid1()

    try:
        os.makedirs(os.path.join('./', 'tmp'))
    except OSError:
        pass

    try:
        os.makedirs(os.path.join('./tmp', 'META-INF'))
    except OSError:
        pass
    try:
        os.makedirs(os.path.join('./tmp', 'OEBPS'))
    except OSError:
        pass


    
    title = root.xpath('//*[@class = "series" ]')
    if title == []:
        title = root.xpath('//*[@class = "novel_title" ]')[0].text.strip()
    else:
        title = root.xpath('//*[@class = "series" ]')[0].tail.strip()

    author = root.xpath('//*[@class = "novel_writername" ]/a')
    if author == []:
        author = root.xpath('//*[@class = "novel_writername" ]')[0].text
        author = author.lstrip("作者：")
        author = author.strip()
    else:
        author = root.xpath('//*[@class = "novel_writername" ]/a')[0].text

    ex = root.xpath('//*[@class = "novel_ex" ]')[0].text

    subtitles = root.xpath('//*[@class="long_subtitle"]')
    if subtitles == []:
        subtitles = root.xpath('//*[@class = "chapter" or @class = "period_subtitle"]')
        i=0
        for subtitle in subtitles:
            if list(subtitle) == []:
                subtitles[i] = subtitle.text
            i = i+1



    path = "./[" + author + "] " + title
    
    print title + "　著:" + author + "　を取得開始します"
    
    i = 1
    for index, subtitle in enumerate(subtitles):
        if isinstance(subtitle, lxml.html.HtmlElement):
            html_novel = urllib2.urlopen(url+str(i)).read()
            time.sleep(2)
            novel_tmp = lxml.html.fromstring(html_novel)
            novel = lxml.html.tostring(novel_tmp.xpath('//*[@id = "novel_view"]')[0],encoding="utf-8",method="xml",pretty_print="True")
            fout = open(os.path.join('./tmp/', 'OEBPS', 'content'+str(index)+'.html'), 'w')
            tmpl = Template(filename="./templates/content.html",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
            fout.write(tmpl.render(title=title, subtitle=subtitle[0].text, novel=novel))
            fout.close()
            print "『"+ subtitle[0].text +"』" + u"取得中..."
            i = i+1
        else:
            fout = open(os.path.join('./tmp/', 'OEBPS', 'content'+str(index)+'.html'), 'w')
            tmpl = Template(filename="./templates/chapter.html",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
            fout.write(tmpl.render(title=title, chapter=subtitle))
            fout.close()
       
       
   


    fout = open(os.path.join('./tmp/', 'OEBPS', 'content.opf'), 'w')
    tmpl = Template(filename="./templates/content.opf",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
    fout.write(tmpl.render(title=title, author=author, uuid = uuid, subtitles=subtitles))
    fout.close()

    i = 0
    for subtitle in subtitles:
        if isinstance(subtitle, lxml.html.HtmlElement):
            subtitles[i] = subtitle[0].text
        i = i+1


    fout = open(os.path.join('./tmp/', 'META-INF', 'container.xml'), 'w')
    tmpl = Template(filename="./templates/container.xml",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
    fout.write(tmpl.render())
    fout.close()

    fout = open(os.path.join('./tmp/', 'OEBPS', 'toc.ncx'), 'w')
    tmpl = Template(filename="./templates/toc.ncx",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
    fout.write(tmpl.render(uuid=uuid, title=title, subtitles=subtitles))
    fout.close()

    fout = open(os.path.join('./tmp/', 'OEBPS', 'cover.html'), 'w')
    tmpl = Template(filename="./templates/cover.html",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
    fout.write(tmpl.render(title=title, author=author))
    fout.close()

    fout = open(os.path.join('./tmp/', 'OEBPS', 'ex.html'), 'w')
    tmpl = Template(filename="./templates/ex.html",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
    fout.write(tmpl.render(title=title,ex=ex))
    fout.close()

    fout = open(os.path.join('./tmp/', 'OEBPS', 'stylesheet.css'), 'w')
    tmpl = Template(filename="./templates/stylesheet.css",input_encoding = "utf-8", output_encoding="utf-8",encoding_errors="replace")
    fout.write(tmpl.render())
    fout.close()

    '''Create the ZIP archive.  The mimetype must be the first file in the archive 
    and it must not be compressed.'''

    epub_name = '%s.epub' % os.path.basename(path)
    cwd = os.getcwd()
    os.chdir('./tmp')    
    print u"圧縮開始：" + epub_name
    epub = zipfile.ZipFile("../"+epub_name, 'w')
    epub.write("../templates/mimetype","mimetype", compress_type=zipfile.ZIP_STORED)

    for p in os.listdir('.'):
        if os.path.isdir(p):
            for f in os.listdir(p):
                epub.write(os.path.join(p, f), compress_type=zipfile.ZIP_DEFLATED)

    epub.close()
    print u"圧縮終了：" + epub_name
    os.chdir(cwd)
    shutil.rmtree('./tmp')
    return epub_name


if __name__ == '__main__':
    for url_list in fileinput.input():
        create_archive(url_list.rstrip())
