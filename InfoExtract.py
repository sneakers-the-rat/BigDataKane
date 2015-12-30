__author__ = 'Jonny'
import pattern.web
import re, sys, os
from os import walk
from operator import itemgetter
from pattern.web import plaintext, DOM
from bs4 import BeautifulSoup
from collections import Counter
import pattern.vector as vec
import os
import progressbar
import csv
import pickle
import json

basedir = "/Users/Jonny/Documents/Scripting/RapResults/RapGenius/"
common_words_file = "/Users/Jonny/Documents/Scripting/RapResults/CommonWords"
results_basedir = "/Users/Jonny/Documents/Scripting/RapResults/"
stop_names_file = "/Users/Jonny/Documents/Scripting/RapResults/stop_names"
artist_names_file = "/Users/Jonny/Documents/Scripting/RapResults/indexes/artist_names"
lyrics_index_dir = "/Users/Jonny/Documents/Scripting/RapResults/IndexedLyrics/"
indexes_dir = "/Users/Jonny/Documents/Scripting/RapResults/indexes/"

def get_artist_names(dir = basedir):
    f = open(artist_names_file, 'w')
    artistnames = []
    for dir in os.listdir(basedir):
        # dir names are the name of the artist, separated by -, like jay-z
        name1 = re.split('-', dir)
        for n in name1:
            artistnames.extend(n)
            f.write(n)
            f.write("\n")
            print n
    f.close()
    return artistnames


def make_song_list(artist_name):
    allfiles = []
    dir = basedir + artist_name
    filenames = os.listdir(dir)
    for f in filenames:
            if re.search( '\.git', f):
                continue
            else:
                allfiles.append(os.path.join(dir,f))
    return allfiles

def get_files(dir):
    global filenames
    filenames = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            filenames[len(filenames):] = [os.path.join(root, name)]

def extract_song_info(dir):
    global filenames
    #making these global in case the json dump fails we can still use them in-session.
    global fileid
    global idfile
    global artistsongid
    global songidartist
    get_files(dir)
    #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(filenames)).start()
    idcount = 0 #to assign unique id to each lyrics file
    print len(filenames) #to keep track of function progress... inelegantly...
    fileid = dict() #two dictionaries to move back and forth between ids and filenames
    idfile = dict()
    artistsongid = dict() #"" between artists and ids
    songidartist = dict()
    for i in filenames:
        art = list()
        print idcount + "/" + len(filenames) #"progress bar"
        fileid[i] = idcount
        idfile[idcount] = [i]
        ##open and read file with beautifulsoup
        f = open(i, 'r')
        page = f.read()
        soup = BeautifulSoup(page, "html.parser")
        soup.prettify()
        ##get artists from page and index them
        for artists in soup.find_all(href=re.compile("artist")):
            addart = artists.string
            if addart != "Verified Artists":
                art[len(art):] = [addart]
                songidartist[idcount] = art #index all artists for given song by id
        for i in art:
            if i in artistsongid.keys():
                existlist = [artistsongid[i]]
                newlist = [existlist[:], idcount]
                artistsongid[i] = (newlist) #and vice versa
            else:artistsongid[i] = idcount
        ######################################
        #failed attempts at saving the indexes
        #pickle.dump(artistsongid, open(as_index_file, "wb"))
        #pickle.dump(songidartist, open(sa_index_file, "wb"))
        #aa = csv.writer(codecs.open(as_index_file, 'w', encoding='utf_8', errors='ignore'))
        #bb = csv.writer(codecs.open(sa_index_file, 'w', encoding='utf_8', errors='ignore'))
        #for key, val in artistsongid.items():
        #    aa.writerow([key, val])
        #    bb.writerow([val, key])
        ########################################
        #Extract lyrics as plain text and save as indexed file
        lyrics = soup.select(".lyrics")
        if lyrics:
            lyrics_string = lyrics[0].text
            lyrics_string = lyrics_string.encode('ascii',errors='ignore')
            lyrics_file = lyrics_index_dir + str(idcount)
            f = open(lyrics_file, 'w')
            f.write(lyrics_string)
            f.close()
        else: ""
        #pbar.update(idcount)
        idcount = idcount + 1
    #save indices
    as_index_file = indexes_dir + "ArtistSongID"
    sa_index_file = indexes_dir + "SongIDArtist"
    fileid_file = indexes_dir + "FileID"
    idfile_file = indexes_dir + "IDFile"
    f = open(as_index_file, 'w')
    json.dump(artistsongid, f)
    f.close()
    f = open(sa_index_file, 'w')
    json.dump(songidartist, f)
    f.close()
    f = open(fileid_file, 'w')
    json.dump(fileid, f)
    f.close()
    f = open(idfile_file, 'w')
    json.dump(idfile, f)
    f.close()

def make_indices(dir):
    ##just the index part of extract_song_info
    global filenames
    #making these global in case the json dump fails we can still use them in-session.
    global fileid
    global idfile
    global artistsongid
    global songidartist
    get_files(dir)
    idcount = 0
    print len(filenames) #to keep track of function progress... inelegantly...
    fileid = dict() #two dictionaries to move back and forth between ids and filenames
    idfile = dict()
    artistsongid = dict() #"" between artists and ids
    songidartist = dict()

    for i in filenames:
        art = list()
        print(idcount, "/", len(filenames)) #"progress bar"
        fileid[i] = idcount
        idfile[idcount] = [i]
        ##open and read file with beautifulsoup
        f = open(i, 'r')
        page = f.read()
        soup = BeautifulSoup(page, "html.parser")
        soup.prettify()
        ##get artists from page and index them
        for artists in soup.find_all(href=re.compile("artist")):
            addart = artists.string
            #addart = addart.encode('ascii',errors='replace')
            if addart != "Verified Artists":
                art[len(art):] = [addart]
                songidartist[idcount] = addart #index all artists for given song by id
        for i in art:
            artistsongid[i] = idcount
        idcount = idcount + 1
    as_index_file = indexes_dir + "ArtistSongID"
    sa_index_file = indexes_dir + "SongIDArtist"
    fileid_file = indexes_dir + "FileID"
    idfile_file = indexes_dir + "IDFile"
    f = open(as_index_file, 'w')
    json.dump(artistsongid, f)
    f.close()
    f = open(sa_index_file, 'w')
    json.dump(songidartist, f)
    f.close()
    f = open(fileid_file, 'w')
    json.dump(fileid, f)
    f.close()
    f = open(idfile_file, 'w')
    json.dump(idfile, f)
    f.close()
##save fileid and idfile dictionaries at the end too
##clean lyrics of names
##count words, exlude words
##Lyrics in SongIndex# files
##Artist:SongIndex, SongIndex:SongName
