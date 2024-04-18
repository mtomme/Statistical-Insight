from flask import Flask, render_template, request
import requests
import logging
from bs4 import BeautifulSoup

# Set up logging to output to console only
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
visited_urls = set()  # Global set to track visited URLs

def calculate_average_price(car_info):
    total_price = sum(float(car['price'].replace('$', '').replace(',', '')) for car in car_info if car['price'] != 'Not Priced')
    num_cars_with_price = sum(1 for car in car_info if car['price'] != 'Not Priced')
    return round(total_price / num_cars_with_price, 2) if num_cars_with_price else 0

def get_car_info(url, debug=False):
    if url in visited_urls:
        logging.debug(f"URL {url} already visited, stopping further requests.")
        return [], True  # Return True to indicate no more pages
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        if response.status_code == 302:
            logging.info(f"Redirect detected for URL {url}, likely no more pages.")
            return [], True  # No more pages to process
        elif response.status_code == 200:
            visited_urls.add(url)  # Add URL to the visited set
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = soup.select('a.vehicle-card-link.js-gallery-click-link h2.title')
            mileages = soup.select('div.vehicle-details div.mileage')
            prices = soup.select('div.price-section.price-section-vehicle-card span.primary-price')
            locations = soup.select('div.vehicle-dealer')
            car_info = [{
                'title': title.get_text(strip=True),
                'mileage': mileage.get_text(strip=True),
                'price': price.get_text(strip=True),
                'location': location.get_text(strip=True)
            } for title, mileage, price, location in zip(titles, mileages, prices, locations) if all([title, mileage, price, location])]
            return car_info, False
        else:
            logging.error(f"Unexpected status code {response.status_code} for URL: {url}")
            return [], True
    except requests.RequestException as e:
        logging.error(f"Request failed for URL {url}: {str(e)}")
        return [], True

def categorize_mileage(car_info):
    categories = {
        "Under 20k": [],
        "20k-40k": [],
        "40k-60k": [],
        "60k-80k": [],
        "80k-100k": [],
        "100k+": []
    }
    for car in car_info:
        mileage = int(car['mileage'].replace(' miles', '').replace(',', ''))
        if mileage < 20000:
            categories["Under 20k"].append(car)
        elif mileage < 40000:
            categories["20k-40k"].append(car)
        elif mileage < 60000:
            categories["40k-60k"].append(car)
        elif mileage < 80000:
            categories["60k-80k"].append(car)
        elif mileage < 100000:
            categories["80k-100k"].append(car)
        else:
            categories["100k+"].append(car)
    return categories

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    zipcode = request.form.get('zipcode', '')
    distance = request.form.get('distance', 'all')
    makes = request.form.get('makes', 'all')
    model = request.form.get('model', 'all')
    stockType = request.form.get('stockType', 'all')
    sort = request.form.get('sort', 'best_match_desc')

    url_template = 'https://www.cars.com/shopping/results/?page={}&page_size=100&sort={}&makes%5B%5D={}&models%5B%5D={}&stock_type={}&maximum_distance={}&zip={}'
    page_num = 1
    car_info = []
    stop = False

    while not stop and page_num <= 10:  # Ensures it doesn't exceed your max page limit
        url = url_template.format(page_num, sort, makes, model, stockType, distance, zipcode)
        page_car_info, stop = get_car_info(url, debug=True)
        if page_car_info:
            car_info.extend(page_car_info)
            page_num += 1

    if car_info:
        average_price = calculate_average_price(car_info)
        mileage_categories = categorize_mileage(car_info)
        return render_template('search_results.html', car_info=car_info, average_price=average_price, mileage_categories=mileage_categories)
    return "No search results found."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)