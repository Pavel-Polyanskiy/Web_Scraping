#The goal of this project is to scrape the book website from https://bookshop.org/books?keywords=python and retrieve the book title,
#author, link to the detailed description and prices(both with and without discounts if there are any)

#importing libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://bookshop.org/books?keywords=python' #basic url with no page numbers
with open('index.html', "w") as file:
    file.write(requests.get(url).text)


html = requests.get(url)
soup = BeautifulSoup(html.content)

#number of pages:
pages_number = int(soup.find('nav', class_ = 'pagination').find('span', class_ = 'last').find('a', href = True)['href'][-3:])
#url for multiple pages: 'https://bookshop.org/books?keywords=python&page=100'

#empty lists for each attribute
titles = []
authors = []
prices = []
links = []
discounts = []


#for each page
for page in range(1, pages_number + 1):
    url = f"https://bookshop.org/books?keywords=python&page={page}"
    html = requests.get(url)
    soup = BeautifulSoup(html.content)
    #for each book item in the list
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

    print(f'Page #{page} is scraped!') # for tracing the process

#converting to dataframe
df = pd.DataFrame({'book_title' : titles, 'author' : authors, 'link' : links, 'price_no_disc' : prices, 'price_with_disc' : discounts})

#checking the head of df
df.head()

#converting to csv
df.to_csv('books_scraped.csv')