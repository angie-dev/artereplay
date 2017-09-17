# artereplay

**artereplay** is a utility to search or download replay videos available from arteplus7 site

It is written in Python and uses `wget` to download videos, with a fallback to a plain `requests.get` in case `wget` is not available

It has been written for fun and to learn Python, therefore is inspired but not copied from other sources

In particular [trou/arteget](https://github.com/trou/arteget) is a "similar but different" script written in Ruby also under the GNU GPL license

Enjoy downloading those nice programs that you will never have the time to watch ;)

August 6th, 2017 update : arte updated its site. While most functionality is still there, I couldn't find the endpoint for list command. Keeping it as deprecated for now.

## Examples

* Print the 3 most viewed videos and adds them to a file - DEPRECATED
    ```
    ./artereplay.py list most_viewed --max 3 -f outputfile.txt
    ```
        
* Search for all karambolage videos (can also be used with -f)
    ```
    ./artereplay.py search karambolage
    ```
* Download from arteplus7 url the French version with no subtitles and quality HQ, renaming to programname.mp4

    ```
    ./artereplay.py download --subs no --lang fr --qual HQ -o dirname/programname.mp4 url
    ```
* Download multiple videos from command line into a directory

    ```
    ./artereplay.py download --subs no --lang de --qual HQ -d dirname/ url1 url2 url3
    ```
* Download a list of videos from a file, tries to match subtitles and language, must match quality, downloads to directory

    ```
    ./artereplay.py download --subs yes --lang fr --qual HQ -d dirname/ -i inputfile.txt
    ```
* Same as the above but doesn't download videos, adds downloadable links to a file instead

    ```
    ./artereplay.py download --subs yes --lang es --qual HQ -i inputfile.txt -dlf list_to_dl.txt
    ```
    
arteplus7 url needs to look like this: http://www.arte.tv/LANG/videos/PROGRAM_ID/PROGRAM_NAME

## Usage with Docker

To avoid installing virtualenv and python modules, a Dockerfile is provided.

* Build the image
    ```
    docker build -t <image-name> .
    ```
* Run the image in a container for searching
    ```
    docker run --rm -ti --name <container-name> <image-name> search <keyword>
    ```
* Run the image in a container for downloading. You have to bind-mount your host directory to the container's /app. As a result -d option is useless.
    ```
    docker run --rm -ti -v <local_path_to_download_videos>:/app --name <container-name> <image-name> download <any other options> <video url>
    ```

## Logging

* ` -v -vv -vvv` control the info level on the console, default is ERROR, -v is WARNING, -vv is INFO and -vvv is DEBUG
* `--logfile <file>` and `--loglevel <LEVEL>` control the logging to a file, loglevel can be CRITICAL ERROR WARNING INFO DEBUG

## Localization and accessibility

The script works with any arte site and will download for any language if available.

The supported sites are therefore: French (fr), German (de), English (en), Spanish (es), and Polish (pl).

There are 3 options available on the command line:
* `-sl / --site_lang fr|de|es|en|pl` will attempt to list, search, and download from the specified site. Default is fr. 
* `-l / --lang fr|de|es|en|pl` will attempt to download a version of the specified language. Default is fr.
* `-s / --subs yes|no|mal` will attempt to download a subtitled version, a non subtitled version (original or dubbed), or the hearing impaired version. Default is yes.

With the download command, some priorities are applied to find the most appropriate video:
- subtitles default to yes and fallbacks are defined this way : mal > yes, yes > no, no > yes.
- arte has a mechanism to define the most appropriate content based on the site language. If no matching video is found, the script will take what arte considers as default for this site_lang
