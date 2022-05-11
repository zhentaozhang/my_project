import logging
import time
import re
import pymysql
import requests
from fake_useragent import UserAgent
from pyquery import PyQuery as pq
import multiprocessing
from bs4 import BeautifulSoup

ua = UserAgent()
headers = {'User-Agent': ua.random}
BASE_URL = "https://movie.douban.com/top250?start={one}&filter="
TOTAL_PAGE = 10
limit = 25


# 共10页，拼接每页的url
def scrape_index(start):
    url = BASE_URL.format(one=(start - 1) * limit)
    return url


# 返回每页的url.text
def scrape_page(url):
    logging.info("scraping %s...", url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        logging.error("get invalid status code %s while scraping %s",
                      response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


# 转换成页
def scrape_detail(url):
    return scrape_page(url)


# 得到具体页的href
def parse_detail(html):
    detail_list = []
    doc = pq(html)
    a = doc(".pic a")
    for href in a.items():
        detail_list.append(href.attr('href'))
    return detail_list


# 请求具体页的html返回网页.text
def scrape_point(point_url):
    try:
        resp = requests.get(point_url, headers=headers)
        return resp.text
    except TypeError:
        print("*" * 20)


# 解析网页，使用pq得到想要的信息
def point_url_detail(point_html):
    doc = pq(point_html)
    title = doc('#content h1 span:first-child').text() if doc('#content h1 span:first-child').text() else None
    star = doc('.rating_self strong').text() if doc('.rating_self strong').text() else None
    runtime = re.compile('property="v:runtime".*>(.*?)</span')
    runtime_1 = re.findall(runtime, point_html) if re.findall(runtime, point_html) else None
    type_0 = re.compile('property="v:genre">(.*?)</span>')
    type_1 = re.findall(type_0, point_html) if re.findall(type_0, point_html) else None
    actor = re.compile('rel="v:starring">(.*?)</a>')
    actor_1 = re.findall(actor, point_html) if re.findall(actor, point_html) else None
    actor_2 = ','.join(actor_1)
    type_2 = ','.join(type_1)
    short_text = doc('.all.hidden').text() if doc('.all.hidden').text() else doc(".indent#link-report span").text()
    return {
        "title": title,
        "actor": actor_2,
        "short_text": short_text,
        "runtime": runtime_1,
        "type": type_2,
        "star": star
    }


def save(data):
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='spider')
    cursor = db.cursor()
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO top250(title, actor, short_text,runtime, type,star) VALUES ({values})'.format(values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("Successful")
            db.commit()
    except:
        print('Failed')
        db.rollback()
    db.close()


def main(page):
    index_html = scrape_index(page)
    detail_html = scrape_page(index_html)
    detail_point_lists = parse_detail(detail_html)
    # print(detail_point_lists)
    for i in detail_point_lists:
        resp_point = scrape_point(i)
        data = point_url_detail(resp_point)
        save(data)
        logging.info("data saved successfully")


if __name__ == '__main__':
    t1 = time.time()
    try:
        pool = multiprocessing.Pool()
        pages = range(1, TOTAL_PAGE + 1)
        pool.map(main, pages)
        pool.close()
        pool.join()
    except TypeError:
        pass
    t2 = time.time()
    print(t2 - t1)
