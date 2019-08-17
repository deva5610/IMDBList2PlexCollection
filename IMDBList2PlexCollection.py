#------------------------------------------------------------------------------
#
#     Automated IMDB List to Plex Collection Script by /u/deva5610
#
#              Created by modifiying the excellent
#
#       Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16
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
import json
import requests
import time
import platform
from lxml import html
from plexapi.server import PlexServer
from tmdbv3api import TMDb
from tmdbv3api import Movie

# Start with a nice clean screen
os.system('cls' if os.name == 'nt' else 'clear')

# Hacky solution for Python 2.x & 3.x compatibility
if hasattr(__builtins__, 'raw_input'):
    input=raw_input


### Header ###
print("===================================================================")
print(" Automated IMDB List to Collection script by /u/deva5610  ")
print(" Created by modifiying the excellent  ")
print(" Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16  ")
print("===================================================================")
print("\n")

### ConfigParser Python2/3 Support ###

try:
    # >3.2
    from configparser import ConfigParser
except ImportError:
    # python27
    # Refer to the older SafeConfigParser as ConfigParser
    from ConfigParser import SafeConfigParser as ConfigParser

parser = ConfigParser()

# Get config.ini path and check it exists!
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
didreadreadme = os.path.isfile(config_path)
if not didreadreadme:
    print("You need to read the README. Please create a config.ini in the same folder as this program.")
    print("\n")
    input("Press Enter to exit, and then go and read the README.")
    sys.exit()

# Process config.ini
parser.read(config_path)
PLEX_URL = parser.get('plex', 'url')
# Strip trailing slashes from URL
slash = '/'
if (PLEX_URL[-1] == slash):
    PLEX_URL = PLEX_URL.rstrip('//')
PLEX_TOKEN = parser.get('plex', 'token')
MOVIE_LIBRARIES = parser.get('plex', 'library').split(',')

# IMDB List Details
IMDB_COLLECTION_NAME = input("Collection Name (eg - Disney Classics): ")
print("\n")

def script():
    
#IMDB URL input
    IMDB_URL = input("IMDB List URL (eg - https://www.imdb.com/list/ls002400902/): ")
    print("\n")
    if not (IMDB_URL[-1] == slash):
        IMDB_URL = IMDB_URL + '/'

#How many pages do we want to scrape?
    PAGE_NUMBERS = int(raw_input("How many pages do you want to scrape on this IMDB list? (default: 1): ") or "1")
    print("\n")

    def add_collection(library_key, rating_key):
        headers = {"X-Plex-Token": PLEX_TOKEN}
        params = {"type": 1,
                  "id": rating_key,
                  "collection[0].tag.tag": IMDB_COLLECTION_NAME,
                  "collection.locked": 1
                  }

        url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
        r = requests.put(url, headers=headers, params=params)

    def run_imdb_sync():
        try:
            plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        except:
            print("No Plex server found at: {base_url}".format(base_url=PLEX_URL))
            print("Please check that config.ini exists, and is correct.")
            print("If the URL displayed is correct, your token may be incorrect.")
            print("\n")
            input("Press Enter to exit")
            sys.exit()

# Get list of movies from the Plex server
        all_movies = []
        for movie_lib in MOVIE_LIBRARIES:
            try:
                print("Retrieving a list of movies from the '{library}' library in Plex.".format(library=movie_lib))
                print("\n")
                movie_library = plex.library.section(movie_lib)
                library_language = movie_library.language  # IMDB will use language from last library in list
                all_movies.extend(movie_library.all())
            except:
                print("The '{library}' library does not exist in Plex.".format(library=movie_lib))
                print("Please check that config.ini exists, and is correct.")
                print("\n")
                input("Press Enter to exit")
                sys.exit()

# Get the requested imdb list
        print("Retrieving movies from selected IMDB list. Depending on the amount of pages selected this might take a few minutes.")
        print("\n")
        maxpages = int(PAGE_NUMBERS) + 1
        title_name = []
        title_years = []
        title_ids = []
        for i in range(1,maxpages):
            url = IMDB_URL + '?page={}'.format(i)
            r = requests.get(url, headers={'Accept-Language': library_language})
            tree = html.fromstring(r.content)
            title_name.extend(tree.xpath("//div[contains(@class, 'lister-item-content')]//h3[contains(@class, 'lister-item-header')]//a/text()"))
            title_years.extend(tree.xpath("//div[contains(@class, 'lister-item-content')]//h3[contains(@class, 'lister-item-header')]//span[contains(@class, 'lister-item-year')]/text()"))
            title_ids.extend(tree.xpath("//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst"))

# Convert TMDB to IMDB ID and create a dictionary of {imdb_id: movie} 
        print("Matching IMDB IDs to Library. For large Libraries using TMDB agent this step can take a long time.")
        print("\n")
        reqcount = 0
        tmdb = TMDb()
        tmdb.api_key = parser.get('tmdb', 'apikey')
        movie = Movie()
        imdb_map = {}
        for m in all_movies:         
            if 'themoviedb://' in m.guid:
                if reqcount >= 10:
                    time.sleep(2.5)
                    reqcount = 0
                if tmdb.api_key:
                    tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0]
                    tmdbapi = movie.details(tmdb_id)
                    imdb_id = tmdbapi.imdb_id
                    reqcount += 1
                else:
                    imdb_id = None
            elif 'imdb://' in m.guid:
                imdb_id = m.guid.split('imdb://')[1].split('?')[0]
            else:
                imdb_id = None
            
            if imdb_id and imdb_id in title_ids:
                imdb_map[imdb_id] = m
            else:
                imdb_map[m.ratingKey] = m

# Add movies to the selected collection
        print("Adding the collection '{}' to matched movies.".format(IMDB_COLLECTION_NAME))
        print("\n")
        in_library_idx = []
        for i, imdb_id in enumerate(title_ids):
            movie = imdb_map.pop(imdb_id, None)
            if movie:
                add_collection(movie.librarySectionID, movie.ratingKey)
                in_library_idx.append(i)

# Get list of missing movies from selected list
        missing_imdb_movies = [(idx, imdb) for idx, imdb in enumerate(zip(title_ids, title_name, title_years))
                            if idx not in in_library_idx]

        return missing_imdb_movies, len(title_ids)

    if __name__ == "__main__":

        missing_imdb_movies, list_count = run_imdb_sync()
    
        print("\n===================================================================\n")
        print("Number of IMDB movies from selected list in the library: {count}".format(count=list_count-len(missing_imdb_movies)))
        print("Number of missing selected list movies: {count}".format(count=len(missing_imdb_movies)))
        print("\nList of movies missing that are in selected IMDB list:\n")
    
        for idx, (imdb_id, title, year) in missing_imdb_movies:
            if platform.python_version().startswith('2'):
                print("{idx}\t{imdb_id}\t{title} {year}".format(idx=idx+1, imdb_id=imdb_id.encode('UTF-8'), title=title.encode('UTF-8'), year=year.encode('UTF-8')))
            else:
                print("{idx}\t{imdb_id}\t{title} {year}".format(idx=idx+1, imdb_id=imdb_id, title=title, year=year))
    
        print("\n===================================================================")
        print("                               Done!                               ")
        print("===================================================================\n")
        print("\n")
        print("Would you like to add more movies from IMDB to this collection?")
        print("\n")
        EOS = input("Input Y to continue, or N to exit - ")
        if EOS == "Y" or EOS == "y":
            print("\n")
            script()
        else:
            sys.exit()
script()
