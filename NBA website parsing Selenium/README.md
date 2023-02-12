# The description: 

in this project we would scrape the website containing all relevant information about NBA players.

# How it would look like:

Firsty, we will grab all the information about players available on the page as shown on the screenshot below:

<img src='Screenshot 2021-09-06 at 18.44.21.png'  />

Secondly, we will visit the profile of each player that is represented as follows:

<img src='Screenshot 2021-09-06 at 18.44.41.png'  />


And exract the data about his last 5 appearances 

<img src='Screenshot 2021-09-06 at 18.44.46.png'  />

# Selenium:

The website of interest is dynamic one. It means that while clicking on the next page with other players the link is not being changed. Hence, in order to find the HTML code of all pages with all players we are forced to use Selenium Library. In particular, we will ask webdriver to visit the website, accept all cookies and visit every page together with extracting HTMl code into the file.

# Beautiful Soup:

Then, BS4 will be used in order to find all tables and links needed to fullfil the database.

# Finally:

We will combine all retrieved data into single csv file: **nba_players_data.csv**.

Also, two folders with *html* and *csv* files of each page will be attached.

