# IMDBList2PlexCollection
Simple script to take an IMDB list, match the movies in your Plex Library and turn them into a collection.

This script is a modified version of [this excellent script](https://gist.github.com/JonnyWong16/f5b9af386ea58e19bf18c09f2681df23).

Thanks to /u/SwiftPanda16 for the original.

# Disclaimer
I'm not a developer.....at all. My modifications are probably quite slap happy, but they work fine for me and have on a few
different installs now with 0 problems. **This doesn't mean it will for you.** I'm not responsible for any heartaches caused when you
decide to mess with your Plex server. Maybe spin up a small test library before deploying it on a big library if you're concerned
about my lack of ability!

# Installation
Edit imdb2collection.py with your favourite text editor. PLEX_URL, PLEX_TOKEN and MOVIE_LIBRARIES need to be set.

PLEX_URL cannot end with a trailing slash - http://localhost:32400 & https://plex.woofwoof.wahoo are both fine,
https://plex.woofwoof.wahoo/ is not.

PLEX_TOKEN can be found using [this guide.](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
A token can also be found in Tautulli or Ombi if you're using them.

MOVIE_LIBRARIES is pretty self explanatory. ['My Movies 1'], ['My Movies 1', 'My Movies 2'] are both valid examples.

They are the three variables most people will have to fill in. If you're using 'The Movie Database' agent instead of Plex Movie you'll
also need to edit the TMDB_API_KEY variable.

That's all. Nothing else needs to be edited.

# Usage
Use pip to install the few listed requirements.

pip install -r requirements.txt

Run the script with "python imdb2collection.py" and follow the instructions. You'll want two things. A URL to the IMDB list you want to match, set to "Compact View" (eg - https://www.imdb.com/list/ls064646512/?sort=list_order,asc&st_dt=&mode=simple&page=1&ref_=ttls_vw_smp) and to decide what you want the matching movies to be tagged as
(eg - Pixar, Pixar Movies, Pixar Animations, etc - all 3 are valid entries when asked).

***Note - You must set the IMDB page you want copied to the 'Compact View' mode before copying the URL. Failing to do this will result in 0 movies being seen. This change means that pages generated from the powerful [IMDB search](https://www.imdb.com/search/title/) can also be scraped and not just specific list pages.***

That's it. The script should (hopefully!) run, it'll match movies from the IMDB list to your Movies Library and tag them into the
collection you specified.

# Issues
Probably. Don't blame me. Fork, fix and merge.

# Enjoy
This one is simple.
