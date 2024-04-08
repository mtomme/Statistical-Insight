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
    print("Search Link:", url)  # Print the search link
    s = HTMLSession()
    r = s.get(url)

    titles = r.html.find('a.vehicle-card-link.js-gallery-click-link h2.title')
    mileages = r.html.find('div.vehicle-details div.mileage')
    prices = r.html.find('div.price-section.price-section-vehicle-card span.primary-price')
    locations = r.html.find('div.vehicle-dealer')
    images = r.html.find('div.image-wrap img.vehicle-image')  # Updated image selection

    if titles and mileages and prices and locations and images:  # Check if all elements are present
        car_info = []
        for title, mileage, price, location, image in zip(titles, mileages, prices, locations, images):
            car_info.append({
                'title': title.text,
                'mileage': mileage.text,
                'price': price.text,
                'location': location.text,
                'image': image.attrs['src'] if 'src' in image.attrs else 'No image available'  # Handle missing image
            })
        return render_template('search_results.html', car_info=car_info)
    else:
        missing_info = []
        if not titles:
            missing_info.append('Titles')
        if not mileages:
            missing_info.append('Mileages')
        if not prices:
            missing_info.append('Prices')
        if not locations:
            missing_info.append('Locations')
        if not images:
            missing_info.append('Images')
        return f"Missing information: {', '.join(missing_info)}"

if __name__ == '__main__':
    app.run(debug=True)
