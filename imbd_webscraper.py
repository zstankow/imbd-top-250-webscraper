import grequests
import requests
import time
from bs4 import BeautifulSoup
import json
import logging

with open('conf.json', 'r') as config_file:
    config = json.load(config_file)

user_agent = config['user_agent']
batch_size = config['batch_size']
base_url = config['base_url']
top_movies_url = config['top_movies_url']

logging.basicConfig(
    filename='movies.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def directors_of_movies_grequests(titles, urls, batch):
    """ Returns dictionary with the key as the movie title and it's value being the corresponding movie director. """
    directors = {}

    for i in range(0, 250, batch):
        batch_titles = titles[i:i+batch]
        batch_urls = urls[i:i+batch]
        reqs = (grequests.get(url, headers=user_agent) for url in batch_urls)
        responses = grequests.map(reqs)
        logging.info(f"Sending batch requests for movies {i + 1} to {i + batch}")

        for title, response in zip(batch_titles, responses):
            soup = BeautifulSoup(response.text, 'html.parser')
            directors[title.text] = soup.find("a", class_="ipc-metadata-list-item__list-content-item").text
            if directors[title.text]:
                logging.info(f"Successfully fetched movie title {title.text} and director {directors[title.text]}.")
            else:
                logging.error(f"Failed to fetch director of movie title {title.text}.")
            print(f"{title.text} - {directors[title.text]}")
            with open("stdout.log", "a") as f:
                f.write(f"{title.text} - {directors[title.text]}\n")


def directors_of_movies_requests(titles, urls):
    """ Returns dictionary with the key as the movie title and it's value being the corresponding movie director. """
    directors = {}
    for title, url in zip(titles, urls):
        source = requests.get(url, headers=user_agent)
        if source.status_code == 200:
            logging.info(f"Successfully fetched URL: {url}")
        else:
            logging.error(f"Failed to fetch URL: {url}, status code: {source.status_code}")
        soup = BeautifulSoup(source.text, 'html.parser')
        directors[title.text] = soup.find("a", class_="ipc-metadata-list-item__list-content-item").text
        if directors[title.text]:
            logging.info(f"Successfully fetched movie title: {title.text}, and director: {directors[title.text]}.")
        else:
            logging.error(f"Failed to fetch director of movie title {title.text}.")
        print(f"{title.text} - {directors[title.text]}")
        with open("stdout.log", "a") as f:
            f.write(f"{title.text} - {directors[title.text]}\n")


def get_movie_urls(urls: list):
    """ Returns list of links to each individual movie webpage in the IMBD top 250 movies ranking list."""
    return [base_url + url['href'] for url in urls]


def top_250_movies_grequests(main_url):
    """ Prints movie titles and directors of top 250 movies according to IMBD ranking, and returns time to print. """
    source = requests.get(main_url, headers=user_agent)
    if source.status_code == 200:
        logging.info(f"Successfully fetched URL: {main_url}")
    else:
        logging.error(f"Failed to fetch URL: {main_url}, status code: {source.status_code}")

    soup = BeautifulSoup(source.text, 'html.parser')
    movie_titles = soup.find('ul', class_='ipc-metadata-list').find_all('h3')
    if movie_titles:
        logging.info(f"Found movie title tags.")
    else:
        logging.error(f"Failed to find movie title tags within HTML.")

    links = soup.find_all('a', class_="ipc-lockup-overlay ipc-focusable")
    movie_urls = get_movie_urls(links)
    start_time = time.time()
    directors_of_movies_grequests(movie_titles, movie_urls, batch_size)
    end_time = time.time()
    delta_t = end_time - start_time
    return delta_t


def top_250_movies_requests(main_url):
    """ Prints movie titles and directors of top 250 movies according to IMBD ranking, and returns time to print. """
    source = requests.get(main_url, headers=user_agent)
    if source.status_code == 200:
        logging.info(f"Successfully fetched URL: {main_url}")
    else:
        logging.error(f"Failed to fetch URL: {main_url}, status code: {source.status_code}")
    soup = BeautifulSoup(source.text, 'html.parser')
    movie_titles = soup.find('ul', class_='ipc-metadata-list').find_all('h3')

    links = soup.find_all('a', class_="ipc-lockup-overlay ipc-focusable")
    movie_urls = get_movie_urls(links)
    start_time = time.time()
    directors_of_movies_requests(movie_titles, movie_urls)
    end_time = time.time()
    delta_t = end_time - start_time
    return delta_t


if __name__ == '__main__':
    url = top_movies_url
    t1 = top_250_movies_requests(url)
    logging.info(f"Using requests library, top 250 movies and their directors were extracted from IMBD in {t1} seconds.")
    t2 = top_250_movies_grequests(url)
    logging.info(f"Using grequests library, top 250 movies and their directors were extracted from IMBD in {t2} seconds.")

    print("\n")
    print(f"Time for script using requests library: {t1} seconds.")
    print(f"Time for script using grequests library: {t2} seconds. ")
    with open("stdout.log", "a") as f:
        f.write(f"Time for script using requests library: {t1} seconds.\n")
        f.write(f"Time for script using grequests library: {t2} seconds.")