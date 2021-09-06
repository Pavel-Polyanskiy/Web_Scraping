#importing libraries
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
import csv
import numpy as np
import re

#PART 1: Selenium
#Extracting all HTML code for each of 12 pages with Selenium:

#setting options
options = webdriver.ChromeOptions()
#using headless mode to disable the launch of the browser explicitly
options.add_argument('headless')

#initializing the timer for scraping 
start_time = time.time()
try:
    driver = webdriver.Chrome(executable_path='/Users/polyanaboss/Desktop/chromedriver', options = options) 
    driver.get('https://www.nba.com/players')
    time.sleep(2)
    driver.find_element_by_id('onetrust-accept-btn-handler').click() #accepting all cookies by clicking on the correspondent button
    time.sleep(5)
    #1st page is scraped separately because there is no need to click on the "next" button
    with open(f'/Users/polyanaboss/Desktop/selenium_practice/nba_players/data/page_1.html', 'w') as html:
        html.write(driver.page_source) #writing the file for the page
    time.sleep(3)
    #pages 2-12:
    for i in range(2, 13):
        driver.find_elements_by_class_name('Pagination_button__1MPZe')[1].click() #clicking on the next page
        time.sleep(3)
        with open(f'/Users/polyanaboss/Desktop/selenium_practice/nba_players/data_experimental/page_1_{i}.html', 'w') as html:
            html.write(driver.page_source)
        time.sleep(3)
  
except Exception as ex:
    print(ex)
finally:
    driver.quit()
    driver.close()

finished_time = time.time() - start_time
print(f'Total time spent for scraping html files: {finished_time}') #around 85 seconds here

#PART 2: Beautiful Soup and Requests

start_time_2 = time.time() #starting the next timer
for page in range(1, 13):
    with open(f'data/page_{page}.html') as html: #opening each page HTML file and creating BS4 object
        src = html.read() 

    soup = BeautifulSoup(src)
        
    table = soup.find('table') #table of players
    df = pd.read_html(str(table), flavor = 'bs4')[0] #into pandas dataframe
    links_to_profile = [] #getting all links to personal profiles of the players
    for i in range(len(df)):
        if page == 1: #for the first page we are required to add the domain to the link we extracted 
            link = 'https://www.nba.com' + soup.find_all('td', class_ = 'primary text RosterRow_primaryCol__19xPQ')[i].find('a', href = True)['href'][:-1]
            links_to_profile.append(link) #appending to the total list
        else: #for the rest pages no need to add domain
            link = soup.find_all('td', class_ = 'primary text RosterRow_primaryCol__19xPQ')[i].find('a', href = True)['href'][:-1]
            links_to_profile.append(link)

    df['links'] = links_to_profile #assigning the links to the dataframe 

    all_data = [] #now we will visit each player profile and find info(of there is any)  about his last 5 games
    #all_data = pd.Dataframe(columns = ['Game Date', 'Matchup', 'W/L', 'MIN', 'PTS'])
    for i, link in enumerate(links_to_profile, 1):
        html = requests.get(link) #reading the link and creating soup
        soup_personal = BeautifulSoup(html.content)
        try: #trying to find the last 5 games
            table = soup_personal.find('table')
            last_5 = pd.read_html(str(table), flavor = 'bs4')[0].iloc[:, :5]
            last_5['links'] = link #assigning the link for the future concatenation
            all_data.append(last_5)
        except: #if the player did not play any game then the dataset with "no data" columns will be appended
            errors = ['No data'] * 5 
            last_5 = pd.DataFrame({'Game Date' : errors, 'Matchup' : errors, 'W/L' : errors, 'MIN' : errors, 'PTS' : errors, 'links' : link})
            all_data.append(last_5)
        print(f'Last 5 games of Player #{i + 50 * page - 50} are scraped') #for tracing the process of each player out of 572
    df1 = pd.DataFrame(columns = ['Game Date', 'Matchup', 'W/L', 'MIN', 'PTS', 'links']) #concatenating all tables about last 5 games
    for table in all_data:
        df2 = pd.DataFrame(table)
        df1 = pd.concat((df1, df2), axis = 0)
        df1.reset_index(drop = True, inplace = True) #reseting the index


    df_final = pd.merge(df,df1,on='links',how='right') #concatenating the initial dataset about players with their games via right join
    df_final.to_csv(f'data_csv/page_{page}.csv') #converting each of 12 datasets to csv file to specific folder
    print(f"PAGE #{page} IS DONE!") #for tracing the process of each page out of 12

finished_time2 = time.time() - start_time_2
print(f'Total time spent for creating 12 csv files: {finished_time2}') #about 480 seconds here

#creating the final dataset
nba_players_data = pd.DataFrame(columns = pd.read_csv(f'data_csv/page_2.csv').columns) #getting the list of columns from the random df
for i in range(1,13): #for each page the csv file is downloaded to pandas df and then appended to the final dataframe
    if i != 8 and i != 11: #due to some unexplainable reasons files with 8 and 11 pages have defected column names, that's why i treated them separately
        df = pd.read_csv(f'data_csv/page_{i}.csv')
        nba_players_data = pd.concat((nba_players_data, df), axis = 0)
    else:
        df = pd.read_csv(f'data_csv/page_{i}.csv').iloc[:, :15] #taking only necessary columns
        df.columns = nba_players_data.columns
        nba_players_data = pd.concat((nba_players_data, df), axis = 0)

nba_players_data.drop(columns = ['Unnamed: 0'], axis = 1, inplace = True) #droping unnecessary column
nba_players_data.reset_index(drop = True, inplace = True) #reseting the index

nba_players_data['Height'] = nba_players_data['Height'].str.replace('-', '.').astype('float64') #replacing - with . and changing to float type
names = [] #now we will split name and last name that were extracted in camelcase format via regex
for i in nba_players_data['Player']:
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(i)) #splitting name and surname
    names.append(name)

nba_players_data['Player'] = names #reassigning player names

#finally, converting the dataframe to csv format
nba_players_data.to_csv('/Users/polyanaboss/Desktop/selenium_practice/nba_players/nba_players_data.csv')
