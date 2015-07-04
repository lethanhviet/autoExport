#!/usr/bin/python

#######################################################
# Import
#######################################################
import sys
import subprocess
from datetime import datetime, date, time, timedelta
from deluge.ui.client import client
import deluge.component as component
from twisted.internet import reactor, defer

# Enable the below for debug log
#import logging
#from deluge.log import LOG as log
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#######################################################
# Customize
#######################################################
labels = ["btn", "btn.packs"]   # Label(s) to export
minseedtime = 3                 # Minimum seeding time in hours
src = "/home/ltv/src/"          # Where is rtorrent_fast_resume.pl kept?
state_folder = "/home/ltv/.config/deluge/state/"        # Link to deluge's state folder
watch_folder = {"btn": "/home/ltv/rtorrent.watch/btn/", "btn.packs": "/home/ltv/rtorrent.watch/btn.packs/"}     # Linkt to rTorrent's watch folder
is_interactive = False          # Set this to True to allow direct output or set to False for cron

#######################################################
# Execute
#######################################################
oldcount = 0
skipcount = 0
errorcount = 0
torrent_ids = []
cliconnect = client.connect()

def printSuccess(dresult, is_success, smsg):
    global is_interactive
    if is_interactive:
        if is_success:
            print "[+]", smsg
        else:
            print "[i]", smsg

def printError(emsg):
    global is_interactive
    if is_interactive:
        print "[e]", emsg

def endSession(esresult):
    if esresult:
        print esresult
        reactor.stop()
    else:
        client.disconnect()
        printSuccess(None, False, "Client disconnected.")
        reactor.stop()

def printReport(rresult):
    if errorcount > 0:
        printError(None, "Failed! Number of errors: %i" % (errorcount))
    else:
        if oldcount > 0:
            printSuccess(None, True, "Moved %i torrents to rTorrent -- Skipped %i torrents" % (oldcount, skipcount))
        else:
            printSuccess(None, True, "No torrent was moved to rTorrent! -- Skipped %i torrents" % (skipcount))
    endSession(None)

def on_torrents_status(torrents):
    tlist=[]
    for torrent_id, status in torrents.items():
        if status["label"] in labels:           # Check if torrent label is part of labels list
            seedtime = datetime.fromtimestamp(status["seeding_time"]) - datetime.fromtimestamp(0)   # Get total seeding time of torrent
            if timedelta(hours = minseedtime) <= seedtime:
                with open(state_folder + torrent_id + ".torrent", "rb", 0) as input_file, open(watch_folder[status["label"]] + torrent_id + ".torrent", "wb", 0) as output_file:
                    global oldcount
                    oldcount += 1
                    successmsg = "Moved %s to rTorrent" % (status["name"])
                    errormsg = "Error moving %s" % (status["name"])
                    subprocess.check_call(["perl", src + "rtorrent_fast_resume.pl", status["save_path"]], stdin=input_file, stdout=output_file)
                    tlist.append(client.core.remove_torrent(torrent_id, False).addCallbacks(printSuccess, printError, callbackArgs = (True, successmsg), errbackArgs = (errormsg)))
            else:
                global skipcount
                skipcount += 1
                printSuccess(None, False, " Skipping %s" % (status["name"]))
    defer.DeferredList(tlist).addCallback(printReport)

def on_session_state(result):
    client.core.get_torrents_status({"id": result}, ["name", "save_path", "seeding_time", "label"]).addCallback(on_torrents_status)

def on_connect_success(result):
    printSuccess(None, True, "Connection was successful!")
    printSuccess(None, False, "Current time is %s" % ((datetime.now())))
    client.core.get_session_state().addCallback(on_session_state)

cliconnect.addCallbacks(on_connect_success, endSession, errbackArgs=("Connection failed: check settings and try again."))

reactor.run()