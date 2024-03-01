from requests_html import HTMLSession

# Variables used in the link for searches
zipcode = 78412
distance = 100
makes = 'chevrolet'
model = ''
page= '2'
stockType = 'used'
sort = 'best_match_desc'
priceMax = ''
priceMin = ''
yearMax = ''
yearMin = ''

# add a feature that goes through pages and adds onto the txt file or makes more txt files '&page={}'
url = 'https://www.cars.com/shopping/results/?stock_type=all&page={}&page_size=100&sort={}&makes%5B%5D={}&models%5B%5D={}&stock_type={}&maximum_distance={}&zip={}'.format(page, sort, makes, model, stockType, distance, zipcode)
s = HTMLSession()
r = s.get(url)

# Check if the elements exist before trying to find them
titles = r.html.find('a.vehicle-card-link.js-gallery-click-link h2.title')
mileages = r.html.find('div.vehicle-details div.mileage')
prices = r.html.find('div.price-section.price-section-vehicle-card span.primary-price')
locations = r.html.find('div.vehicle-dealer')

# Check if all lists are not empty before zipping
if titles and mileages and prices and locations:
    # Open a file in write mode
    with open('car_info.txt', 'w') as file:
        # Zip the lists together and iterate over the zipped result
        for title, mileage, price, location in zip(titles, mileages, prices, locations):
            # Write the information to the file
            file.write(f"{title.text}, {mileage.text}, {price.text}, {location.text}\n\n")
    print("Data written to car_info.txt file.")
else:
    print("Some information is missing.")