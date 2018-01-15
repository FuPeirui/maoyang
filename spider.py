# -*- coding:utf-8 -*-
import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool    #加入进程池

#获取页面html信息
def get_one_page_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text

        #若网络错误，则返回网络状态码
        print('status_code:' + str(response.status_code))
        return None
    except RequestException:
        print("RequestException")
        return None

#正则表达式里范了一个低级的错误，浪费了很多时间，就是把一个p打成大写的P,说明正则表达式不适合写大量且易调试的程序

def parse_one_page_html(html):
    pattern= re.compile('<dd>.*?board-index.*?">(\d+)</i>'+    #board-index(电影排名）
               '.*?title="(.*?)"'+                             #电影名字
                '.*?data-src="(.*?)"'+                         #图片链接
                '.*?class="star">(.*?)</p>',re.S)              #演员
    items = re.findall(pattern,html)
    for item in items:
        yield {   #返回的是一个生成器对象
            'index': item[0],
            'title': item[1],
            'image': item[2],
            'actor': item[3].strip()[3:]    #strip()移除头尾指定的字符，这里指定的是空格，最后对主演
                                            #进行切片处理
        }

def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        #json将content对象转换成string
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()



def main(offset):
    url = 'http://maoyan.com/board/4?offset='+str(offset)
    html = get_one_page_html(url)
    for item in parse_one_page_html(html):
        print(item)
        write_to_file(item)

if __name__ == '__main__':
    #Pool类可以提供指定数量的进程供用户调用，当有新的请求提交到Pool中时，如果池还没有满，就会创建一个新
    # 的进程来执行请求。如果池满，请求就会告知先等待，直到池中有进程结束，才会创建新的进程来执行这些请求。
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
    pool.close()    #关闭进程池
    pool.join()     #主进程等待子进程的退出

