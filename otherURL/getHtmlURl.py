import os,sys
from posixpath import split

father_path=os.path.abspath(os.path.dirname(__file__)+os.path.sep+"..")
sys.path.append(father_path)


from getWeChatPic import InitRequest





class LHtmlUrl(InitRequest):

    def __init__(self) -> None:
        super().__init__()

    def get_item(self,soup,tag):
        for item in soup:
            # if 
            if hasattr(item,'find_all') and tag:
                yield item.find_all(tag)
            else:
                yield item
    
    def lhtml(self,html):
        soup = self._check_build(html)
        soup_art=self.get_item(soup.find_all('article'),'li')
        urls = self.get_item(soup_art,'')
        return urls

here_dir = os.path.dirname(__file__)
html_p = os.path.join(here_dir,'example.html')
url_md = os.path.join(here_dir,'urls.md')
x = LHtmlUrl()

MD_HEAD ='''---
title: tg
author: https://github.com/congcong0806
date: '2022-02-18'
---
'''
MD_H3='### '
MD_H4='#### '
def filter_url(itm):
    return '\n{}{}'.format(MD_H3,itm) if "http" not in itm else '\n{}{}\n> http{}'.format(MD_H4,itm.split("http")[0],itm.split("http")[1])
with open(url_md,'w',encoding='utf-8') as wf:
    wf.writelines(MD_HEAD)
    with open(html_p,'r' ,encoding='utf-8') as rf:
        html_txt = rf.read()
        urls = x.lhtml(html_txt)
        for item in urls:
            wf.writelines([filter_url(itm.text) for itm in item])

