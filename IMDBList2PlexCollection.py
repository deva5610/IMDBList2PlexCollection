#------------------------------------------------------------------------------
#
#      Automated IMDB List to Plex Collection Script by /u/deva5610 - V2.0
#
#                      Created by modifiying the excellent
#
#        Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16
#
#                         *** USE AT YOUR OWN RISK! ***
#   *** I AM NOT RESPONSIBLE FOR DAMAGE TO YOUR PLEX SERVER OR LIBRARIES! ***
#
#------------------------------------------------------------------------------

#############################################
##### CODE BELOW - DON'T EDIT BELOW HERE#####
#############################################
import os
import sys
import requests
import time
import platform
from lxml import html
from plexapi.server import PlexServer
from tmdbv3api import TMDb
from tmdbv3api import Movie
import configparser
from bs4 import BeautifulSoup
import re
import traceback  # Added for error handling

# Start with a nice clean screen
os.system('cls' if os.name == 'nt' else 'clear')

# Hacky solution for Python 2.x & 3.x compatibility
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

### Header ###
print("===================================================================")
print(" Automated IMDB List to Collection script by /u/deva5610 - V1.2 ")
print(" Created by modifying the excellent  ")
print(" Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16  ")
print("===================================================================")
print("\n")

def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

# Load configuration from config.ini
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config = load_config(config_path)

PLEX_URL = config.get('plex', 'url')
PLEX_TOKEN = config.get('plex', 'token')
MOVIE_LIBRARIES = config.get('plex', 'library').split(',')
TMDB_API_KEY = config.get('tmdb', 'apikey')

def validate_input(imdb_url, page_numbers):
    # Validate user inputs for IMDb URL and page numbers
    imdb_url_pattern = r'^https:\/\/www\.imdb\.com\/list\/ls\d+\/$'
    if not re.match(imdb_url_pattern, imdb_url):
        raise ValueError("Invalid IMDb URL. It should be in the format 'https://www.imdb.com/list/ls<list_id>/'.")

    try:
        page_numbers = int(page_numbers)
        if page_numbers <= 0:
            raise ValueError()
    except ValueError:
        raise ValueError("Page numbers should be a positive integer.")

def add_collection(library_key, rating_key):
    # Add a movie to a Plex collection
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {
        "type": 1,
        "id": rating_key,
        "collection[0].tag.tag": IMDB_COLLECTION_NAME,
        "collection.locked": 1
    }
    url = f"{PLEX_URL}/library/sections/{library_key}/all"

    try:
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(f"Added movie to collection: {rating_key}")
    except Exception as e:
        print(f"Failed to add movie to collection: {rating_key}")
        traceback.print_exc()  # Print the exception and its traceback

def retrieve_movies_from_plex(plex, movie_libraries):
    # Retrieve movies from Plex libraries
    all_movies = []
    for movie_lib in movie_libraries:
        try:
            movie_library = plex.library.section(movie_lib)
            all_movies.extend(movie_library.all())
        except Exception as e:
            print(f"Error retrieving movies from '{movie_lib}' library: {str(e)}")
            traceback.print_exc()  # Print the exception and its traceback
    return all_movies

def retrieve_movies_from_imdb(imdb_url, page_numbers):
    # Retrieve movies from IMDb list
    imdb_movies = []

    for page in range(1, int(page_numbers) + 1):
        page_url = f"{imdb_url}?page={page}"

        try:
            response = requests.get(page_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except Exception as e:
            print(f"Failed to retrieve page {page} from IMDb: {str(e)}")
            traceback.print_exc()  # Print the exception and its traceback
            continue  # Continue to the next page

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            movie_elements = soup.find_all("div", class_="lister-item-content")

            for movie_element in movie_elements:
                title_element = movie_element.find("h3", class_="lister-item-header")
                year_element = movie_element.find("span", class_="lister-item-year")
                imdb_link = movie_element.find("a", href=True)

                # Check if all required elements are found
                if title_element and year_element and imdb_link:
                    title = title_element.find("a").text.strip()
                    
                    # Extract the year and handle variations in the format
                    year_text = year_element.text.strip('()')
                    year = ''.join(filter(str.isdigit, year_text))  # Extract digits from the year text

                    imdb_id = imdb_link["href"].split("/title/")[1].split("/")[0]

                    imdb_movies.append({
                        "title": title,
                        "year": year,
                        "imdb_id": imdb_id
                    })
                else:
                    print(f"Failed to extract movie data from page {page}. Missing elements:")
                    if not title_element:
                        print("- Title element not found.")
                    if not year_element:
                        print("- Year element not found.")
                    if not imdb_link:
                        print("- IMDb link element not found.")
        else:
            print(f"Failed to retrieve page {page} from IMDb.")

    return imdb_movies
    
def match_imdb_to_plex_movies(plex_movies, imdb_movies):
    # Match IMDb movies to Plex movies
    imdb_to_plex_map = {}
    
    for imdb_movie in imdb_movies:
        matched_plex_movie = find_matching_plex_movie(imdb_movie, plex_movies)
        if matched_plex_movie:
            imdb_to_plex_map[imdb_movie["imdb_id"]] = matched_plex_movie
    
    return imdb_to_plex_map

def find_matching_plex_movie(imdb_movie, plex_movies):
    # Custom matching logic to find a Plex movie that matches the IMDb movie
    for plex_movie in plex_movies:
        if is_matching(imdb_movie, plex_movie):
            return plex_movie
    return None

def is_matching(imdb_movie, plex_movie):
    # Custom comparison logic to determine if an IMDb movie matches a Plex movie
    imdb_title = imdb_movie["title"]
    imdb_year = imdb_movie["year"]
    plex_title = plex_movie.title
    plex_year = plex_movie.year

    # Example: Consider it a match if titles are the same and years are within +/- 1 year
    if imdb_title == plex_title and abs(int(imdb_year) - int(plex_year)) <= 1:
        return True

    return False

def run_imdb_sync():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        PLEX_URL, PLEX_TOKEN, MOVIE_LIBRARIES, TMDB_API_KEY = load_config(CONFIG_PATH)
        imdb_url = input("IMDB List URL (e.g., https://www.imdb.com/list/ls002400902/): ")
        page_numbers = input("How many pages do you want to scrape on this IMDB list? (default: 1): ") or "1"
        validate_input(imdb_url, page_numbers)

        # Input the collection name
        global IMDB_COLLECTION_NAME
        IMDB_COLLECTION_NAME = input("Collection Name (e.g., Disney Classics): ")

        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        plex_movies = retrieve_movies_from_plex(plex, MOVIE_LIBRARIES)

        imdb_movies = retrieve_movies_from_imdb(imdb_url, page_numbers)
        imdb_to_plex_map = match_imdb_to_plex_movies(plex_movies, imdb_movies)

        print("Adding the collection '{0}' to matched movies.".format(IMDB_COLLECTION_NAME))
        for imdb_id, plex_movie in imdb_to_plex_map.items():
            add_collection(plex_movie.librarySectionID, plex_movie.ratingKey)

        print("Done!")
    except Exception as e:
        print("An error occurred:", str(e))
        sys.exit(1)

def main():
    run_imdb_sync()

if __name__ == "__main__":
    main()
