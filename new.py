# -*- coding:utf-8 -*-

import logging
import multiprocessing
import re
import time
from urllib.parse import urljoin
import pymysql
import requests
from fake_useragent import UserAgent
from pyquery import PyQuery as pq

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
BASE_URL = 'https://ssr1.scrape.center'
TOTAL_PAGE = 10

ua = UserAgent()
headers = {'User-Agent': ua.random}


def scrape_page(url):
    logging.info('scraping %s...', url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        logging.error("get invalid status code %s while scraping %s",
                      response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    index_url = f'{BASE_URL}/page/{page}'
    return scrape_page(index_url)


def parse_index(html):
    pattern = re.compile('<a.*?href="(.*?)".*?class="name"')
    items = re.findall(pattern, html)
    if not items:
        return []
    for item in items:
        detail_url = urljoin(BASE_URL, item)
        logging.info('get detail url %s', detail_url)
        yield detail_url


def scrape_detail(url):
    return scrape_page(url)


def parse_detail(html):
    doc = pq(html)
    cover = doc('.cover').attr('src') if doc('.cover').attr('src') else None
    name = doc(".m-b-sm").text() if doc(".m-b-sm").text() else None
    categories = doc(".categories button span").text() if doc(".categories button span").text() else None
    published_pattern = re.compile('(\d{4}-\d{2}-\d{2})\s?上映')
    published = re.search(published_pattern, html).group(1) if re.search(published_pattern, html) else None
    drama = doc('.drama p').text() if doc('.drama p') else None
    score = doc('.score').text() if doc(".score").text() else None
    return {
        "cover": cover,
        "name": name,
        "categories": categories,
        "published": published,
        "drama": drama,
        "score": score
    }


def save_data(data):
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db="spider")
    cursor = db.cursor()
    values = ','.join(['%s'] * len(data))
    # sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
    sql = 'INSERT INTO onespider(cover, name, categories, published, drama, score) VALUES ({values})'.format(
        values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("Successful")
            db.commit()
    except:
        print("Failed")
        db.rollback()
    db.close()


def main(page):
    index_html = scrape_index(page)
    detail_urls = parse_index(index_html)
    for detail_url in detail_urls:
        detail_html = scrape_detail(detail_url)
        data = parse_detail(detail_html)
        logging.info('get detail data %s', data)
        logging.info("saving data to json file")
        save_data(data)
        logging.info("data saved successfully")


if __name__ == '__main__':
    T1 = time.time()
    pool = multiprocessing.Pool()
    pages = range(1, TOTAL_PAGE + 1)
    pool.map(main, pages)
    pool.close()
    pool.join()
    T2 = time.time()
    print("程序运行时间:%s秒" % (T2 - T1))
