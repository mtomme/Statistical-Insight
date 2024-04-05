from flask import Flask, render_template, request
from requests_html import HTMLSession

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    zipcode = request.form['zipcode']
    distance = request.form['distance']
    makes = request.form['makes']
    model = request.form['model']
    stockType = request.form['stockType']
    sort = request.form['sort']

    url = 'https://www.cars.com/shopping/results/?stock_type=all&page=1&page_size=100&sort={}&makes%5B%5D={}&models%5B%5D={}&stock_type={}&maximum_distance={}&zip={}'.format(sort, makes, model, stockType, distance, zipcode)
    s = HTMLSession()
    r = s.get(url)

    titles = r.html.find('a.vehicle-card-link.js-gallery-click-link h2.title')
    mileages = r.html.find('div.vehicle-details div.mileage')
    prices = r.html.find('div.price-section.price-section-vehicle-card span.primary-price')
    locations = r.html.find('div.vehicle-dealer')

    if titles and mileages and prices and locations:
        car_info = []
        for title, mileage, price, location in zip(titles, mileages, prices, locations):
            car_info.append(f"{title.text}, {mileage.text}, {price.text}, {location.text}")
        return render_template('search_results.html', car_info=car_info)
    else:
        return "Some information is missing."

if __name__ == '__main__':
    app.run(debug=True)