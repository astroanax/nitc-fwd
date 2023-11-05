#!/usr/bin/env python3
import requests
import logging
import json
import os
import time
import signal
import sys

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

firewall_host = None
magic = None

def login(username, password):
    check_url = "http://networkcheck.kde.org/"
    r = requests.get(check_url)
    if r.url != check_url:
        global firewall_host
        global magic

        firewall_login_url = r.url
        magic = firewall_login_url[r.url.find('?')+1:]
        firewall_host = r.url[:r.url.rfind('/')]
        headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin" : firewall_host,
                "Referer": firewall_login_url
        }
        data = {
                "4Tredir": check_url,
                "magic" : magic,
                "username": "***REMOVED***",
                "password": "***REMOVED***"
        }
        r1 = requests.post(firewall_host+'/', data=data)
        if r1.url == firewall_host + '/':
            logger.error("firewall authentication failed")
            return 1
        elif r1.url == firewall_login_url:
            logger.error("authentication limit reached")
            return 2
        else:
            logger.info("logged in, keepalive url is " + r1.url)
            config_file_loc = get_config_file_loc()
            config = {}
            with open(config_file_loc, "r+") as f:
                config = json.load(f)
                config["keepalive"] = r1.url
            with open(config_file_loc, "w") as f:
                json.dump(config, f)
            return r1.url

    logger.info("no login; internet already accessible")
    return 0

def handle_kill(signum, frame):
    logging.error("received signal " + str(signum))
    try:
        r = requests.get(firewall_host + '/logout?' + magic)
        if r.status_code == 200:
            logging.info("successfully logged out")
        else:
            logging.info("error logging out")
            exit(2)
    except Exception as e:
        logging.error(e)
    exit(1)

def keepalive(keepalive_url):
    while True:
        time.sleep(10*60)
        requests.get(keepalive_url)

def get_config_file_loc():
    try:
        config_file_dir = os.environ["XDG_CONFIG_HOME"] + '/'
    except KeyError:
        config_file_dir = os.environ["HOME"] + '/.config/'
        logger.info("$XDG_CONFIG_HOME not set; using $HOME/.config/ as default for configuration directory")
    config_file_loc = config_file_dir + 'nitc-fwd-config.json'
    return config_file_loc

def main():
    signal.signal(signal.SIGINT, handle_kill)
    signal.signal(signal.SIGTERM, handle_kill)
    config_file_loc = get_config_file_loc()
    try:
        with open(config_file_loc, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.info("creating new config file at " + str(config_file_loc))
        with open(config_file_loc, 'w') as f:
            username = input("enter username: ")
            password = input("enter password: ")
            config = {"username": username, "password": password}
            json.dump(config, f)
    if "keepalive" in config.keys():
        firewall_keepalive_url = config["keepalive"]
        logger.info("loaded existing keepalive url from config")
        try:
            requests.get(firewall_keepalive_url)
            logger.info("using old keepalive, " + firewall_keepalive_url)
            keepalive(firewall_keepalive_url)
        except Exception as e:
            logging.error("failed not use old keepalive, re-logging in")
            username = config["username"]
            password = config["password"]
            
            firewall_keepalive_url = login(username, password)
            if type(firewall_keepalive_url) == int:
                return firewall_keepalive_url
            else:
                keepalive(firewall_keepalive_url)
    else:
        username = config["username"]
        password = config["password"]
        
        firewall_keepalive_url = login(username, password)
        if type(firewall_keepalive_url) == int:
            return firewall_keepalive_url
        else:
            keepalive(firewall_keepalive_url)

if __name__ == '__main__':
    main()
