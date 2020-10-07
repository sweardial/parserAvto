import requests
from bs4 import BeautifulSoup
import csv

URL = input('Enter URL: ')
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'accept': '*/*'}
HOST = 'https://auto.ria.com'
CSV_PATH = 'cars.csv'


def get_html(url, params=None):
    r = requests.get(url=url,
                     headers=HEADERS,
                     params=params)
    return r


# Checking the number of search pages.
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    number = soup.find("nav", class_="unstyle pager")
    if number is not None:  # if we find a page list
        number = number.get_text()
        number = number.split()  # splitting a string
        list_of_numbers = []  # creatng a list for splitted elements
        for n in number:
            try:
                n = int(n)  # if it could be converted into 'int' type
                list_of_numbers.append(n)  # appening the number into our list
            except ValueError:
                pass
        return list_of_numbers[-1]  # taking the last element, which will represent the number of
        # pages
    else:
        return 1  # if we don't find a page list there is just one page


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all("div", class_="proposition")
    cars = []
    number = 0
    for item in items:
        information = item.find('div', class_='proposition_information')
        information = information.get_text().replace('•', '')
        information = information.split()
        cars.append({
            'title': item.find('h3', class_='proposition_name').get_text(strip=True),
            'link': HOST + item.find('a').get('href'),
            'price in $': item.find('span', class_="green bold size18").get_text(strip=True),
            'price in uah': item.find('span', class_="grey size13").get_text(strip=True),
            'city': item.find('svg', class_='svg svg-i16_pin').find_next('strong').get_text(
                strip=True),
        })
        if len(information) == 6:
            cars[number]['type of engine'] = information[0] + ' ' + information[1] + ' ' + \
                                             information[2]
            cars[number]['transmission'] = information[3]
            cars[number]['drive unit'] = information[4] + ' ' + information[5]
        elif len(information) == 4:
            cars[number]['type of engine'] = information[0]
            cars[number]['transmission'] = information[1]
            cars[number]['drive unit'] = information[2] + ' ' + information[3]
        number += 1
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Car model', 'Link', 'Dollar Price',
                         'UAH Price', 'City', 'Type of Engine',
                         'Transmission', 'Drive Unit'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price in $'],
                            item['price in uah'], item['city'], item['type of engine'],
                            item['transmission'], item['drive unit']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Parsing {page} from {pages_count}..')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        print(f'Number of cars = {len(cars)}')
        save_file(cars, CSV_PATH)
    else:
        print('Error')


if __name__=='__main__':
    parse()
