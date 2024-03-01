#########################################################

################# Enter Values Here #####################

#########################################################
zipcode = 78412
pages = 1
data_name = "new3"
#########################################################

link = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePage_false_0&formSourceTag=112&newSearchFromOverviewPage=true&inventorySearchWidgetType=AUTO&entitySelectingHelper.selectedEntity=&entitySelectingHelper.selectedEntity2=&zip={}&distance=100&searchChanged=true&modelChanged=true&filtersModified=true".format(zipcode)
raw_data = "_data/_{}_raw.csv".format(data_name)
clean_data = "_data/_{}_clean.csv".format(data_name)

print("\n ** ready to extract data from: {}...{}".format(link[:20], link[-20:]))
print("\n ** pages processing: {}".format(pages))

from bs4 import BeautifulSoup
from seleniumbase import Driver
import pandas
import time

data = []
driver=Driver(uc=True)
driver.get(link)
print("\n 3...")
time.sleep(1)
print("\n 2...")
time.sleep(1)
print("\n 1...")
time.sleep(1)
assert "CarGurus" in driver.title

for i in range(pages):

  html = driver.page_source
  soup = BeautifulSoup(html, "html.parser")
  cars = soup.find_all("div", {"class":"pazLTN"})

  for car in cars:
    row = {}
    title = car.find_all("h4", {"class": "bLgDNy"})
    info = car.find_all("div", {"class": "EeLi0s"})
    deal = car.find_all("div", {"class": "Lxkk9T" })

    for item in info:
        div_elements = item.find_all("dl", {"class": "propertyList"})
        if div_elements:  # Check if any elements were found
            pre_price = div_elements[0].text
            # Your further processing with pre_price
        else:
            # Handle case when no elements are found
            print("No div elements with class 'k4FSCT' found.")

        row["mileage"] = item.find_all("p")[1].text
        seller_ratings = item.find_all("div", {"class": "cg-dealFinder-result-sellerRatingValue"})
    if seller_ratings:
        row["dealer_rating"] = str(seller_ratings[0])
    else:
        row["dealer_rating"] = "No rating found"  # or any default value you prefer
    for item in title:
        row["year"] = title[0].text
        row["make"] = title[0].text

    for item in deal:
        row["market_price"] = item.find_all("p", {"class": "cg-dealfinder-result-deal-imv"})[0].text
        row["days_listed"] = item.find_all("p", {"class": "cg-dealfinder-result-deal-imv"})[1].text

    data.append(row)

    print("\n page {} scraping finished".format(i+1))
    assert "CarGurus" in driver.title

driver.close()
df = pandas.DataFrame(data)
df.to_csv(raw_data, encoding="ascii")
print("\n ** data extraction success!")
print("\n ** raw data added: {}".format(raw_data))


# coding: utf-8

# In[1]:

#########################################################

#################### Data Cleaning ######################

#########################################################

import warnings
warnings.filterwarnings("ignore")

import pandas as pd

data = pd.read_csv(raw_data)
print("\n ** starting cleaning data: {}".format(raw_data))
time.sleep(3)

def remove_dollar_and_comma(string):
    string = string.replace("$","")
    string = string.replace(",","")
    return string

def star_counter(string):
    num = 5 - string.count("star_disabled") - 0.5 * string.count("star_half")
    return num

def print_finish_message(cleanee):
    message = "\n finished cleaning \"{}\"".format(cleanee)
    print(message)
    time.sleep(1)

# extract year from title
data["year"] = data["year"].str[:4]
data["year"] = data["year"].astype("int")
print_finish_message("year")

# extract price
def price_clean(price):
    price = price.split()[0]
    price = remove_dollar_and_comma(price)
    return price
data["price"] = data["price"].apply(price_clean).astype("int")
print_finish_message("price")

# extract market_price
def market_price_clean(market_price):
    market_price = market_price[market_price.index("$"):] 
    market_price = remove_dollar_and_comma(market_price)
    return market_price
data["market_price"] = data["market_price"].apply(market_price_clean).astype("int")
print_finish_message("market_price")

# extract mileage
def mileage_clean(mileage):
    mileage = mileage[mileage.index(" ")+1:]
    mileage = mileage[:mileage.index(" ")]
    mileage = mileage.replace(",","")
    return(mileage)
data["mileage"] = data["mileage"].apply(mileage_clean).astype("int")
print_finish_message("mileage")

# extract make
def make_clean(make):
    make = make.split()[1]
    if make == "Land":
        make = "Land Rover"
    return make
data["make"] = data["make"].apply(make_clean).astype("str")
print_finish_message("make")

# calculate rating
def dealer_rating_clean(dealer_rating):
    return star_counter(dealer_rating)
data["dealer_rating"] = data["dealer_rating"].apply(dealer_rating_clean).astype("float")
print_finish_message("dealer_rating")

# extract days_listed
def days_listed_clean(days_listed):
    days_listed = days_listed.split()[0]
    if days_listed == "<":
        days_listed = 1
    return days_listed
data["days_listed"] = data["days_listed"].apply(days_listed_clean).astype("int")
print_finish_message("days_listed")

# create column state
data["state"] = data["address"][:]
data["city"] = data["address"][:]
print_finish_message("address")

address = data["address"]
state = data["state"]
city = data["city"]

print("\n data reformatting...")    
for i in range(len(state)):
    city[i] = address[i][:address[i].index(",")]
    state[i] = address[i][address[i].index(","):]
    state[i] = state[i].replace(", ","")

# remove address column
data = data.drop("address", 1)

# rearrange columns
cols = ["year", "make", "mileage", "dealer_rating", "days_listed", "price", "market_price", "city", "state"]
data = data[cols]

data.to_csv(clean_data)
print("\n** data cleaning finished")
print("\n** clean data available as {}".format(clean_data))