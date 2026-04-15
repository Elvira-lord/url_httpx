# 实现:  5.批量url探活+链接提取
import os.path

import openpyxl

标题 = "\033[33m" + r"""
.__       __     __                       ________  
|  |__  _/  |_ _/  |_ ______  ___  ___    \\_____  \\ 
|  |  \ \   __\   __\____ \ \  \/  /     /  ____/ 
|   Y  \ |  |   |  |  |  |_> > >    <     /       \ 
|___|  / |__|   |__|  |   __/ /__/\_ \ /\ \_______ \
     \/               |__|          \/ \/         \/
"""+ "\033[0m"+"\033[31m"+r"""
[*]version:2.0.0
"""

print(标题)

import requests
import random
import re

ua=[
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
]


#这里是用来读取文件的
class file_read():

    def file_url(self):
        file_name="url.txt"
        with open(file_name,'r',encoding='utf-8') as f:
            urls=f.read().splitlines()
        return sorted(list(urls))    #这个用来返回文件中的url

    def file_classified(self):  #来分类这些url
        url_s=self.file_url()
        # print(url_s)
        """
        一般分为 ip/纯域名、加http的、加https的、域名
        """
        http=[]    #放http
        https=[]    #放https
        ip=[]    #放ip/域名
        for url in url_s:
            if url.startswith('http://'):
                http.append(url)
                https.append(url.replace('http://', 'https://'))
                # ip.append(url.replace('http://', ''))
            elif url.startswith('https://'):
                https.append(url)
                http.append(url.replace('https://', 'http://'))
                # ip.append(url.replace('https://', ''))
            else:
                # ip.append(url)    #不要纯域名的
                https.append('https://'+url)
                http.append('http://'+url)
        total=http+https+ip    #用来放总的
        total_url=sorted(list(set(total)))
        return total_url



#请求+页面链接提取
class request_url():
    def __init__(self):
        self.url = None
        self.content = None

    def req_url(self,url):
        try:
            self.url = url
            response = requests.get(url, headers={'User-Agent': random.choice(ua)}, timeout=2.5)
            response.encoding = 'utf-8'
            self.content = response.text
            try:
                title = re.findall(r'<title>(.*?)</title>', response.text)[0]
            except:
                title='-'
            server = str(response.headers.get('Server'))
            protocol = url.split('://')[0] if '://' in url else '-'
            return [url, response.url, self.extract_host(url), response.status_code, len(response.text), title, server, protocol]
            #['请求url', '响应url', 'host', 响应码, 响应长度, 'title', 'Server', 'protocol']
        except:
            self.content = None  # 确保content被设置为None
            protocol = url.split('://')[0] if '://' in url else '-'
            return [url, url, self.extract_host(url), 0, 0, '-', '-', protocol]

    def link_url(self):
        # 如果内容为空或None，直接返回空结果
        if not self.content:
            return self.domain_url(), []

        re_rule1=r'href=([\'"])(.*?)\1'
        re_rule2=r'src=([\'"])(.*?)\1'
        #这里可以继续加正则，然后继续拼接
        url=re.findall(re_rule1,self.content)
        url+=re.findall(re_rule2,self.content)
        url_list=[]
        for i in range(len(url)):
            #过滤
            if url[i][1].startswith('http://'):
                houzui=url[i][1][7:].replace('///','/').replace('//','/')
                url_list.append('http://'+houzui)
            elif url[i][1].startswith('https://'):
                houzui=url[i][1][8:].replace('///','/').replace('//','/')
                url_list.append('https://'+houzui)
            elif url[i][1].startswith('/'):
                houzui=url[i][1].replace('///','/').replace('//','/')
                url_list.append(self.domain_url()+houzui)


        return self.domain_url(),sorted(list(url_list))

        # 返回域名
    def domain_url(self):
        if self.url.startswith('http:'):
            domain_u=re.findall(r'http://[^/]+',self.url)
        elif self.url.startswith('https:'):
            domain_u=re.findall(r'https://[^/]+',self.url)
        else:
            domain_u=['null']
        return domain_u[0]

    # 提取host（域名:端口）
    def extract_host(self, url):
        try:
            if url.startswith('http://'):
                host_part = url[7:].split('/')[0].split('?')[0]
            elif url.startswith('https://'):
                host_part = url[8:].split('/')[0].split('?')[0]
            else:
                host_part = url.split('/')[0].split('?')[0]
            return host_part
        except:
            return 'null'

    def display(self,response):
        #['请求url', '响应url', 'host', 响应码, 响应长度, 'title', 'Server', 'protocol']
        if str(response[3]).startswith('2'):
            print(f'\033[32m[{response[3]}] -- [{response[4]}] {response[1]}  [title]:{response[5]}   [server]:{response[6]}   [protocol]:{response[7]}\033[0m')
        elif str(response[3]).startswith('3'):
            print(f'\033[34m[{response[3]}] -- [{response[4]}] {response[1]}  [title]:{response[5]}   [server]:{response[6]}   [protocol]:{response[7]}\033[0m')
        elif str(response[3]).startswith('4'):
            print(f'\033[31m[{response[3]}] -- [{response[4]}] {response[1]}  [title]:{response[5]}   [server]:{response[6]}   [protocol]:{response[7]}\033[0m')
        elif str(response[3]).startswith('5'):
            print(f'\033[33m[{response[3]}] -- [{response[4]}] {response[1]}  [title]:{response[5]}   [server]:{response[6]}   [protocol]:{response[7]}\033[0m')
        elif str(response[3]).startswith('0'):
            print(f'\033[35m[{response[3]}] -- [{response[4]}] {response[1]}  [title]:{response[5]}   [server]:{response[6]}   [protocol]:{response[7]}\033[0m')
        else:
            print(f'[{response[3]}] -- [{response[4]}] {response[1]}  [title]:{response[5]}   [server]:{response[6]}   [protocol]:{response[7]}')


class save():

    def save (self,url_list):
        if not os.path.exists('result'):
            os.mkdir('result')
        if not os.path.exists('result/url.xlsx'):
            wb=openpyxl.Workbook()
            wb.save('result/url.xlsx')
        if os.path.getsize('result/url.xlsx')<=10240:
            wb=openpyxl.load_workbook('result/url.xlsx')
            ws=wb.active
            ws.title='url'
            if ws['A1'].value==None:
                ws['A1']='request_url'
                ws['B1']='response_url'
                ws['C1']='host'
                ws['D1']='status_code'
                ws['E1']='length'
                ws['F1']='title'
                ws['G1']='server'
                ws['H1']='protocol'
                wb.save('result/url.xlsx')
        wb = openpyxl.load_workbook('result/url.xlsx')
        ws = wb.active
        for url in url_list:
            ws.append(url)
        wb.save('result/url.xlsx')

    def save_source(self,source_url_list):
        if not os.path.exists('result'):
            os.mkdir('result')
        for domain_url,source_url_list in source_url_list.items():
            with open(f'result/{domain_url.replace('http://','').replace('https://','')}.txt', 'a', encoding='utf-8') as f:
                for url in source_url_list:
                    f.write(url+'\n')

url=file_read().file_classified()  #获取全部url（处理过了）
url_list=[]     #用来存储原来的url的响应

source_url_list={}  #源码中爬取到的链接

# 用于跟踪每个域名的协议信息
protocol_tracker = {}

for u in url:
    # print(f'{u}')   #每个链接
    req=request_url()
    response1=req.req_url(u)   #获取响应啥的
    # print(response1)
    if u[:5] == response1[0][:5] and response1[3] != 0:   #只存储响对应的协议的url
        host = response1[2]
        protocol = response1[7]

        # 跟踪协议信息
        if host not in protocol_tracker:
            protocol_tracker[host] = {'http': False, 'https': False, 'responses': []}

        if protocol == 'http':
            protocol_tracker[host]['http'] = True
        elif protocol == 'https':
            protocol_tracker[host]['https'] = True

        protocol_tracker[host]['responses'].append(response1)

        req.display(response1)
        domain_url,source_url=req.link_url()
        source_url_list[domain_url]=sorted(list(set(source_url)))

# 处理协议信息并生成最终结果
final_results = []
for host, info in protocol_tracker.items():
    if info['http'] and info['https']:
        protocol_str = 'http / https'
    elif info['http']:
        protocol_str = 'http'
    elif info['https']:
        protocol_str = 'https'
    else:
        protocol_str = '-'

    # 更新所有响应的协议信息
    for response in info['responses']:
        response[7] = protocol_str
        final_results.append(response)

url_list = final_results

# print(url_list)   #这个用来后面保存文件，探活【基本功能】
# print(source_url_list)     #这个用来后面保存文件,字典，保存每个源代码的内提取的链接

#保存基本的探活文件
save_file=save()
save_file.save(url_list)

#保存额外提取的源代码链接
save_file.save_source(source_url_list)

