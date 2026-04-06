from bs4 import BeautifulSoup
from termcolor import colored
import httpx
import trio
import os
import csv
from datetime import datetime
import time
import importlib
import pkgutil
import re
import sys
import json

from axomosint.localuseragent import ua
from axomosint.instruments import TrioProgress

try:
    import cookielib
except Exception:
    import http.cookiejar as cookielib

EMAIL_FORMAT = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
__version__ = "1.61"

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

def get_functions(modules):
    websites = []
    for module in modules:
        if len(module.split(".")) > 3:
            modu = modules[module]
            site = module.split(".")[-1]
            websites.append(modu.__dict__[site])
    return websites

def credit():
    print('our discord : https://discord.gg/FgR3MXqZy9')
    print('our youtube : https://youtube.com/@axos0022 - tiktok : https://tiktok.com/@axos002')
    print('axom')

def is_email(email: str) -> bool:
    return bool(re.fullmatch(EMAIL_FORMAT, email))

def print_result(data, email, start_time, websites):
    desc = colored("[used]","green") + "," + colored("[not used]", "magenta") + "," + colored("[error]","yellow") + "," + colored("[error]","red")
    print("\033[H\033[J")
    print("*" * (len(email) + 6))
    print("   " + email)
    print("*" * (len(email) + 6))

    for r in data:
        if not r["rateLimit"] and not r["error"] and r["exists"]:
            extras = ""
            if r["emailrecovery"]:
                extras += " " + r["emailrecovery"]
            if r["phoneNumber"]:
                extras += " / " + r["phoneNumber"]
            if r["others"] and "FullName" in r["others"]:
                extras += " / FullName " + r["others"]["FullName"]
            if r["others"] and "Date, time of the creation" in r["others"]:
                extras += " / Date, time of the creation " + r["others"]["Date, time of the creation"]
            print(colored("[used] " + r["domain"] + extras, "green"))

    print("\n" + desc)
    print(str(len(websites)) + " websites checked in " + str(round(time.time() - start_time, 2)) + " seconds")

def export_csv(data, email):
    now = datetime.now()
    ts = int(datetime.timestamp(now))
    filename = "osint_" + str(ts) + "_" + email + "_results.csv"
    with open(filename, 'w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    exit("Results exported to " + filename)

async def launch_module(module, email, client, out):
    try:
        await module(email, client, out)
    except Exception:
        nm = str(module).split('<function ')[1].split(' ')[0]
        out.append({"name": nm, "domain": nm, "rateLimit": False, "error": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def maincore(email):
    modules = import_submodules("axomosint.modules")
    websites = get_functions(modules)
    timeout = 10
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
    print_result(out, email, start_time, websites)
    credit()
    export_csv(out, email)

def main():
    if len(sys.argv) < 2:
        exit("Usage: python3 axomicosint.py email@example.com")
    email = sys.argv[1]
    if not is_email(email):
        exit("Invalid email format!")
    trio.run(maincore(email))

if __name__ == "__main__":
    main()
