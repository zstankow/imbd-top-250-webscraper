import grequests
import requests
import time
from bs4 import BeautifulSoup
import json

with open('conf.json', 'r') as config_file:
    config = json.load(config_file)

user_agent = config['user_agent']
batch_size = config['batch_size']
base_url = config['base_url']
top_movies_url = config['top_movies_url']


def directors_of_movies_grequests(titles, urls, batch):
    """ Returns dictionary with the key as the movie title and it's value being the corresponding movie director. """
    directors = {}
    for i in range(0, 250, batch):
        batch_titles = titles[i:i+batch]
        batch_urls = urls[i:i+batch]
        reqs = (grequests.get(url, headers=user_agent) for url in batch_urls)
        responses = grequests.map(reqs)

        for title, response in zip(batch_titles, responses):
            soup = BeautifulSoup(response.text, 'html.parser')
            directors[title.text] = soup.find("a", class_="ipc-metadata-list-item__list-content-item").text
            print(f"{title.text} - {directors[title.text]}")


def directors_of_movies_requests(titles, urls):
    """ Returns dictionary with the key as the movie title and it's value being the corresponding movie director. """
    directors = {}
    for title, url in zip(titles, urls):
        source = requests.get(url, headers=user_agent).text
        soup = BeautifulSoup(source, 'html.parser')
        directors[title.text] = soup.find("a", class_="ipc-metadata-list-item__list-content-item").text
        print(f"{title.text} - {directors[title.text]}")
    return directors


def get_movie_urls(urls: list):
    """ Returns list of links to each individual movie webpage in the IMBD top 250 movies ranking list."""
    return [config[base_url] + url['href'] for url in urls]


def top_250_movies_grequests(main_url):
    """ Prints movie titles and directors of top 250 movies according to IMBD ranking, and returns time to print. """
    source = requests.get(main_url, headers=user_agent).text
    soup = BeautifulSoup(source, 'html.parser')
    movie_titles = soup.find('ul', class_='ipc-metadata-list').find_all('h3')

    links = soup.find_all('a', class_="ipc-lockup-overlay ipc-focusable")
    movie_urls = get_movie_urls(links)
    start_time = time.time()
    directors_of_movies_grequests(movie_titles, movie_urls, batch_size)
    end_time = time.time()
    delta_t = end_time - start_time
    return delta_t


def top_250_movies_requests(main_url):
    """ Prints movie titles and directors of top 250 movies according to IMBD ranking, and returns time to print. """
    source = requests.get(main_url, headers=user_agent).text
    soup = BeautifulSoup(source, 'html.parser')
    movie_titles = soup.find('ul', class_='ipc-metadata-list').find_all('h3')

    links = soup.find_all('a', class_="ipc-lockup-overlay ipc-focusable")
    movie_urls = get_movie_urls(links)
    start_time = time.time()
    directors_of_movies_requests(movie_titles, movie_urls)
    end_time = time.time()
    delta_t = end_time - start_time
    return delta_t


if __name__ == '__main__':
    url = base_url
    t1 = top_250_movies_requests(url)
    t2 = top_250_movies_grequests(url)
    print("\n")
    print(f"Time for script using requests library: {t1} seconds.")
    print(f"Time for script using grequests library: {t2} seconds. ")
