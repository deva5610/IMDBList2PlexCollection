# IMDBList2PlexCollection
Simple script/[standalone build](https://github.com/deva5610/IMDBList2PlexCollection/releases/) to take an IMDB list, match the movies
in your Plex Library and turn them into a collection.

This script is a modified version of [this excellent script](https://gist.github.com/JonnyWong16/f5b9af386ea58e19bf18c09f2681df23).

Thanks to /u/SwiftPanda16 for the original.

# Disclaimer
I'm not a developer.....at all. My modifications are probably quite slap happy, but they work fine for me and have on a few
different installs now with 0 problems. **This doesn't mean it will for you.** I'm not responsible for any heartaches caused when you
decide to mess with your Plex server. Maybe spin up a small test library before deploying it on a big library if you're concerned
about my lack of ability!

# Configuration
Create or edit config.ini with your favourite text editor. Keep config.ini in the same working directory as the script. 

**ONLY _"url="_, _"token="_ and _"library="_ underneath the [plex] header need to be set for the script to work**.

**url=** cannot end with a trailing slash - _**url=http://localhost:32400**_ & _**url=https://plex.woofwoof.wahoo**_ are both 
examples of proper formatting, _**url=https://plex.woofwoof.wahoo/**_ is not.

**token=** can be found using [this guide.](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
A token can also be found in Tautulli or Ombi if you're using them. _**token=njkjdkHJJKAJKnjSAKJ**_ is an example of correct formatting.

**library=** is pretty self explanatory. Multiple libraries supported, seperated by a comma ",". _**library=Movies and library=4K Movies,Movies,Kids Movies**_ are examples of correct formatting.

They are the three variables most people will have to fill in.

**_If, and only IF you're using_** 'The Movie Database' agent instead of Plex Movie you'll also need to edit the _**apikey=**_ variable
located under the [tmdb] header.

**Once complete it should look like**

    [plex]
    url=http://PLEXSERVERURL:32400
    token=REPLACEmeWITHyourTOKEN
    library=Movies,Test Library,Kids

    [tmdb]
    apikey=Optional

# Usage
If you are not using a [standalone binary](https://github.com/deva5610/IMDBList2PlexCollection/releases/) you'll need to install dependencies. Use pip to install the few listed requirements.

pip install -r requirements.txt **_OR_** "pip install lxml" "pip install plexapi" "pip install requests" "pip install tmdbv3api" in turn.

Run the script with "python imdb2collection.py" and follow the instructions. You'll want two things. A URL to the IMDB list you want to match (eg - https://www.imdb.com/list/ls064646512/) and to decide what you want the matching movies to be tagged as
(eg - Pixar, Pixar Movies, Pixar Animations, etc - all 3 are valid entries when asked).

***Note - IMDB Lists are supported in their default 'detailed' view, as are the result pages from the powerful [IMDB search engine.](https://www.imdb.com/search/title/)***

That's it. The script should (hopefully!) run, it'll match movies from the IMDB list to your Movies Library and tag them into the
collection you specified.

# Issues
Probably. Don't blame me. Fork, fix and merge.

# Enjoy
This one is simple.
