import os
os.system('cls' if os.name == 'nt' else 'clear')
import json
import requests
import time
from lxml import html
from plexapi.server import PlexServer

#------------------------------------------------------------------------------
#
#	  Automated IMDB List to Plex Collection Script by /u/deva5610
#
#		       Created by modifiying the excellent
#
#       Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16
#
#                         *** USE AT YOUR OWN RISK! ***
#   *** I AM NOT RESPONSIBLE FOR DAMAGE TO YOUR PLEX SERVER OR LIBRARIES! ***
#
#------------------------------------------------------------------------------

#############################
### EDIT THE BELOW VALUES ###
#############################

### Plex server details ###

PLEX_URL = 'http://<plex-server>:32400' 		#Plex URL without trailing slash.
PLEX_TOKEN = '<plex-token>'
MOVIE_LIBRARIES = ['Movies']			#Enter Plex movie libraries, multiple allowed like ['Movies2', 'Test Movies'].

### TMBD API Key if using "The Movie Database" agent ###

TMDB_API_KEY = ''

#############################################
##### CODE BELOW - DON'T EDIT BELOW HERE#####
#############################################

#Hacky solution for Python 2.x & 3.x compatibility
if hasattr(__builtins__, 'raw_input'):
 input=raw_input

### Header ###

print("===================================================================")
print(" Automated IMDB List to Collection script by /u/deva5610  ")
print(" Created by modifiying the excellent  ")
print(" Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16  ")
print("===================================================================")
print("\n")

###IMDB List Details###

IMDB_URL = input("IMDB List URL (eg - https://www.imdb.com/list/ls002400902/): ")
IMDB_COLLECTION_NAME = input("Collection Name (eg - Disney Classics): ")

TMDB_REQUEST_COUNT = 0  # DO NOT CHANGE

def add_collection(library_key, rating_key):
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "collection[0].tag.tag": IMDB_COLLECTION_NAME,
              "collection.locked": 1
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
    r = requests.put(url, headers=headers, params=params)


def remove_collection(library_key, rating_key):
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "collection[].tag.tag-": IMDB_COLLECTION_NAME
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
    r = requests.put(url, headers=headers, params=params)


def get_imdb_id_from_tmdb(tmdb_id):
    global TMDB_REQUEST_COUNT
    
    if not TMDB_API_KEY:
        return None
    
    # Wait 10 seconds for the TMDb rate limit
    if TMDB_REQUEST_COUNT >= 40:
        time.sleep(10)
        TMDB_REQUEST_COUNT = 0
    
    params = {"api_key": TMDB_API_KEY}
    
    url = "https://api.themoviedb.org/3/movie/{tmdb_id}".format(tmdb_id=tmdb_id)
    r = requests.get(url, params=params)
    
    TMDB_REQUEST_COUNT += 1
    
    if r.status_code == 200:
        movie = json.loads(r.text)
        return movie['imdb_id']
    else:
        return None
    
    
def run_imdb_sync():
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("No Plex server found at: {base_url}".format(base_url=PLEX_URL))
        print("Exiting script.")
        return [], 0

    # Get list of movies from the Plex server
    all_movies = []
    for movie_lib in MOVIE_LIBRARIES:
        try:
            print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=movie_lib))
            movie_library = plex.library.section(movie_lib)
            library_language = movie_library.language  # IMDB will use language from last library in list
            all_movies.extend(movie_library.all())
        except:
            print("The '{library}' library does not exist in Plex.".format(library=movie_lib))
            print("Exiting script.")
            return [], 0

    # Get the requested imdb list
    print("Retrieving movies from selected IMDB list.")
    r = requests.get(IMDB_URL, headers={'Accept-Language': library_language})
    tree = html.fromstring(r.content)
    title_name = tree.xpath("//div[contains(@class, 'lister-item-content')]//h3[contains(@class, 'lister-item-header')]//a/text()")
    title_years = tree.xpath("//div[contains(@class, 'lister-item-content')]//h3[contains(@class, 'lister-item-header')]//span[contains(@class, 'lister-item-year')]/text()")
    title_ids = tree.xpath("//div[contains(@class, 'lister-item-content')]//div[contains(@class, 'ipl-rating-interactive')]/input//@data-tconst")

    # Create a dictionary of {imdb_id: movie}
    imdb_map = {}
    for m in all_movies:
        if 'imdb://' in m.guid:
            imdb_id = m.guid.split('imdb://')[1].split('?')[0]
        elif 'themoviedb://' in m.guid:
            tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0]
            imdb_id = get_imdb_id_from_tmdb(tmdb_id)
        else:
            imdb_id = None
            
        if imdb_id and imdb_id in title_ids:
            imdb_map[imdb_id] = m
        else:
            imdb_map[m.ratingKey] = m

    # Add movies to the selected collection
    print("Adding the collection '{}' to movies on the selected IMDB list...".format(IMDB_COLLECTION_NAME))
    in_library_idx = []
    for i, imdb_id in enumerate(title_ids):
        movie = imdb_map.pop(imdb_id, None)
        if movie:
            add_collection(movie.librarySectionID, movie.ratingKey)
            in_library_idx.append(i)

### See no reason to remove movies yet. Commenting this section out for now. ###
#            
#    # Remove movies from collection with are no longer on the IMDB Top 250 list
#    print("Removing the collection '{}' from movies not on the IMDB Top 250 list...".format(IMDB_COLLECTION_NAME))
#    count = 0
#    for movie in imdb_map.values():
#        remove_collection(movie.librarySectionID, movie.ratingKey)
    
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
        print("{idx}\t{imdb_id}\t{title} {year}".format(idx=idx+1, imdb_id=imdb_id.encode('UTF-8'), title=title.encode('UTF-8'), year=year.encode('UTF-8')))
    
    print("\n===================================================================")
    print("                               Done!                               ")
    print("===================================================================\n")
    
    input("Press Enter to finish...")
