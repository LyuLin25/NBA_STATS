#!/usr/bin/env python
# coding: utf-8

import datetime
import json
import os
import sys
import time
import re
import Adafruit_DHT
from Waveshare_43inch_ePaper import *
import requests
from lxml import etree
import urllib
import urllib2

#get home temp & humidity
def get_home_air():
    h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    result = {'temp': int(t), 'humidity': int(h), 'update': int(time.time())}
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home_air.json')
    with open(data_file, 'w') as out_file:
        json.dump(result, out_file)
        
#get web weather report   
def get_weather():
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather.json')

    def fail_exit(msg):
        with open(output_file, 'w') as out_file:
            json.dump({'error': msg}, out_file)
        sys.exit(1)

    html = ''
    try:
        r = requests.get('http://weather.sina.com.cn/', timeout=10)
        r.encoding = 'utf-8'
        html = r.text
    except Exception, e:
        fail_exit(unicode(e))

    result = {field: None for field in '''city_name current_temp current_weather
              current_wind current_humidity current_aq current_aq_desc
              today_weather today_temp_low today_temp_hig tomorrow_weather
              tomorrow_temp_low tomorrow_temp_hig tomorrow_wind tomorrow_aq
              tomorrow_aq_desc'''.split()}

    tree = etree.HTML(html)
    rt = tree.xpath('//*[@id="slider_ct_name"]')
    if rt:
        result['city_name'] = rt[0].text
    rt = tree.xpath('//*[@id="slider_w"]//div[@class="slider_degree"]')
    if rt:
        result['current_temp'] = rt[0].text.replace(u'℃', '')
    rt = tree.xpath('//*[@id="slider_w"]//p[@class="slider_detail"]')
    if rt:
        tmp0 = re.sub(r'\s', '', rt[0].text)
        tmp0 = tmp0.split('|')
        if len(tmp0) >= 3:
            result['current_weather'] = tmp0[0].strip()
            result['current_wind'] = tmp0[1].strip()
            tmp1 = re.search(r'([\-\d]+)%', tmp0[2])
            if tmp1 is not None:
                result['current_humidity'] = tmp1.group(1)
        tmp0 = None
        tmp1 = None

    rt = tree.xpath('//*[@id="slider_w"]/div[1]/div/div[4]/div/div[1]/p')
    if rt:
        result['current_aq'] = rt[0].text

    rt = tree.xpath('//*[@id="slider_w"]/div[1]/div/div[4]/div/div[2]/p[1]')
    if rt:
        result['current_aq_desc'] = rt[0].text

    rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[1]/p[3]/img')
    if len(rt) == 1:
        result['today_weather'] = rt[0].get('alt')
    elif len(rt) == 2:
        tmp0 = rt[0].get('alt')
        tmp1 = rt[1].get('alt')
        result['today_weather'] = tmp0
        if tmp0 != tmp1:
            result['today_weather'] += u'转' + tmp1
        tmp0 = None
        tmp1 = None

    rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[1]/p[5]')
    if rt:
        tmp0 = rt[0].text.split('/')
        if len(tmp0) > 1:
            result['today_temp_hig'] = tmp0[0].replace(u'°C', '').strip()
            result['today_temp_low'] = tmp0[1].replace(u'°C', '').strip()
        else:
            result['today_temp_low'] = tmp0[0].replace(u'°C', '').strip()
        tmp0 = None

    rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/p[3]/img')
    if rt:
        tmp0 = rt[0].get('alt')
        tmp1 = rt[1].get('alt')
        result['tomorrow_weather'] = tmp0
        if tmp0 != tmp1:
            result['tomorrow_weather'] += u'转' + tmp1
        tmp0 = None
        tmp1 = None

    rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/p[5]')
    if rt:
        tmp0 = rt[0].text.split('/')
        result['tomorrow_temp_hig'] = tmp0[0].replace(u'°C', '').strip()
        result['tomorrow_temp_low'] = tmp0[1].replace(u'°C', '').strip()
        tmp0 = None

    rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/p[6]')
    if rt:
        result['tomorrow_wind'] = rt[0].text.strip()

    rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/ul/li')
    if rt:
        result['tomorrow_aq'] = rt[0].text
        result['tomorrow_aq_desc'] = rt[1].text

    keys_require = '''city_name current_temp current_weather current_wind
        current_humidity current_aq current_aq_desc today_weather
        today_temp_low tomorrow_weather tomorrow_temp_low tomorrow_temp_hig
        tomorrow_wind'''.split()

    for key in keys_require:
        if not result.get(key):
            fail_exit('can not get key %s' % key)

    result['update'] = int(time.time())
    with open(output_file, 'w') as out_file:
        json.dump(result, out_file)

#get nba stats   
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
       
while True:
    if time.strftime('%S',time.localtime(time.time()))=='00' :
        screen_width = 800
        screen_height = 600
        screen = Screen('/dev/ttyAMA0')
        screen.connect()
        screen.handshake()

        #screen.load_pic()
        #time.sleep(5)

        screen.clear()
        screen.set_memory(MEM_FLASH)
        screen.set_rotation(1)

        clock_x = 40
        clock_y = 20
        temp_x = 0
        time_now = datetime.datetime.now()
        print time_now
        time_string = time_now.strftime('%H:%M')
        date_string = time_now.strftime('%Y-%m-%d')
        week_string = [u'星期一',u'星期二',u'星期三',u'星期四',u'星期五',u'星期六',u'星期日'][time_now.isoweekday() - 1]
        if time_string[0] == '0':
            time_string = time_string[1:]
            temp_x += 40
            
        for c in time_string:
            bmp_name = 'NUM{}.BMP'.format('S' if c == ':' else c)
            screen.bitmap(clock_x + temp_x, clock_y, bmp_name)
            temp_x += 70 if c == ':' else 100
            
        screen.set_ch_font_size(FONT_SIZE_48)
        screen.set_en_font_size(FONT_SIZE_48)
        screen.text(clock_x + 350 + 150, clock_y + 20, date_string)
        screen.text(clock_x + 350 + 190, clock_y + 80, week_string)

        screen.line(0, clock_y + 160, 800, clock_y + 160)
        screen.line(0, clock_y + 161, 800, clock_y + 161)

        stats = nba_stats()
        stats.getTarget()   
        nba_guest_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_guest.json')
        nba_stats_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_stats.json')
        nba_host_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_host.json')

        team_dict = {u'马刺':'SAS.BMP',u'老鹰':'ATL.BMP',u'开拓者':'POR.BMP',u'勇士':'GSW.BMP',u'骑士':'CLE.BMP',u'灰熊':'MEM:BMP',u'雷霆':'OKC.BMP',u'雄鹿':'MIL.BMP',u'掘金':'DEN.BMP',u'火箭':'HOU.BMP',u'鹈鹕':'NOP.BMP',u'太阳':'PHX.BMP',u'国王':'SAC.BMP',u'湖人':'LAL.BMP',u'快船':'LAC.BMP',u'猛龙':'TOR.BMP',u'活塞':'DET.BMP',u'步行者':'IND.BMP',u'76人':'PHI.BMP',u'尼克斯':'NYN.BMP',u'篮网':'BKN.BMP',u'凯尔特人':'BOS.BMP',u'森林狼':'MIN.BMP',u'爵士':'UTA.BMP',u'黄蜂':'CHA.BMP',u'公牛':'CHI.BMP',u'热火':'MIA.BMP',u'魔术':'ORL.BMP',u'奇才':'WAS.BMP'}

        with open(nba_guest_file, 'r') as guest_file:
            guest_data = json.load(guest_file)
        with open(nba_host_file, 'r') as host_file:
            host_data = json.load(host_file)
        with open(nba_stats_file, 'r') as stats_file:
            stats_data = json.load(stats_file)
        # print guest_data

        spurs_guest = spurs_host = 0

        if u'马刺' in guest_data:
            spurs_guest = 1
            spurs_guest_num = guest_data.index(u'马刺')
            screen.bitmap(20, clock_y + 200, 'SAS.BMP')
            host_name = host_data[spurs_guest_num]
            host_logo = team_dict[host_name]
            screen.bitmap(20, clock_y + 480, host_logo)
            screen.text(40, clock_y + 350, stats_data[spurs_guest_num])
        elif u'马刺' in host_data:
            spurs_host = 1
            spurs_host_num = host_data.index(u'马刺')
            screen.bitmap(20, clock_y + 480, 'SAS.BMP')
            guest_name = guest_data[spurs_host_num]
            guest_logo = team_dict[guest_name]
            screen.bitmap(20, clock_y + 200, guest_logo)
            screen.text(40, clock_y + 350, stats_data[spurs_host_num])
        else:
            screen.bitmap(30, clock_y + 250, 'SAS.BMP')
            screen.text(50, clock_y + 390, 'NO GAME')
            screen.text(60, clock_y + 450, 'TODAY')
        #print go_spurs_go + spurs_guest_num + spurs_host_num

        # if spurs_guest or spurs_host:
            # screen.bitmap(20, clock_y + 200, 'SAS.BMP')
            
        get_home_air()
        get_weather()
        def weather_fail(msg):
            screen.text(10, clock_y + 170, msg)
            screen.update()
            screen.disconnect()
            sys.exit(1)

        weather_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather.json')
        wdata = {}
        try:
            with open(weather_data_file, 'r') as in_file:
                wdata = json.load(in_file)
        except IOError:
            weather_fail(u'ERROR:无法加载天气数据!')

        if wdata.get('error'):
            weather_fail(wdata.get('error'))

        if int(time.time()) - wdata['update'] > 2 * 3600:
            weather_fail(u'ERROR:天气数据已过期!')

        cw = wdata['current_weather']
        bmp_name = {u'晴': 'WQING.BMP', u'阴': 'WYIN.BMP', u'多云': 'WDYZQ.BMP',
                    u'雷阵雨': 'WLZYU.BMP', u'小雨': 'WXYU.BMP', u'中雨': 'WXYU.BMP'}.get(cw, None)
        if not bmp_name:
            if u'雨' in cw:
                bmp_name = 'WYU.BMP'
            elif u'雪' in cw:
                bmp_name = 'WXUE.BMP'
            elif u'雹' in cw:
                bmp_name = 'WBBAO.BMP'
            elif u'雾' in cw or u'霾' in cw:
                bmp_name = 'WWU.BMP'

        if bmp_name:
            screen.bitmap(600, clock_y + 380, bmp_name)

        screen.set_ch_font_size(FONT_SIZE_64)
        screen.set_en_font_size(FONT_SIZE_64)

        margin_top = 20
        weather_y = clock_y + 170
        weather_line_spacing = 10
        weather_line1_height = 64
        weather_line2_height = 42
        weather_line3_height = 64
        weather_line4_height = 64
        weather_text_x = 256 - 30
        weather_line5_x = weather_text_x + 64
        if len(wdata['current_aq_desc']) > 2:
            weather_line5_x -= 80

        screen.text(weather_text_x + 124, weather_y + margin_top, wdata['today_weather'])

        tmp0 = u'{current_temp}℃  {current_humidity} %'.format(**wdata)
        tmp0 = tmp0.replace('1', '1 ')
        screen.text(weather_text_x + 124, weather_y + margin_top +
                    weather_line1_height +
                    weather_line_spacing +
                    weather_line2_height +
                    weather_line_spacing, tmp0)

        try:
            home_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home_air.json')
            hdata = json.load(file(home_data_file, 'r'))
            # print hdata
            if int(time.time()) - hdata['update'] < 120:
                tmp0 = u'{temp}℃ {humidity} %'.format(**hdata)
                print tmp0
                tmp0 = tmp0.replace('1', '1 ')
                screen.text(weather_text_x + 124, weather_y + margin_top +
                            weather_line1_height +
                            weather_line_spacing +
                            weather_line2_height +
                            weather_line_spacing +
                            weather_line3_height +
                            weather_line_spacing, tmp0)
        except Exception, e:
            pass

        screen.text(weather_line5_x + 120, weather_y + margin_top +
                    weather_line1_height +
                    weather_line_spacing +
                    weather_line2_height +
                    weather_line_spacing +
                    weather_line3_height +
                    weather_line_spacing +
                    weather_line4_height +
                    weather_line_spacing,
                    u'{current_aq} {current_aq_desc}'.format(**wdata))

        screen.set_ch_font_size(FONT_SIZE_32)
        screen.set_en_font_size(FONT_SIZE_32)

        screen.text(weather_text_x + 124 - 20 - screen.get_text_width(wdata['city_name'], FONT_SIZE_32),
                    weather_y + margin_top + 10, wdata['city_name'])

        screen.text(weather_text_x + 40, weather_y + margin_top +
                    weather_line1_height +
                    weather_line_spacing +
                    weather_line2_height +
                    weather_line_spacing + 10, u'室外')

        screen.text(weather_text_x + 40, weather_y + margin_top +
                    weather_line1_height +
                    weather_line_spacing +
                    weather_line2_height +
                    weather_line_spacing +
                    weather_line3_height +
                    weather_line_spacing + 10, u'室内')

        screen.text(weather_text_x + 40, weather_y + margin_top +
                    weather_line1_height +
                    weather_line_spacing +
                    weather_line2_height +
                    weather_line_spacing +
                    weather_line3_height +
                    weather_line_spacing +
                    weather_line4_height +
                    weather_line_spacing + 10, u'空气指数')

        if wdata.get('today_temp_hig'):
            fmt = u'{today_temp_hig}~{today_temp_low}℃ {current_wind}'
        else:
            fmt = u'{today_temp_low}℃ {current_wind}'
        msg = fmt.format(**wdata)
        screen.text(weather_text_x + 124, weather_y + margin_top
                    + weather_line1_height + weather_line_spacing + 5, msg)
        weather2_x = 550
        weather2_y = (weather_y + margin_top +
                      weather_line1_height +
                      weather_line_spacing +
                      weather_line2_height +
                      weather_line_spacing)

        screen.update()
        screen.disconnect()