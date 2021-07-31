#Importing the libraries
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from dateparser import parse
from urllib.parse import urljoin
from dateparser.search import search_dates
from selenium import webdriver
from time import sleep
import pandas as pd

#Initializing the Session
session = HTMLSession()

base_url = 'https://www.9news.com.au/'

#Crawling Sections from news Sites
#SECTION_LINKS
def get_section_links(retry = 3):
    
    session = HTMLSession()
    r = session.get(base_url, timeout = 180)
    soup = BeautifulSoup(r.content, 'lxml')
    section = soup.find('ul',{'class':'Header__SiteHeaderNavItems-b5cu1y-0 CHVxa'}).find_all('a')
    section_links = [urljoin(base_url, x.attrs['href']) for x in section]
    section_links = list(set(filter(lambda x: x.startswith('https://www.9news.com.au/'), section_links)))
    ignore_list = ['https://www.9news.com.au/national/today-in-history-new-pictures-gallery-famous-historical-images-crime-sport-celebrity-world-news-global-events/349cc469-40ad-49f0-b748-c2f482c4b0b5',
                   'https://www.9news.com.au/weather/nsw/sydney',
                   'https://www.9news.com.au/weather/sa/adelaide',
                   'https://www.9news.com.au/national/australia-breaking-news-live-coronavirus-updates-headlines-june-9-2021-scott-morrison-china-trade-threat/87ecf971-a99e-4265-86c4-bc68ec1a2678',
                   'https://www.9news.com.au/videos',
                   'https://www.9news.com.au/contact-us',
                   'https://www.9news.com.au/about-us',
                   'https://www.9news.com.au/weather',
                   'https://www.9news.com.au/meet-the-team/digital',
                   'https://www.9news.com.au/videos/watch-live',
                   'https://www.9news.com.au/weather/vic/melbourne',
                   'https://www.9news.com.au/app',
                   'https://www.9news.com.au/weather/qld/brisbane',
                   'https://www.9news.com.au/meet-the-team/national',
                   'https://www.9news.com.au/60-minutes',
                   'https://www.9news.com.au/royal-family',
                   'https://www.9news.com.au/motoring',
                   'https://www.9news.com.au/national/australia-breaking-news-live-coronavirus-updates-headlines-july-5-2021-covid19-vaccine-nsw-lockdown-case-numbers/d0e94ec8-b0f0-425d-a3b7-a9808c02a114',
                   'https://www.9news.com.au/just-in',
                   'https://www.9news.com.au/national/australia-breaking-news-live-coronavirus-updates-headlines-july-9-2021-covid19-sydney-lockdown-cases-vaccine/a8792af6-90c0-47cb-b6a4-e717365d07e2']
    section_links = [url for url in section_links if url != base_url and url not in ignore_list]
    return section_links
section_links = get_section_links()

#Crawling Page 
#ARTICLE
def get_article(url, retry = 3):
    #for url in article_links: break 
    r = session.get(url, timeout=180)
    soup = BeautifulSoup(r.content, 'lxml')
    #article = soup.find('article')
    row={}
    row['title'] = soup.find('h1').text.strip()
    row['pubDate'] = search_dates(soup.find('div',{'class':'article__header'}).text.strip())[0][1]
    row['description'] = '/n'.join([p.text.strip() for p in soup.find('div',{'class':'article__body-croppable'}).find_all('span')])
    row['link'] = url
    return row

#Crawling Articles
# ARTICLE LINKS
def get_article_links_frm_page(soup, retry = 3):
    #for url in section_links: break
    r = session.get(url, timeout = 180)
    soup = BeautifulSoup(r.content, 'lxml')
    articles = [urljoin(base_url, x.find('a').attrs['href']) for x in soup.find('div',{'class':'feed__stories'}).find_all("article")]
    
    article_links=[]
    for article in articles: #break
        try:
            row = get_article(article)
            if not row:
                continue
            date = row['pubDate']
            title = row['title']
            
            if date > upto:
                article_links.append(row)
            elif date == upto:
                if title not in titles:
                    article_links.append(row)
            else:
                return article_links, True
        except:
            pass
    if len(article_links) > 0:
        return article_links, False
    return article_links, True

#Pagination Using Selenium
def get_article_links(url):
    article_links = []
       
    driver = webdriver.Chrome()
    driver.get(url)
    while True:
        #find last _article
        e = driver.find_elements_by_xpath("//div[@class='feed__stories']//h3")[-1]
        link = e.find_element_by_tag_name('a').get_attribute('href')
        row = get_article(link)
        try:
            if row['pubDate'] >= upto:
                load_more = driver.find_element_by_xpath("//div[@class='feed__load-more']")
                load_more.click()
        except:
            break
        else:
            break
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    sleep(0.1)
    pg_article_links, last_page = get_article_links_frm_page(soup)
    article_links.extend(pg_article_links)
    driver.quit()
    return article_links

# Crawl Articles 
upto = parse('10 May 2021')
titles = []
article_links = []
for url in section_links:
    article_links.extend(get_article_links(url))

NineNews = pd.DataFrame(article_links)
NineNews.to_csv("NineNews.csv")






























































































