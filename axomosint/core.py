
import os
import sys
import subprocess
import requests
import trio
import httpx
import time
from datetime import datetime
import csv
import importlib
import pkgutil
import re

from axomosint.localuseragent import ua
from axomosint.instruments import TrioProgress

try:
    import cookielib
except:
    import http.cookiejar as cookielib

EMAIL_FORMAT = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def is_email(email: str) -> bool:
    return bool(re.fullmatch(EMAIL_FORMAT, email))

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
    for m in modules:
        if len(m.split(".")) > 3:
            mod = modules[m]
            site = m.split(".")[-1]
            websites.append(mod.__dict__[site])
    return websites

def normalize_entry(r):
    keys = ["domain", "rateLimit", "error", "exists", "emailrecovery", "phoneNumber", "others"]
    return {k: r.get(k, None) for k in keys}

def print_results(data, email, start_time, websites):
    print("\n"*3)
    normalized = [normalize_entry(r) for r in data]
    for r in normalized:
        if not r["rateLimit"] and not r["error"] and r["exists"]:
            extras = ""
            if r["emailrecovery"]:
                extras += " " + r["emailrecovery"]
            if r["phoneNumber"]:
                extras += " / " + r["phoneNumber"]
            print(f"[used] {r['domain']}{extras}")
    print(f"\nChecked {len(websites)} sites in {round(time.time()-start_time,2)}s")

def export_csv(data, email):
    ts = int(datetime.timestamp(datetime.now()))
    fname = f"osint_{ts}_{email}_results.csv"
    if not data:
        with open(fname, "w", newline="", encoding="utf8") as f:
            f.write("No results found\n")
        print("Results exported to", fname)
        return
    normalized = [normalize_entry(r) for r in data]
    with open(fname, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=normalized[0].keys())
        w.writeheader()
        w.writerows(normalized)
    print("Results exported to", fname)

async def launch(module, email, client, out):
    try:
        await module(email, client, out)
    except:
        name = str(module).split("<function ")[1].split(" ")[0]
        out.append({"name": name, "domain": name, "rateLimit": False, "error": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def main_core(email):
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
    if len(sys.argv) < 2:
        exit("Usage: python3 core.py email@example.com")
    email = sys.argv[1]
    if not is_email(email):
        exit("Invalid email!")
    trio.run(main_core, email)

if __name__ == "__main__":
    main()
