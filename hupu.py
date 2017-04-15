import string
import urllib
import urllib2
import re
import codecs
import lxml
from lxml import etree
from lxml import html
import xmllib
import thread
import time
#from scrapy.spiders import Spider  
#from scrapy.selector import Selector 
import pdb
import json
import os


class nba_stats():
    def __init__(self):
        self.file = None
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent' : self.user_agent }
        self.response = ''

    def getTarget(self):
        url = "https://nba.hupu.com" 
        request = urllib2.Request(url,headers = self.headers)
        response = urllib2.urlopen(request)
        response = ''.join(response)
        sel = response
        sel = etree.HTML(sel)
        links1 = sel.xpath('//*[@id="nbaScoreTab_div0"]/div[@class="gamespace_list_no"]/table/tbody/tr[1]/td[2]/span/a/text()')
        links2 = sel.xpath('//*[@id="nbaScoreTab_div0"]/div[@class="gamespace_list_no"]/table/tbody/tr[1]/td[3]/span/a/text()')
        links3 = sel.xpath('//*[@id="nbaScoreTab_div0"]/div[@class="gamespace_list_no"]/table/tbody/tr[1]/td[4]/span/a/text()')
        output_file1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_guest.json')
        output_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_stats.json')
        output_file3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_host.json')
        for i in range(len(links1)):
            print links1[i] + links2[i] + links3[i]
        with open(output_file1, 'w') as out_file1:
            json.dump(links1, out_file1)
        with open(output_file2, 'w') as out_file2:
            json.dump(links2, out_file2)
        with open(output_file3, 'w') as out_file3:
            json.dump(links3, out_file3)
stats = nba_stats()
stats.getTarget()  
