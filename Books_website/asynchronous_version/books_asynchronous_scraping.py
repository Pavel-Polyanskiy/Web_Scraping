import json
import time
from bs4 import BeautifulSoup
import datetime
import csv
import asyncio
import aiohttp
import pandas as pd

start_time = time.time()

titles = []
authors = []
prices = []
links = []
discounts = []
async def get_page_data(session, page):
    url = f"https://bookshop.org/books?keywords=python&page={page}" #url with page number

    async with session.get(url=url) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "lxml")

        for box in soup.find_all('div', class_ = 'booklist-book'):
            name = box.find('h2', class_ = 'font-serif-bold lg:pt-4 leading-tight').text.strip()
            link = 'https://bookshop.org/' + box.find('h2', class_ = 'font-serif-bold lg:pt-4 leading-tight').find('a',  href = True)['href']
            author = box.find('h3', class_ = 'text-s').text.strip()
            try: #trying to find price with discount
                price_no_discount  = box.find('div', class_ = 'line-through mr-2 lg:mr-0 text-primary').text.strip()
            except:
                price_no_discount = ""

            #common price with no discount
            price_low = box.find('div', class_ = 'font-sans-bold').text.strip()

            #if there is no discount then these prices are equal
            if price_no_discount == "":
                price_no_discount = price_low

            #appending the values to each list
            titles.append(name)
            authors.append(author)
            prices.append(price_no_discount)
            links.append(link)
            discounts.append(price_low)
            
        print(f'Page #{page} done')


async def gather_data():
    async with aiohttp.ClientSession() as session:
        #response = await session.get(url=url, headers=headers)
        #soup = BeautifulSoup(await response.text(), "lxml")
        #pages_count = int(soup.find("div", class_="pagination-numbers").find_all("a")[-1].text)

        tasks = []

        for page in range(1, 101): #total number of pages
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())

    finish_time = time.time() - start_time
    print(f"Total time spent: {finish_time}")

main()
df = pd.DataFrame({'book_title' : titles, 'author' : authors, 'link' : links, 'price_no_disc' : prices, 'price_with_disc' : discounts})
print(df.head())
