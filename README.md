artereplay is an utility to search or download replay videos available from arteplus7 site

It is written in Python and uses wget to download videos, with a fallback to a plain requests.get in case wget is not available

It has been written for fun and to learn Python, therefore is inspired but not copied from other sources
In particular trou/arteget is a "similar but different" script written in Ruby also under the GNU GPL license

Enjoy downloading those nice programs that you will never have the time to watch ;)

Examples
========
1) Print the 3 most viewed videos and adds them to a file
./artereplay.py list most_viewed --max 3 -f outputfile.txt

2) Search for all karambolage videos (can also be used with -f)
./artereplay.py search karambolage

3) Download from arteplus7 url the French version with no subtitles and quality HQ, renaming to programname.mp4
./artereplay.py download --subs no --lang fr --qual HQ -o dirname/programname.mp4 url

4) Download multiple videos from command line into a directory
./artereplay.py download --subs no --lang de --qual HQ -d dirname/ url1 url2 url3

5) Download a list of videos from a file, tries to match subtitles and language, must match quality, downloads to directory
./artereplay.py download --subs yes --lang fr --qual HQ -d dirname/ -i inputfile.txt 

6) Same as the above but doesn't download videos, adds downloadable links to a file instead
./artereplay.py download --subs yes --lang es --qual HQ -i inputfile.txt -dlf list_to_dl.txt 

arteplus7 url needs to look like this: http://www.arte.tv/guide/<LANG/<ID>/<PROGRAM_NAME>

Logging
=======
-v -vv -vvv control the info level on the console, default is ERROR, -v is WARNING, -vv is INFO and -vvv is DEBUG
--logfile file and --loglevel control th logging to a file, loglevel can be CRITICAL ERROR WARNING INFO DEBUG

Localization and accessibility
==============================
The script works with any arte site and will download for any language if available.
The supported sites are therefore: French (fr), German (de), English (en), Spanish (es), and Polish (pl).
There are 3 options available on the command line:
-sl / --site_lang fr|de|es|en|pl will attempt to list, search, and download from the specified site. Default is fr. 
-l / --lang fr|de|es|en|pl will attempt to download a version of the specified language. Default is fr.
-s / --subs yes|no|mal will attempt to download a subtitled version, a non subtitled version (original or dubbed), or the hearing impaired version. Default is yes.

With the download command, some priorities are applied to find the most appropriate video:
- subtitles default to yes and fallbacks are defined this way : mal > yes, yes > no, no > yes.
- arte has a mechanism to define the most appropriate content based on the site language. If no matching video is found, the script will take what arte considers as default for this site_lang

There are some known limitations:
- There are much less choices for non FR or DE versions. For instance, Spanish version with no subtitles will only work if the video is originally Spanish.
- Due to the huge number of possible combinations, they have not all been tested. Also arte may change them over time. This could be better managed by adding some more configurability to the script.

Known issues and limitations
============================
- There is no fallback for video quality if not matched, assuming this shouldn't happen. You can always look up the JSON in case you don't find what you want.
- Search is just a regular search, there is no specific search for arte regular programs like metropolis, karambolage, ...
- If wget is not present on the system, the script will attempt to download using requests module, which I didn't test intensively.
- It's possible to keyboard interrupt the wget process and the script will proceed to the next download if any. That can be nice, or unwanted if the desired behaviour was to completely stop the script.

This is just a script so I'm lazy about the above. Feel free to improve.

Contact
=======
develangie at gmail d0t com










