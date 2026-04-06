
import builtins
import random
import hashlib
import string

builtins.random = random
builtins.hashlib = hashlib
builtins.string = string
import os
import sys
import trio
import httpx
import time
from datetime import datetime
import csv
import importlib.util
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

def load_modules():
    modules = []
    folder = os.path.join(os.path.dirname(__file__), "modules")
    for file in os.listdir(folder):
        if file.endswith(".py") and file != "__init__.py":
            path = os.path.join(folder, file)
            name = file[:-3]
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, name):
                modules.append(getattr(mod, name))
    return modules

def normalize_entry(r):
    keys = ["domain", "rateLimit", "error", "errorReason", "exists", "emailrecovery", "phoneNumber", "others"]
    normalized = {k: r.get(k, None) for k in keys}
    if normalized["error"] and not normalized["errorReason"]:
        normalized["errorReason"] = "Unknown"
    return normalized

def print_results(data, email, start_time, websites):
    print("\n")
    normalized = [normalize_entry(r) for r in data]

    for r in normalized:
        if r["error"]:
            print(f"{r['domain']} [ERROR: {r['errorReason']}]\n")
        elif r["exists"]:
            print(f"{r['domain']} [USED]\n")
        else:
            print(f"{r['domain']} [NOT USED]\n")

    print(f"Checked {len(websites)} sites in {round(time.time()-start_time,2)}s\n")

def export_csv(data, email):
    ts = int(datetime.timestamp(datetime.now()))
    fname = f"osint_{ts}_{email}_results.csv"
    if not data:
        with open(fname, "w", newline="", encoding="utf8") as f:
            f.write("No results found\n")
        return
    normalized = [normalize_entry(r) for r in data]
    with open(fname, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=normalized[0].keys())
        w.writeheader()
        w.writerows(normalized)

async def launch(module, email, client, out):
    try:
        await module(email, client, out)
    except Exception as e:
        name = str(module).split("<function ")[1].split(" ")[0]
        out.append({"domain": name, "rateLimit": False, "error": True, "errorReason": str(e), "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def main_core(email):
    websites = load_modules()
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
