import json
import trio
from tqdm import tqdm
from bs4 import BeautifulSoup
from termcolor import colored
import httpx
from subprocess import Popen, PIPE
import os
from argparse import ArgumentParser
import csv
from datetime import datetime
import time
import importlib
import pkgutil
import hashlib
import re
import sys
import string
import random

try:
    import cookielib
except Exception:
    import http.cookiejar as cookielib

DEBUG = False
EMAIL_FORMAT = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
VERSION = "2.0"

ua = json.loads('''{"browsers": {"chrome": ["Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36", "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36", "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36", "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36", "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36", "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15", "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14"], "firefox": ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0", "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0", "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0", "Mozilla/5.0 (X11; OpenBSD amd64; rv:28.0) Gecko/20100101 Firefox/28.0", "Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0", "Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3", "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:27.0) Gecko/20121011 Firefox/27.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0", "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0", "Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/23.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:23.0) Gecko/20131011 Firefox/23.0", "Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/22.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0", "Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20130405 Firefox/22.0", "Mozilla/5.0 (Microsoft Windows NT 6.2.9200.0); rv:22.0) Gecko/20130405 Firefox/22.0", "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/21.0.1", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/21.0.1", "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:21.0.0) Gecko/20121011 Firefox/21.0.0", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (X11; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20130514 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.2; rv:21.0) Gecko/20130326 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130401 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130331 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130330 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130328 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130401 Firefox/21.0", "Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130331 Firefox/21.0", "Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (Windows NT 5.0; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0", "Mozilla/5.0 (Windows NT 6.2; Win64; x64;) Gecko/20100101 Firefox/20.0", "Mozilla/5.0 (Windows x86; rv:19.0) Gecko/20100101 Firefox/19.0", "Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20100101 Firefox/19.0", "Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/18.0.1", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0)  Gecko/20100101 Firefox/18.0", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6"], "safari": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A", "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10", "Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3"]}}''')

class TrioProgress(trio.abc.Instrument):
    def __init__(self, total):
        self.tqdm = tqdm(total=total)
    def task_exited(self, task):
        if task.name.split(".")[-1] == "launch_module":
            self.tqdm.update(1)

def import_submodules(package, recursive=True):
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results

def get_functions(modules, args=None):
    websites = []
    for module in modules:
        if len(module.split(".")) > 3:
            modu = modules[module]
            site = module.split(".")[-1]
            if args is not None and args.nopasswordrecovery:
                if "adobe" not in str(modu.__dict__[site]) and "mail_ru" not in str(modu.__dict__[site]) and "odnoklassniki" not in str(modu.__dict__[site]) and "samsung" not in str(modu.__dict__[site]):
                    websites.append(modu.__dict__[site])
            else:
                websites.append(modu.__dict__[site])
    return websites

def check_update():
    check_version = httpx.get("https://pypi.org/pypi/holehe/json")
    if check_version.json()["info"]["version"] != VERSION:
        if os.name != 'nt':
            p = Popen(["pip3", "install", "--upgrade", "holehe"], stdout=PIPE, stderr=PIPE)
        else:
            p = Popen(["pip", "install", "--upgrade", "holehe"], stdout=PIPE, stderr=PIPE)
        p.communicate()
        p.wait()
        print("Axomic OSINT has been updated, please restart.")
        exit()

def credit():
    print('Creator: Axom')
    print('Tool: Axomic OSINT')
    print('GitHub: https://github.com/Axom/axomicosint')

def is_email(email):
    return bool(re.fullmatch(EMAIL_FORMAT, email))

def print_result(data, args, email, start_time, websites):
    def print_color(text, color, args):
        if not args.nocolor:
            return colored(text, color)
        return text
    description = (print_color("[+] Email used", "green", args) + "," +
                   print_color(" [-] Email not used", "magenta", args) + "," +
                   print_color(" [x] Rate limit", "yellow", args) + "," +
                   print_color(" [!] Error", "red", args))
    if not args.noclear:
        print("\033[H\033[J")
    else:
        print("\n")
    print("*" * (len(email) + 6))
    print("   " + email)
    print("*" * (len(email) + 6))
    for results in data:
        if results["rateLimit"] and not args.onlyused:
            print(print_color("[x] " + results["domain"], "yellow", args))
        elif "error" in results.keys() and results["error"] and not args.onlyused:
            toprint = ""
            if results["others"] is not None and "Message" in str(results["others"].keys()):
                toprint = " Error message: " + results["others"]["errorMessage"]
            print(print_color("[!] " + results["domain"] + toprint, "red", args))
        elif not results["exists"] and not args.onlyused:
            print(print_color("[-] " + results["domain"], "magenta", args))
        elif results["exists"]:
            toprint = ""
            if results["emailrecovery"] is not None:
                toprint += " " + results["emailrecovery"]
            if results["phoneNumber"] is not None:
                toprint += " / " + results["phoneNumber"]
            if results["others"] is not None and "FullName" in str(results["others"].keys()):
                toprint += " / FullName " + results["others"]["FullName"]
            if results["others"] is not None and "Date, time of the creation" in str(results["others"].keys()):
                toprint += " / Date, time of the creation " + results["others"]["Date, time of the creation"]
            print(print_color("[+] " + results["domain"] + toprint, "green", args))
    print("\n" + description)
    print(str(len(websites)) + " websites checked in " + str(round(time.time() - start_time, 2)) + " seconds")

def export_csv(data, args, email):
    if args.csvoutput:
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        name_file = "axomic_" + str(round(timestamp)) + "_" + email + "_results.csv"
        with open(name_file, 'w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(output_file, fieldnames=data[0].keys())
            fc.writeheader()
            fc.writerows(data)
        exit("Results exported to " + name_file)

async def launch_module(module, email, client, out):
    data = {'adobe': 'adobe.com', 'amazon': 'amazon.com', 'atlassian': 'atlassian.com', 'bitmoji': 'bitmoji.com', 'codecademy': 'codecademy.com', 'codepen': 'codepen.io', 'devrant': 'devrant.com', 'diigo': 'diigo.com', 'discord': 'discord.com', 'duolingo': 'duolingo.com', 'ebay': 'ebay.com', 'facebook': 'facebook.com', 'fanpop': 'fanpop.com', 'github': 'github.com', 'google': 'google.com', 'gravatar': 'gravatar.com', 'imgur': 'imgur.com', 'instagram': 'instagram.com', 'laposte': 'laposte.fr', 'mail_ru': 'mail.ru', 'myspace': 'myspace.com', 'nike': 'nike.com', 'pinterest': 'pinterest.com', 'protonmail': 'protonmail.ch', 'quora': 'quora.com', 'replit': 'replit.com', 'rocketreach': 'rocketreach.co', 'samsung': 'samsung.com', 'snapchat': 'snapchat.com', 'soundcloud': 'soundcloud.com', 'spotify': 'spotify.com', 'teamtreehouse': 'teamtreehouse.com', 'tunefind': 'tunefind.com', 'twitter': 'twitter.com', 'venmo': 'venmo.com', 'voxmedia': 'voxmedia.com', 'vsco': 'vsco.co', 'wattpad': 'wattpad.com', 'wordpress': 'wordpress.com', 'xing': 'xing.com', 'yahoo': 'yahoo.com'}
    try:
        await module(email, client, out)
    except Exception:
        name = str(module).split('<function ')[1].split(' ')[0]
        out.append({"name": name, "domain": data.get(name, name), "rateLimit": False, "error": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def facebook(email, client, out):
    name = "facebook"
    domain = "facebook.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Origin': 'https://www.facebook.com', 'DNT': '1', 'Connection': 'keep-alive'}
    try:
        response = await client.get("https://www.facebook.com/accounts/emailsignup/", headers=headers)
        if response.status_code == 404:
            raise Exception("Endpoint not found")
        token = response.text.split('{"config":{"csrf_token":"')[1].split('"')[0]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = {'email': email, 'username': ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(random.randint(6, 30))), 'first_name': '', 'opt_into_one_tap': 'false'}
    headers["x-csrftoken"] = token
    try:
        check = await client.post("https://www.facebook.com/api/v1/web/accounts/web_create_ajax/attempt/", data=data, headers=headers)
        check = check.json()
        if check["status"] != "fail":
            if 'email' in check["errors"].keys():
                if check["errors"]["email"][0]["code"] == "email_is_taken":
                    out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
                elif "email_sharing_limit" in str(check["errors"]):
                    out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
            else:
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def atlassian(email, client, out):
    name = "atlassian"
    domain = "atlassian.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://id.atlassian.com/', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Origin': 'https://id.atlassian.com', 'DNT': '1', 'Connection': 'keep-alive'}
    try:
        r = await client.get("https://id.atlassian.com/login", headers=headers)
        data = {'csrfToken': r.text.split('{&quot;csrfToken&quot;:&quot;')[1].split('&quot')[0], 'username': email}
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    response = await client.post('https://id.atlassian.com/rest/check-username', headers=headers, data=data)
    if response.json()["action"] == "signup":
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})

async def gravatar(email, client, out):
    name = "gravatar"
    domain = "en.gravatar.com"
    method = "other"
    frequent_rate_limit = False
    hashed_name = hashlib.md5(email.encode()).hexdigest()
    r = await client.get(f'https://en.gravatar.com/{hashed_name}.json')
    if r.status_code != 200:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    else:
        try:
            data = r.json()
            FullName = data['entry'][0]['displayName']
            others = {'FullName': str(FullName) + " / " + str(data['entry'][0]["profileUrl"])}
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": others})
            return None
        except Exception:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
            return None

async def wordpress(email, client, out):
    name = "wordpress"
    domain = "wordpress.com"
    method = "login"
    frequent_rate_limit = False
    cookies = {'G_ENABLED_IDPS': 'google', 'ccpa_applies': 'true', 'usprivacy': '1YNN', 'landingpage_currency': 'EUR', 'wordpress_test_cookie': 'WP+Cookie+check'}
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    params = {'http_envelope': '1', 'locale': 'fr'}
    try:
        response = await client.get('https://public-api.wordpress.com/rest/v1.1/users/' + email + '/auth-options', headers=headers, params=params, cookies=cookies)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    info = response.json()
    if "email_verified" in info["body"].keys():
        if info["body"]["email_verified"]:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif "unknown_user" in str(info) or "email_login_not_allowed" in str(info):
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def voxmedia(email, client, out):
    name = "voxmedia"
    domain = "voxmedia.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://auth.voxmedia.com/login', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://auth.voxmedia.com', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    data = {'email': email}
    response = await client.post('https://auth.voxmedia.com/chorus_auth/email_valid.json', headers=headers, data=data)
    try:
        rep = response.json()
        if rep["available"]:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif rep["message"] == "You cannot use this email address.":
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def rocketreach(email, client, out):
    name = "rocketreach"
    domain = "rocketreach.co"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://rocketreach.co/signup', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    try:
        response = await client.get("https://rocketreach.co/signup")
        token = re.search(r'name="csrfmiddlewaretoken" value="(.*)"', response.text).group(1)
        headers["x-csrftoken"] = token
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    try:
        r = await client.get('https://rocketreach.co/v1/validateEmail?email_address=' + email, headers=headers)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    if r.json()["found"]:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif not r.json()["found"]:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def ebay(email, client, out):
    name = "ebay"
    domain = "ebay.com"
    method = "login"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Origin': 'https://www.ebay.com', 'DNT': '1', 'Connection': 'keep-alive'}
    try:
        req = await client.get("https://www.ebay.com/signin/", headers=headers)
        srt = req.text.split('"csrfAjaxToken":"')[1].split('"')[0]
    except IndexError:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = {'identifier': email, 'srt': srt}
    req = await client.post('https://signin.ebay.com/signin/srv/identifer', data=data, headers=headers)
    results = json.loads(req.text)
    if "err" in results.keys():
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})

async def amazon(email, client, out):
    name = "amazon"
    domain = "amazon.com"
    method = "login"
    frequent_rate_limit = False
    headers = {"User-agent": random.choice(ua["browsers"]["chrome"])}
    try:
        url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
        req = await client.get(url, headers=headers)
        body = BeautifulSoup(req.text, 'html.parser')
        data = dict([(x["name"], x["value"]) for x in body.select('form input') if ('name' in x.attrs and 'value' in x.attrs)])
        data["email"] = email
        req = await client.post(f'https://www.amazon.com/ap/signin/', data=data)
        body = BeautifulSoup(req.text, 'html.parser')
        if body.find("div", {"id": "auth-password-missing-alert"}):
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def nike(email, client, out):
    name = "nike"
    domain = "nike.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'Content-Type': 'text/plain;charset=UTF-8', 'Origin': 'https://www.nike.com', 'DNT': '1', 'Connection': 'keep-alive', 'Referer': 'https://www.nike.com/', 'TE': 'Trailers'}
    params = {'appVersion': '831', 'experienceVersion': '831', 'uxid': 'com.nike.commerce.nikedotcom.web', 'locale': 'fr_FR', 'backendEnvironment': 'identity', 'browser': '', 'mobile': 'false', 'native': 'false', 'visit': '1'}
    data = '{"emailAddress":"' + email + '"}'
    try:
        response = await client.post('https://unite.nike.com/account/email/v1', headers=headers, params=params, data=data)
        if response.status_code == 409:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif response.status_code == 204:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def samsung(email, client, out):
    name = "samsung"
    domain = "samsung.com"
    method = "password recovery"
    frequent_rate_limit = False
    req = await client.get("https://account.samsung.com/accounts/v1/Samsung_com_FR/signUp")
    token = req.text.split("sJSESSIONID")[1].split('"')[1].split('"')[0]
    crsf = req.text.split("{'token' : '")[1].split("'")[0]
    cookies = {'EUAWSIAMSESSIONID': token}
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://account.samsung.com/accounts/v1/Samsung_com_FR/signUp', 'Content-Type': 'application/json; charset=UTF-8', 'X-CSRF-TOKEN': crsf, 'Origin': 'https://account.samsung.com', 'DNT': '1', 'Connection': 'keep-alive'}
    params = {'v': random.randrange(1000, 9999)}
    data = '{"emailID":"' + email + '"}'
    response = await client.post('https://account.samsung.com/accounts/v1/Samsung_com_FR/signUpCheckEmailIDProc', headers=headers, params=params, cookies=cookies, data=data)
    data = response.json()
    if response.status_code == 200:
        if "rtnCd" in data.keys() and "INAPPROPRIATE_CHARACTERS" not in response.text and "accounts aren't supported." not in response.text:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def codepen(email, client, out):
    name = "codepen"
    domain = "codepen.io"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://codepen.io/accounts/signup/user/free', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://codepen.io', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    try:
        req = await client.get("https://codepen.io/accounts/signup/user/free", headers=headers)
        soup = BeautifulSoup(req.content, features="html.parser")
        token = soup.find(attrs={"name": "csrf-token"}).get("content")
        headers["X-CSRF-Token"] = token
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = {'attribute': 'email', 'value': email, 'context': 'user'}
    response = await client.post('https://codepen.io/accounts/duplicate_check', headers=headers, data=data)
    if "That Email is already taken." in response.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def github(email, client, out):
    name = "github"
    domain = "github.com"
    method = "register"
    frequent_rate_limit = False
    freq = await client.get("https://github.com/join")
    token_regex = re.compile(r'<auto-check src="/signup_check/username[\s\S]*?value="([\S]+)"[\s\S]*<auto-check src="/signup_check/email[\s\S]*?value="([\S]+)"')
    token = re.findall(token_regex, freq.text)
    data = {"value": email, "authenticity_token": token[0]}
    req = await client.post("https://github.com/signup_check/email", data=data)
    if "Your browser did something unexpected." in req.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": None, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif req.status_code == 422:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif req.status_code == 200:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": None, "emailrecovery": None, "phoneNumber": None, "others": None})

async def replit(email, client, out):
    name = "replit"
    domain = "replit.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'application/json', 'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3', 'content-type': 'application/json', 'x-requested-with': 'XMLHttpRequest', 'Origin': 'https://replit.com', 'Connection': 'keep-alive'}
    data = '{"email":"' + str(email) + '"}'
    response = await client.post('https://replit.com/data/user/exists', headers=headers, data=data)
    try:
        if response.json()['exists']:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def teamtreehouse(email, client, out):
    name = "teamtreehouse"
    domain = "teamtreehouse.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://teamtreehouse.com/subscribe/new?trial=yes', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://teamtreehouse.com', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    req = await client.get("https://teamtreehouse.com/subscribe/new?trial=yes", headers=headers)
    soup = BeautifulSoup(req.content, features="html.parser")
    token = soup.find(attrs={"name": "csrf-token"}).get("content")
    headers['X-CSRF-Token'] = token
    data = {'email': email}
    response = await client.post('https://teamtreehouse.com/account/email_address', headers=headers, data=data)
    if 'that email address is taken.' in response.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif response.text == '{"success":true}':
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def devrant(email, client, out):
    name = "devrant"
    domain = "devrant.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://devrant.com', 'Connection': 'keep-alive', 'Referer': 'https://devrant.com/feed/top/month?login=1'}
    data = {'app': '3', 'type': '1', 'email': email, 'username': '', 'password': '', 'guid': '', 'plat': '3', 'sid': '', 'seid': ''}
    try:
        response = await client.post('https://devrant.com/api/users', headers=headers, data=data)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    result = response.json()['error']
    if result == 'The email specified is already registered to an account.':
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def codecademy(email, client, out):
    name = "codecademy"
    domain = "codecademy.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://www.codecademy.com/register?redirect=%2', 'Content-Type': 'application/json', 'Origin': 'https://www.codecademy.com', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    req = await client.get("https://www.codecademy.com/register?redirect=%2F", headers=headers)
    soup = BeautifulSoup(req.content, features="html.parser")
    try:
        headers["X-CSRF-Token"] = soup.find(attrs={"name": "csrf-token"}).get("content")
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = '{"user":{"email":"' + email + '"}}'
    response = await client.post('https://www.codecademy.com/register/validate', headers=headers, data=data)
    if 'is already taken' in response.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def discord(email, client, out):
    name = "discord"
    domain = "discord.com"
    method = "register"
    frequent_rate_limit = False
    def get_random_string(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en-US', 'Content-Type': 'application/json', 'Origin': 'https://discord.com', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    data = '{"fingerprint":"","email":"' + str(email) + '","username":"' + get_random_string(20) + '","password":"' + get_random_string(20) + '","invite":null,"consent":true,"date_of_birth":"","gift_code_sku_id":null,"captcha_key":null}'
    response = await client.post('https://discord.com/api/v8/auth/register', headers=headers, data=data)
    responseData = response.json()
    try:
        if "code" in responseData.keys():
            try:
                if responseData["errors"]["email"]["_errors"][0]['code'] == "EMAIL_ALREADY_REGISTERED":
                    out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
                else:
                    out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
            except Exception:
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif responseData["captcha_key"][0] == "captcha-required":
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def bitmoji(email, client, out):
    name = "bitmoji"
    domain = "bitmoji.com"
    method = "login"
    frequent_rate_limit = False
    try:
        req = await client.get("https://accounts.snapchat.com")
        xsrf = req.text.split('data-xsrf="')[1].split('"')[0]
        webClientId = req.text.split('ata-web-client-id="')[1].split('"')[0]
        url = "https://accounts.snapchat.com/accounts/merlin/login"
        headers = {"Host": "accounts.snapchat.com", "User-Agent": random.choice(ua["browsers"]["firefox"]), "Accept": "*/*", "X-XSRF-TOKEN": xsrf, "Accept-Encoding": "gzip, late", "Content-Type": "application/json", "Connection": "close", "Cookie": "xsrf_token=" + xsrf + "; web_client_id=" + webClientId}
        data = '{"email":' + email + ',"app":"BITMOJI_APP"}'
        response = await client.post(url, data=data, headers=headers)
        if response.status_code != 204:
            data = response.json()
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": data["hasBitmoji"], "emailrecovery": None, "phoneNumber": None, "others": None})
            return None
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def imgur(email, client, out):
    name = "imgur"
    domain = "imgur.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'https://imgur.com', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    r = await client.get("https://imgur.com/register?redirect=%2Fuser", headers=headers)
    headers["X-Requested-With"] = "XMLHttpRequest"
    data = {'email': email}
    response = await client.post('https://imgur.com/signin/ajax_email_available', headers=headers, data=data)
    if response.status_code == 200:
        if response.json()["data"]["available"] or "Invalid email domain" in response.text:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def pinterest(email, client, out):
    name = "pinterest"
    domain = "pinterest.com"
    method = "register"
    frequent_rate_limit = False
    req = await client.get("https://www.pinterest.com/_ngjs/resource/EmailExistsResource/get/", params={"source_url": "/", "data": '{"options": {"email": "' + email + '"}, "context": {}}'})
    if 'source_field' in str(req.json()["resource_response"]["data"]):
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif req.json()["resource_response"]["data"]:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def instagram(email, client, out):
    name = "instagram"
    domain = "instagram.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Origin': 'https://www.instagram.com', 'DNT': '1', 'Connection': 'keep-alive'}
    try:
        freq = await client.get("https://www.instagram.com/accounts/emailsignup/", headers=headers)
        token = freq.text.split('{\\"config\\":{\\"csrf_token\\":\\"')[1].split('\\"')[0]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = {'email': email, 'username': ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(random.randint(6, 30))), 'first_name': '', 'opt_into_one_tap': 'false'}
    headers["x-csrftoken"] = token
    check = await client.post("https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/", data=data, headers=headers)
    check = check.json()
    if check["status"] != "fail":
        if 'email' in check["errors"].keys():
            if check["errors"]["email"][0]["code"] == "email_is_taken":
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
            elif "email_sharing_limit" in str(check["errors"]):
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def snapchat(email, client, out):
    name = "snapchat"
    domain = "snapchat.com"
    method = "login"
    frequent_rate_limit = False
    req = await client.get("https://accounts.snapchat.com")
    xsrf = req.text.split('data-xsrf="')[1].split('"')[0]
    webClientId = req.text.split('ata-web-client-id="')[1].split('"')[0]
    url = "https://accounts.snapchat.com/accounts/merlin/login"
    headers = {"Host": "accounts.snapchat.com", "User-Agent": random.choice(ua["browsers"]["firefox"]), "Accept": "*/*", "X-XSRF-TOKEN": xsrf, "Accept-Encoding": "gzip, late", "Content-Type": "application/json", "Connection": "close", "Cookie": "xsrf_token=" + xsrf + "; web_client_id=" + webClientId}
    data = '{"email":' + email + ',"app":"BITMOJI_APP"}'
    response = await client.post(url, data=data, headers=headers)
    try:
        if response.status_code != 204:
            data = response.json()
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": data["hasSnapchat"], "emailrecovery": None, "phoneNumber": None, "others": None})
            return None
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def twitter(email, client, out):
    name = "twitter"
    domain = "twitter.com"
    method = "register"
    frequent_rate_limit = False
    try:
        req = await client.get("https://api.twitter.com/i/users/email_available.json", params={"email": email})
        if req.json()["taken"]:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def vsco(email, client, out):
    name = "vsco"
    domain = "vsco.co"
    method = "register"
    frequent_rate_limit = False
    headers = {'Authorization': 'Bearer 7356455548d0a1d886db010883388d08be84d0c9'}
    try:
        r = await client.get(f'https://api.vsco.co/2.0/users/email?email={email}', headers=headers)
        resp = r.json()
        if resp["email_status"] == "has_account":
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif resp["email_status"] == "no_account":
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def xing(email, client, out):
    name = "xing"
    domain = "xing.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language': 'en,en-US;q=0.5', 'DNT': '1', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1'}
    try:
        response = await client.get("https://www.xing.com/start/signup?registration=1", headers=headers)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    headers['x-csrf-token'] = response.cookies["xing_csrf_token"]
    data = {'signup_minireg': {'email': email, 'password': '', 'tandc_check': '1', 'signup_channel': 'minireg_fullpage', 'first_name': '', 'last_name': ''}}
    response = await client.post('https://www.xing.com/welcome/api/signup/validate', headers=headers, json=data)
    try:
        errors = response.json()["errors"]
        if "signup_minireg[email]" in errors and errors["signup_minireg[email]"].startswith("We already know this e-mail address."):
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def wattpad(email, client, out):
    name = "wattpad"
    domain = "wattpad.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3', 'Connection': 'keep-alive', 'Referer': 'https://www.wattpad.com/', 'TE': 'Trailers'}
    try:
        await client.get("https://www.wattpad.com", headers=headers)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    headers["X-Requested-With"] = 'XMLHttpRequest'
    params = {'email': email}
    response = await client.get('https://www.wattpad.com/api/v3/users/validate', headers=headers, params=params)
    if response.status_code == 200 or response.status_code == 400:
        if "Cette adresse" not in response.text or response.text == '{"message":"OK","code":200}':
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def myspace(email, client, out):
    name = "myspace"
    domain = "myspace.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'Origin': 'https://myspace.com', 'DNT': '1', 'Connection': 'keep-alive', 'Referer': 'https://myspace.com/signup/email'}
    try:
        r = await client.get("https://myspace.com/signup/email", headers=headers, timeout=2)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    try:
        headers['Hash'] = r.text.split('<input name="csrf" type="hidden" value="')[1].split('"')[0]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    headers['X-Requested-With'] = 'XMLHttpRequest'
    data = {'email': email}
    try:
        response = await client.post('https://myspace.com/ajax/account/validateemail', headers=headers, data=data)
        if "This email address was already used to create an account." in response.text:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def fanpop(email, client, out):
    name = "fanpop"
    domain = "fanpop.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'text/html, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://www.fanpop.com', 'Connection': 'keep-alive', 'Referer': 'https://www.fanpop.com/register'}
    data = {'type': 'register', 'user[name]': '', 'user[password]': '', 'user[email]': email, 'agreement': '', 'PersistentCookie': 'PersistentCookie', 'redirect_url': 'https://www.fanpop.com/', 'submissiontype': 'register'}
    response = await client.post('https://www.fanpop.com/login/superlogin', headers=headers, data=data)
    if "already registered" in response.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def spotify(email, client, out):
    name = "spotify"
    domain = "spotify.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'DNT': '1', 'Connection': 'keep-alive'}
    params = {'validate': '1', 'email': email}
    try:
        req = await client.get('https://spclient.wg.spotify.com/signup/public/v1/account', headers=headers, params=params)
        if req.json()["status"] == 1:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif req.json()["status"] == 20:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": None, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": None, "emailrecovery": None, "phoneNumber": None, "others": None})

async def tunefind(email, client, out):
    name = "tunefind"
    domain = "tunefind.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Referer': 'https://www.tunefind.com/', 'x-tf-react': 'true', 'Origin': 'https://www.tunefind.com', 'Connection': 'keep-alive', 'Content-Type': 'multipart/form-data; boundary=---------------------------'}
    r = await client.get("https://www.tunefind.com/user/join", headers=headers)
    try:
        crsf_token = r.text.split('"csrf-token" content="')[1].split('"')[0]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = '$-----------------------------\r\nContent-Disposition: form-data; name="username"\r\n\r\n\r\n-----------------------------\r\nContent-Disposition: form-data; name="email"\r\n\r\n' + str(email) + '\r\n-----------------------------\r\nContent-Disposition: form-data; name="password"\r\n\r\n\r\n-------------------------------\r\n'
    response = await client.post('https://www.tunefind.com/user/join', headers=headers, data=data)
    if "email" in response.json()["errors"].keys():
        if "Someone is already registered with that email address" in str(response.json()["errors"]["email"]):
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def soundcloud(email, client, out):
    name = "soundcloud"
    domain = "soundcloud.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': random.choice(ua["browsers"]["iOS"])}
    getAuth = await client.get('https://soundcloud.com/octobersveryown', headers=headers)
    script = BeautifulSoup(getAuth.text, 'html.parser').find_all('script')[4]
    clientId = json.loads(script.contents[0])["runtimeConfig"]["clientId"]
    linkMail = email.replace('@', '%40')
    API = await client.get(f'https://api-auth.soundcloud.com/web-auth/identifier?q={linkMail}&client_id={clientId}', headers=headers)
    Json = json.loads(API.text)
    if Json['status'] == 'available' or 'in_use':
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True if Json['status'] == 'in_use' else False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def duolingo(email, client, out):
    name = "duolingo"
    domain = "duolingo.com"
    method = "other"
    frequent_rate_limit = False
    headers = {'authority': 'www.duolingo.com', 'method': 'GET', 'path': '/2017-06-30/users?email=' + email, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate, br, zstd', 'Accept-Language': 'en-US,en;q=0.8', 'User-Agent': random.choice(ua["browsers"]["firefox"])}
    try:
        req = await client.get("https://www.duolingo.com/2017-06-30/users?email=" + email)
        if req.json()["users"]:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def diigo(email, client, out):
    name = "diigo"
    domain = "diigo.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'DNT': '1', 'Connection': 'keep-alive', 'Referer': 'https://www.diigo.com/sign-up?plan=free', 'X-Requested-With': 'XMLHttpRequest'}
    params = {'email': email}
    try:
        response = await client.get('https://www.diigo.com/user_mana2/check_email', headers=headers, params=params)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    if response.status_code == 200:
        if response.text == "0":
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def quora(email, client, out):
    name = "quora"
    domain = "quora.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://fr.quora.com', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    try:
        r = await client.get("https://fr.quora.com", headers=headers)
        revision = r.text.split('revision": "')[1].split('"')[0]
        formkey = r.text.split('formkey": "')[1].split('"')[0]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    data = {'json': '{"args":[],"kwargs":{"value":"' + str(email) + '"}}', 'formkey': str(formkey), '__hmac': '0XXXXXXxxXDxX', '__method': 'validate'}
    response = await client.post('https://fr.quora.com/webnode2/server_call_POST', headers=headers, data=data)
    try:
        if 'Un compte a' in response.text:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def google(email, client, out):
    name = "google"
    domain = "google.com"
    method = "register"
    frequent_rate_limit = False
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en,en-US;q=0.5', 'X-Same-Domain': '1', 'Google-Accounts-XSRF': '1', 'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Origin': 'https://accounts.google.com', 'DNT': '1', 'Connection': 'keep-alive', 'Referer': 'https://accounts.google.com/signup/v2/webcreateaccount?continue=https%3A%2F%2Faccounts.google.com%2F&gmb=exp&biz=false&flowName=GlifWebSignIn&flowEntry=SignUp', 'TE': 'Trailers'}
    req = await client.get("https://accounts.google.com/signup/v2/webcreateaccount?continue=https%3A%2F%2Faccounts.google.com%2FManageAccount%3Fnc%3D1&gmb=exp&biz=false&flowName=GlifWebSignIn&flowEntry=SignUp", headers=headers)
    try:
        freq = req.text.split('quot;,null,null,null,&quot;')[1].split('&quot')[0]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    params = {'hl': 'fr', 'rt': 'j'}
    data = {'continue': 'https://accounts.google.com/', 'dsh': '', 'hl': 'fr', 'f.req': '["' + freq + '","","","' + email + '",false]', 'azt': '', 'cookiesDisabled': 'false', 'deviceinfo': '[null,null,null,[],null,"FR",null,null,[],"GlifWebSignIn",null,[null,null,[],null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,[],null,null,null,[],[]],null,null,null,null,0,null,false]', 'gmscoreversion': 'unined', '': ''}
    response = await client.post('https://accounts.google.com/_/signup/webusernameavailability', headers=headers, params=params, data=data)
    if '"gf.wuar",2' in response.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
    elif '"gf.wuar",1' in response.text or "EmailInvalid" in response.text:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def yahoo(email, client, out):
    name = "yahoo"
    domain = "yahoo.com"
    method = "login"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'https://login.yahoo.com', 'DNT': '1', 'Connection': 'keep-alive'}
    req = await client.get("https://login.yahoo.com", headers=headers)
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'bucket': 'mbr-fe-merge-manage-account', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://login.yahoo.com', 'DNT': '1', 'Connection': 'keep-alive'}
    params = {'.src': 'fpctx', '.intl': 'ca', '.lang': 'en-CA', '.done': 'https://ca.yahoo.com'}
    try:
        data = {'acrumb': req.text.split('<input type="hidden" name="acrumb" value="')[1].split('"')[0], 'sessionIndex': req.text.split('<input type="hidden" name="sessionIndex" value="')[1].split('"')[0], 'username': email, 'passwd': '', 'signin': 'Next', 'persistent': 'y'}
        response = await client.post('https://login.yahoo.com/', headers=headers, params=params, data=data)
        response = response.json()
        if "error" in response.keys():
            if not response["error"]:
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
            else:
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif "render" in response.keys():
            if response["render"]["error"] == "messages.ERROR_INVALID_USERNAME":
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
            else:
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif "location" in response.keys():
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def protonmail(email, client, out):
    name = "protonmail"
    domain = "protonmail.ch"
    method = "other"
    frequent_rate_limit = False
    try:
        response = await client.get('https://api.protonmail.ch/pks/lookup?op=index&search=' + email)
        if "info:1:0" in response.text:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        elif "info:1:1" in response.text:
            regexPattern1 = "2048:(.*)::"
            regexPattern2 = "4096:(.*)::"
            regexPattern3 = "22::(.*)::"
            try:
                timestamp = int(re.search(regexPattern1, response.text).group(1))
            except Exception:
                try:
                    timestamp = int(re.search(regexPattern2, response.text).group(1))
                except Exception:
                    timestamp = int(re.search(regexPattern3, response.text).group(1))
            dtObject = datetime.fromtimestamp(timestamp)
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": {"Date, time of the creation": str(dtObject)}})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def mail_ru(email, client, out):
    name = "mail_ru"
    domain = "mail.ru"
    method = "password recovery"
    frequent_rate_limit = False
    headers = {'authority': 'account.mail.ru', 'accept': 'application/json, text/javascript, */*; q=0.01', 'x-requested-with': 'XMLHttpRequest', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'origin': 'https://account.mail.ru', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'https://account.mail.ru/recovery?email={email}', 'user-agent': random.choice(ua["browsers"]["chrome"]), 'accept-language': 'ru'}
    data = 'email={email}&htmlencoded=false'.replace('@', '%40')
    try:
        response = await client.post('https://account.mail.ru/api/v1/user/password/restore', headers=headers, data=data)
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return
    if response.status_code == 200:
        try:
            reqd = response.json()
            if reqd['status'] == 200:
                phones = ', '.join(reqd['body'].get('phones', [])) or None
                emails = ', '.join(reqd['body'].get('emails', [])) or None
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": emails, "phoneNumber": phones, "others": None})
            else:
                out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        except Exception:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def laposte(email, client, out):
    name = "laposte"
    domain = "laposte.fr"
    method = "register"
    frequent_rate_limit = False
    headers = {'Origin': 'https://www.laposte.fr', 'User-Agent': random.choice(ua["browsers"]["chrome"]), 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Referer': 'https://www.laposte.fr/authentification', 'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'}
    data = {'email': email, 'customerId': '', 'tunnelSteps': ''}
    try:
        response = await client.post('https://www.laposte.fr/authentification', headers=headers, data=data)
        post_soup = BeautifulSoup(response.content, 'html.parser')
        l = post_soup.find_all('span', id="wrongEmail")
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": l != [], "emailrecovery": None, "phoneNumber": None, "others": None})
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def venmo(email, client, out):
    name = "venmo"
    domain = "venmo.com"
    method = "register"
    frequent_rate_limit = True
    headers = {'User-Agent': random.choice(ua["browsers"]["firefox"]), 'Accept': 'application/json', 'Accept-Language': 'en,en-US;q=0.5', 'Referer': 'https://venmo.com/', 'Content-Type': 'application/json', 'Origin': 'https://venmo.com', 'DNT': '1', 'Connection': 'keep-alive', 'TE': 'Trailers'}
    s = await client.get("https://venmo.com/signup/email", headers=headers)
    try:
        headers["device-id"] = s.cookies["v_id"]
    except Exception:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
        return None
    data = '{"last_name":"e","first_name":"z","email":"' + email + '","password":"","phone":"1","client_id":10}'
    response = await client.post('https://venmo.com/api/v5/users', headers=headers, data=data)
    if "Not acceptable" not in response.text:
        if "That email is already registered in our system." in response.text:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None})
        else:
            out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})
    else:
        out.append({"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit, "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def maincore():
    parser = ArgumentParser(description=f"Axomic OSINT v{VERSION}")
    parser.add_argument("email", nargs='+', metavar='EMAIL', help="Target Email")
    parser.add_argument("--only-used", default=False, required=False, action="store_true", dest="onlyused", help="Displays only the sites used by the target email address.")
    parser.add_argument("--no-color", default=False, required=False, action="store_true", dest="nocolor", help="Don't color terminal output")
    parser.add_argument("--no-clear", default=False, required=False, action="store_true", dest="noclear", help="Do not clear the terminal to display the results")
    parser.add_argument("-NP", "--no-password-recovery", default=False, required=False, action="store_true", dest="nopasswordrecovery", help="Do not try password recovery on the websites")
    parser.add_argument("-C", "--csv", default=False, required=False, action="store_true", dest="csvoutput", help="Create a CSV with the results")
    parser.add_argument("-T", "--timeout", type=int, default=10, required=False, dest="timeout", help="Set max timeout value (default 10)")
    check_update()
    args = parser.parse_args()
    credit()
    email = args.email[0]
    if not is_email(email):
        exit("[-] Please enter a target email !\nExample: axomicosint email@example.com")
    modules = import_submodules("holehe.modules")
    websites = get_functions(modules, args)
    timeout = args.timeout
    start_time = time.time()
    client = httpx.AsyncClient(timeout=timeout)
    out = []
    instrument = TrioProgress(len(websites))
    trio.lowlevel.add_instrument(instrument)
    async with trio.open_nursery() as nursery:
        for website in websites:
            nursery.start_soon(launch_module, website, email, client, out)
    trio.lowlevel.remove_instrument(instrument)
    out = sorted(out, key=lambda i: i['name'])
    await client.aclose()
    print_result(out, args, email, start_time, websites)
    credit()
    export_csv(out, args, email)

def main():
    trio.run(maincore)

if __name__ == "__main__":
    main()
