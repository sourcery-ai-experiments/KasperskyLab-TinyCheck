#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.utils import read_config
from app.classes.iocs import IOCs
from app.classes.whitelist import WhiteList

import requests
import json
import urllib3
import time
from multiprocessing import Process

"""
    This file is parsing the watchers present 
    in the configuration file. This in order to get 
    automatically new iocs / elements from remote 
    sources without user interaction.

    As of today the default export JSON format from 
    the backend and unauthenticated HTTP requests
    are accepted. The code is little awkward, it'll
    be better in a next version ;)
"""

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def watch_iocs():
    """
        Retrieve IOCs from the remote URLs defined in config/watchers.
        For each (new ?) IOC, add it to the DB.
    """

    # Retrieve the URLs from the configuration
    urls = read_config(("watchers", "iocs"))
    watchers = [{"url": url, "status": False} for url in urls]

    while True:
        for w in watchers:
            if w["status"] == False:
                iocs = IOCs()
                iocs_list = []
                try:
                    res = requests.get(w["url"], verify=False)
                    if res.status_code == 200:
                        iocs_list = json.loads(res.content)["iocs"]
                    else:
                        w["status"] = False
                except:
                    w["status"] = False

                for ioc in iocs_list:
                    try:
                        iocs.add(ioc["type"], ioc["tag"],
                                 ioc["tlp"], ioc["value"], "watcher")
                        w["status"] = True
                    except:
                        continue

        # If at least one URL haven't be parsed, let's retry in 1min.
        if False in [w["status"] for w in watchers]:
            time.sleep(60)
        else:
            break


def watch_whitelists():
    """
        Retrieve whitelist elements from the remote URLs 
        defined in config/watchers. For each (new ?) element, 
        add it to the DB.
    """

    urls = read_config(("watchers", "whitelists"))
    watchers = [{"url": url, "status": False} for url in urls]

    while True:
        for w in watchers:
            if w["status"] == False:
                whitelist = WhiteList()
                elements = []
                try:
                    res = requests.get(w["url"], verify=False)
                    if res.status_code == 200:
                        elements = json.loads(res.content)["elements"]
                    else:
                        w["status"] = False
                except:
                    w["status"] = False

                for elem in elements:
                    try:
                        whitelist.add(elem["type"], elem["element"], "watcher")
                        w["status"] = True
                    except:
                        continue

        if False in [w["status"] for w in watchers]:
            time.sleep(60)
        else:
            break


p1 = Process(target=watch_iocs)
p2 = Process(target=watch_whitelists)

p1.start()
p2.start()