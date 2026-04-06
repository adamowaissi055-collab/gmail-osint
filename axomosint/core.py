
import os
import sys
import subprocess
import requests
import trio
import httpx
from datetime import datetime
import csv
import importlib
import pkgutil
import re
import time

from axomosint.localuseragent import ua
from axomosint.instruments import TrioProgress

try:
    import cookielib
except Exception:
    import http.cookiejar as cookielib

EMAIL_FORMAT = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
REMOTE_RAW = "https://raw.githubusercontent.com/adamowaissi055-collab/gmail-osint/main/axomosint/core.py"
__version__ = "1.61"

def auto_update():
    try:
        r = requests.get(REMOTE_RAW, timeout=8).text
        local = open(__file__, "r").read()
        if r != local:
            print("[*] New version found. Updating...")
            open(__file__, "w").write(r)
            print("[*] Updated! Restarting...")
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit()
    except:
        pass

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

def print_results(data, email, start_time, websites):
    print("\n" * 3)
    for r in data:
        if not r["rateLimit"] and not r["error"] and r["exists"]:
            extras = ""
            if r.get("emailrecovery"):
                extras += " " + r["emailrecovery"]
            if r.get("phoneNumber"):
                extras += " / " + r["phoneNumber"]
            print(f"[used] {r['domain']}{extras}")
    print(f"\nChecked {len(websites)} sites in {round(time.time() - start_time,2)}s")

def export_csv(data, email):
    ts = int(datetime.timestamp(datetime.now()))
    fname = f"osint_{ts}_{email}_results.csv"
    with open(fname, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=data[0].keys())
        w.writeheader()
        w.writerows(data)
    print("Results exported to", fname)

async def launch(module, email, client, out):
    try:
        await module(email, client, out)
    except:
        name = str(module).split("<function ")[1].split(" ")[0]
        out.append({"name": name,"domain": name,"rateLimit": False,"error": True,
                    "exists": False,"emailrecovery": None,"phoneNumber": None,"others": None})

async def main_core(email):
    auto_update()
    modules = import_submodules("axomosint.modules")
    websites = get_functions(modules)
    client = httpx.AsyncClient(timeout=10)
    out = []
    inst = TrioProgress(len(websites))
    trio.lowlevel.add_instrument(inst)
    async with trio.open_nursery() as n:
        for w in websites:
            n.start_soon(launch, w, email, client, out)
    trio.lowlevel.remove_instrument(inst)
    await client.aclose()
    print_results(out, email, time.time(), websites)
    export_csv(out, email)

def main():
    email = input("Enter email to check: ").strip()
    if not is_email(email):
        exit("Invalid email!")
    trio.run(main_core, email)

if __name__ == "__main__":
    main() 
