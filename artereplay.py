#!/usr/bin/env python3
#
# Copyright 2017 Cécile Ritte
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import json
import requests
import argparse
import parse
import subprocess
import logging
import os
os.environ['COLUMNS'] = "300"

def handle_list_command(args):
    list_programs = []
        
    # Return program info in a list
    list_programs = get_list_programs(args.list, args.max, args.site_lang)
    try:
        # Print nicely
        print(json.dumps(list_programs, indent=4, ensure_ascii=False))
    except:
        logger.warning("Coulnd't nicely print the list of videos. Printing ugly then.")
        print(list_programs)
        
    if args.file != None:
        add_to_file(list_programs, args.file)

    logger.info("Finished PRINT command")

def handle_search_command(args):
    
    search_term = args.term[:7]
    search_programs_list = get_search_programs(search_term, args.site_lang)

    try:
        print(json.dumps(search_programs_list, indent=4, ensure_ascii=False))
    except:
        logger.warning("Coulnd't nicely print the list of videos. Printing ugly then.")
        print(search_programs_list)

    if args.file != None:
        add_to_file(search_programs_list, args.file)

    logger.info("Finished SEARCH command")

def handle_download_command(args):

    # Initialize parameters
    subs = args.subs
    lang = args.lang
    site_lang = args.site_lang
    qual = args.qual.upper()
    dir = args.dirname
    output = args.output
    dlfile = args.downloadfile
    if dir == None: dir=''

    # Get list of URLs to download into list_url (even if just one was provided with the command line)
    list_url=[]
    if args.input != None:
        if args.url != []:
            logger.warning("Found both input file and URL, ignoring URL...")
        inputfile = args.input
        # Ignores option output in the case of input file (presumably multiple URLs)
        output = None 
        list_url = read_from_file(inputfile)
    else:
        # If there is no input file, then the list_url is simply the args.url
        logger.info("Reading list of URLs to download from command line")
        list_url = args.url
    
    list_videos = []
     # Loop on the list of URLs, translate to API URL, get Json content, find the right video (or not), and download it
    for url in list_url:
        program=get_program_from_url(url, site_lang)
        logger.debug("Program to download: {0}".format(program))
     
        json_content = get_json_content(program['api_url'])
        video_found = find_video(json_content, subs, lang, qual)
        list_videos.append(video_found)

        if video_found != None and dlfile == None: 
            if output == None:
                output = dir + program['name'] + '.mp4'
                logger.debug("Setting output to {0}".format(output)) 
            download_video(video_found, output)
        # Ensures output will be computed at each iteration
        output = None    

    if dlfile != None:
        list_todl = []
        count_err = 0
        for video in list_videos:
            if video!=None:
                todl = {'url': video}
                list_todl.append(todl)
            else: count_err+=1
        add_to_file(list_todl,dlfile)
        if count_err !=0: logger.warning("{0} videos could not be found and have not been added to file".format(count_err))

    logger.info("Finished DOWNLOAD command")

# Adds list of programs to output file
def add_to_file(list_programs, outputfile):
    logger.info("Adding list of programs to file {0}".format(outputfile))
    of = open(outputfile, mode='a', closefd=True)
    try:
        for program in list_programs:
            of.write(program['url']+"\n")
    except FileNotFoundError as err:
        logger.error("Inputfile does not exist: {0}".format(err))
        af.close()
        sys.exit(1)
    except IsADirectoryError as err:
        logger.error("You provided a directory, stupid: {0}".format(err))
        af.close()
        sys.exit(1)
    except TypeError as err:
        logger.error("Provided list of programs seems weird, TypeError: {0}".format(err))
        of.close()
        sys.exit(1)
    finally:
        of.close()
    logger.info("Writing to file finished")

# Reads from file, returns a list with the lines (NB : no format check, video download will fail anyway if URL is wrong)
def read_from_file(inputfile):
    logger.info("Reading list of URLs to download from file {0}".format(inputfile))
    list_url = []
    af = open(inputfile, mode='r', closefd=True)
    try:
        for line in af:
            list_url.append(line)
    except FileNotFoundError as err:
        logger.error("Inputfile does not exist: {0}".format(err))
        af.close()
        sys.exit(1)
    except IsADirectoryError as err:
        logger.error("You provided a directory, stupid: {0}".format(err))
        af.close()
        sys.exit(1)
    finally:
        af.close()

    if list_url == None:
        logger.error("Couldn't read from file. Please verify file contents. Aborting...")
        sys.exit(1)

    return list_url

# Finds the right link to video from json content returned by API URL, with selected subs and quality, if possible
def find_video(json_content, subs, lang, qual):

    try:
        logger.info(json_content['videoJsonPlayer']['V7T'])
    except KeyError:
        logger.warning("Could not print description of program, probably because language does not match site version")
   
    program_title = json_content['videoJsonPlayer']['VTI']
    video_list = json_content['videoJsonPlayer']['VSR']
    video_found = None
    video_found_flag = True

    codes = []
    alt_codes = []

    if subs == "mal" and lang == "fr":
        codes = ["VF-STMF"]
        alt_codes = ["VO-STF","VA-STF"]
    if subs == "mal" and lang != "fr":
        logger.warning("Not sure versions exist for hearing impaired people, so will try to download subtitled version instead")
        subs = "yes"

    if subs == "yes" and lang == "fr":
        codes = ["VO-STF","VA-STF"]
        alt_codes = ["VF","VOF-STF","VF-STF","VOF"]
    if subs == "no" and lang == "fr":
        codes = ["VF","VOF-STF","VF-STF","VOF"]
        alt_codes = ["VO-STF","VA-STF"]

    if subs == "yes" and lang == "de":
        codes = ["VO-STA","VA-STA"]
        alt_codes = ["VA","VOA-STA","VA-STA","VOA"]
    if subs == "no" and lang == "de":
        codes = ["VA","VOA-STA","VA-STA","VOA"]
        alt_codes = ["VO-STA","VA-STA"]

    if subs == "no" and lang == "es":
        codes = ["VO"]
        alt_codes = ["VOA-STE[ESP]", "VOF-STE[ESP]", "VO-STE[ESP]"]
    if subs == "yes" and lang == "es":
        codes = ["VOA-STE[ESP]", "VOF-STE[ESP]", "VO-STE[ESP]"]
        alt_codes = ["VO"]
    
    if subs == "no" and lang == "en":
        codes = ["VO"]
        alt_codes = ["VOA-STE[ANG]", "VOF-STE[ANG]", "VO-STE[ANG]"]
    if subs == "yes" and lang == "en":
        codes = ["VOA-STE[ANG]", "VOF-STE[ANG]", "VO-STE[ANG]"]
        codes = ["VO"]

    if subs == "no" and lang == "pl":
        codes = ["VO"]
        alt_codes = ["VOA-STE[POL]", "VOF-STE[POL]", "VO-STE[POL]"]
    if subs == "yes" and lang == "pl":
        codes = ["VOA-STE[POL]", "VOF-STE[POL]", "VO-STE[POL]"]
        codes = ["VO"]   
 
    # We will loop in the list of videos and try to find requested subs version and if not found fall back to the other
    # There is no fallback for quality, assuming arte json always provides the videos in all the different qualities
    for item in video_list:
        video = video_list[item]
        version_code = video['versionCode']
        version_prog = video['versionProg']
        quality = video['quality']
        if version_code in codes and quality == qual:
            logger.info("Found the required version for {0}".format(program_title))
            video_found = video['url']
            video_found_flag = True
            break
        elif version_code in alt_codes and quality == qual:
            video_found = video['url']
            video_found_flag = False
        elif version_prog == 1 and quality == qual:
            video_found = video['url']
            video_found_flag = False
                
    if video_found == None:
        logger.error("Couldn't find a suitable version for {0}".format(program_title))
    else:
        if video_found_flag == False: 
            logger.warning("Couldn't match subtitles preferences, but found video for lang={0} and quality={1}".format(lang,qual))
        logger.info("Download link: {0}".format(video_found))

    return video_found

# Download program with wget
def download_video(video, output):
    #TOFIX This should be done natively in python with requests. Workaround below.
    try:
        process = subprocess.run(['wget','-nv','--show-progress','-O', output, video])
    except OSError as err:
        if err.errno == os.errno.ENOENT:
            logger.warning("Could not find wget, fallback to requests : {0}".format(err))
            download_video_fallback(video, output)
        else:
            logger.error("Some unknown issue {1} occurred with wget: {0}".format(err, err.errno))
    except KeyboardInterrupt as err:
        logger.error("Download interrupted by user: {0}".format(err))
    except subprocess.SubprcessError as err:
        logger.error(err)
        sys.exit(1)
    
    try:
        logger.debug("Wget video terminated with {0}".format(process.returncode))
    # Ugly - allows downloading further videos
    except UnboundLocalError:
        logger.warning("Couldn't retrieve wget return code, probably due to KeyboardInterrupt, continuing program")

# Alternative download in case wget could not be found e.g. Windows. Just download with requests, no such thing as a fancy progress bar.
def download_video_fallback(video, output):

    logger.info("Launching download with requests")
    session = requests.Session()
    session.max_redirects = 3
    try:
        r = requests.get(video, timeout=10)
        r.raise_for_status()
    except requests.exceptions.ConnectionError as err:
        logger.error("Failed to connect to server with error {0}".format(err))
        sys.exit(1)
    except requests.exceptions.Timeout as err:
        logger.error("Exceeded timeout: {0}".format(err))
        sys.exit(1)
    except requests.exceptions.TooManyRedirects as err:
        logger.error("Too many redirects : {0}".format(err))
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        logger.error("HTTP request was unsuccessful with status code {0} : {1}".format(response.status_code,err))
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        logger.error(err)
        sys.exit(1)

    logger.info("Finished downloading with requests")

# Gets program name and api url from the arte tv url
def get_program_from_url(url, site_lang):
    
    logger.info("Retrieving API URL for URL {0}".format(url))

    r = parse.parse("http://www.arte.tv/guide/{lang}/{video_id}/{video_name}", url)
    if r == None: 
        logger.error("Wasn't able to parse URL, exiting...")
        sys.exit(1)
    else:
        video_id = (r.named['video_id'])
        video_name = (r.named['video_name'])
        lang = (r.named['lang'])
        if lang != site_lang:
            logger.warning("Provided arte URL does not match site_lang option. We will use the one from the URL.")
        api_url = 'https://api.arte.tv/api/player/v1/config/{0}/{1}'.format(lang, video_id)
    
    program = {'name': video_name, 'api_url': api_url} 
    logger.info("Found API URL {0} for program name {1}".format(api_url,video_name))

    return program

# Retrieves a list of programs 
def get_list_programs(param, max, site_lang):
    
    if (param == "most_viewed" or "next_expiring" or "newest"):
        url = "http://www.arte.tv/guide/{2}/plus7/videos?limit={1}&sort={0}&country={2}".format(param, max, site_lang)
        logger.info("Getting ready to retrieve list of {0} programs".format(param))
    else:
        logger.error("Provided list parameters don't match, exiting")
        sys.exit(1)
    
    json_content = get_json_content(url)

    list_programs = []
    for program_item in json_content['videos']:
        try:
            program = get_program_from_url(program_item['url'], site_lang)
            program['url']=program_item['url']
            program['date'] = program_item['scheduled_on']
            program['subtitle'] = program_item['subtitle']
            program['teaser'] = program_item['teaser']
            program['views'] = program_item['views']
            list_programs.append(program)
        except KeyError as err:
            #TOFIX in case just one attribute cannot be retrieved, the whole program is not added to list
            logger.warning('Failed to retrieve a program info, but continuing')
            continue

    try:
        logger.debug(json.dumps(list_programs, indent=4, ensure_ascii=False))
    except:
        logger.warning("Could not log debug the json content, not a good sign")
        pass

    if list_programs == []:
        logger.error("Coulnd't retrieve the list of programs, exiting")
        sys.exit(1)

    return list_programs

# Search programs for search_term
def get_search_programs(search_term, site_lang):

    url = "http://www.arte.tv/guide/{1}/programs/autocomplete?q={0}&scope=plus7&country={1}".format(search_term, site_lang)

    json_content = get_json_content(url)

    search_programs_list = []
    for program_item in json_content:
        try:
            program = get_program_from_url(program_item['url'], site_lang)
            program['url']=program_item['url']
            program['title']=program_item['title']
            program['subtitle'] = program_item['subtitle']
            program['duration'] = program_item['duration']
            search_programs_list.append(program)
        except KeyError as err:
            #TOFIX in case just one attribute cannot be retrieved, the whole program is not added to list
            logger.warning('Failed to retrieve a program info, but continuing')
            continue

    try:
        logger.debug(json.dumps(search_programs_list, indent=4, ensure_ascii=False))
    except:
        logger.warning("Could not log debug the json content, not a good sign")
        pass

    if search_programs_list == []:
        logger.error("Coulnd't retrieve the list of programs, exiting")
        sys.exit(1)

    return search_programs_list

# Defining command line arguments
def arg_parser():

    parser = argparse.ArgumentParser("Utility that lists or downloads available videos from arte +7",formatter_class=argparse.RawDescriptionHelpFormatter)

    # Parser used as parent for subparsers, so that log options can be used anywhere on the command line
    log_parser = argparse.ArgumentParser(add_help=False)
    log_parser.add_argument('--logfile', help='Specify a logfile')
    log_parser.add_argument('--loglevel', default='ERROR', choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'],help='Define loglevel when writing to logfile')
    log_parser.add_argument('-v','--verbose', action='count', help='Define console verbosity, repeat up to three times')

    lang_parser = argparse.ArgumentParser(add_help=False)
    lang_parser.add_argument('-sl', '--site_lang', default="fr", choices=['fr','de','en','es','pl'], help="Define arte site to use. Does not relate to video version.")

    subparser = parser.add_subparsers(dest='command')

    # Parser used for print commands
    sub_list_parser = subparser.add_parser('list', help='List most viewed, newest or soon expiring videos in the console or to a file with -f', parents=[log_parser, lang_parser])
    sub_list_parser.add_argument('list', choices=['most_viewed','next_expiring','newest'], help='Can be used with -f/--file')
    sub_list_parser.add_argument('-m', '--max', default=10, help='-- max videos to list, default is 10')
    sub_list_parser.add_argument('-f', '--file', help='used with -l/--list option, append list of URLs to a file that can then be used with i-/--inputfile option.')

    # Parser used to search
    sub_search_parser = subparser.add_parser('search', help='Search on key words and return a list of videos', parents=[log_parser, lang_parser])
    sub_search_parser.add_argument('term', help='Key term to search on, use quotes or double quotes if term contains spaces.')
    sub_search_parser.add_argument('-f', '--file', help='Append list of URLs to a file that can then be used with i-/--inputfile option.')

    # Parser used for download commands
    sub_dl_parser = subparser.add_parser('download', help='Download URL(s) with specified options, or dump downloadable video links to a file', parents=[log_parser, lang_parser])

    # Optional arguments for output. Mutually exclusive group.
    output_group = sub_dl_parser.add_mutually_exclusive_group(required=False)
    output_group.add_argument('-o','--output', help='Download to path/filename. Default is program name.')
    output_group.add_argument('-d', '--dirname', help='--dirname <directory> to download videos to that directory. Cannot be used with --output.')

    # Other video related options
    sub_dl_parser.add_argument('-dlf', '--downloadfile', required=False, help='Program will not attempt to download videos but will add downloadable links to the specified downloadfile')
    sub_dl_parser.add_argument('-l', '--lang', default="fr", choices=['fr','de','en','es','pl'], help="Video version to look for. See README for details.")
    sub_dl_parser.add_argument('-s', '--subs', default="yes", choices = ['yes','no','mal'], help="mal is for hearing impaired people (French only). Fallback: mal > yes, yes > no, no > yes. Default is yes")
    sub_dl_parser.add_argument('-q', '--qual', default="SQ", choices=['MQ','EQ','HQ','SQ','mq','eq','hq','sq'], help='Default is SQ.')
    sub_dl_parser.add_argument('-i','--input', help='--input <filename> to supply a file with a list of URLs to download. -o option ignored. -d option taken into account.')

    # Positional argument
    sub_dl_parser.add_argument('url', nargs='*', help='the URL(s) of the video on arte site.')

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    return args   

# Initiates logger with 2 handlers, a filehandler if file is specified with logfile and loglevel, and a streamhandler for console using verbosity argument
def init_logger(args):

    logger = logging.getLogger('arteget.py')
    logger.setLevel(logging.DEBUG)

    loglevel = args.loglevel
    numeric_level = getattr(logging, loglevel.upper())

    logfile = args.logfile

    if logfile!=None:
        log_file_handler = logging.FileHandler(logfile,mode='a')
        log_file_handler.setLevel(numeric_level)
        log_file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s'))
        logger.addHandler(log_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter( logging.Formatter('[%(levelname)s] %(message)s') )
    logger.addHandler(console_handler)

    if not args.verbose:
        console_handler.setLevel('ERROR')
    elif args.verbose == 1:
        console_handler.setLevel('WARNING')
    elif args.verbose == 2:
        console_handler.setLevel('INFO')
    elif args.verbose >= 3:
        console_handler.setLevel('DEBUG')
    else:
        logger.warning("Wrong verbosity, will default to ERROR")
        console_handler.setLevel('ERROR')

    return logger

# Utilitary method to retrieve json content from an URL
def get_json_content(url):
    session = requests.Session()
    session.max_redirects = 3
    #TODO allow retries on ConnectTimeout
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as err:
        logger.error("Failed to connect to server with error {0}".format(err))
        sys.exit(1)
    except requests.exceptions.Timeout as err:
        logger.error("Exceeded timeout: {0}".format(err))
        sys.exit(1)
    except requests.exceptions.TooManyRedirects as err:
        logger.error("Too many redirects : {0}".format(err))
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        logger.error("HTTP request was unsuccessful with status code {0} : {1}".format(response.status_code,err))
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        logger.error(err)
        sys.exit(1)

    try:
        json_content = json.loads(response.text)
    except json.exceptions.ValueError as err:
        logger.error(err)
        sys.exit(1)

    try:
        logger.debug(json.dumps(json_content, indent=4, ensure_ascii=False))
    except:
        logger.warning("Could not log debug the json content, not a good sign")
        pass

    return json_content

if __name__ == '__main__':
    args = arg_parser() 
    logger = init_logger(args)
    logger.info(args)
    if args.command == 'list':
        handle_list_command(args)        
    elif args.command == 'download':
        handle_download_command(args)
    elif args.command == 'search':
        handle_search_command(args)
    else:
        # Shouldn't happen. argparse should catch this.
        logger.error("Unknown command: {}".format(args.command))
