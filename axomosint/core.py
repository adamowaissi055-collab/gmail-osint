
import os
import sys
import subprocess
import requests
import trio
import httpx
from datetime import datetime
import csv
import importlib.util
import re
import time

from axomosint.localuseragent import ua
from axomosint.instruments import TrioProgress

try:
    import cookielib
except:
    import http.cookiejar as cookielib

EMAIL_FORMAT = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
REMOTE_RAW = "https://raw.githubusercontent.com/adamowaissi055-collab/gmail-osint/main/axomosint/core.py"

def auto_update():
    try:
        r = requests.get(REMOTE_RAW, timeout=8).text
        local = open(__file__, "r").read()
        if r != local:
            print("[*] New version found. Updating...")
            open(__file__, "w").write(r)
            print("[*] Updated! Restarting...")
            subprocess.Popen([sys.executable]+sys.argv)
            sys.exit()
    except:
        pass

def is_email(email: str) -> bool:
    return bool(re.fullmatch(EMAIL_FORMAT, email))

def import_modules_folder(folder="axomosint/modules"):
    modules = []
    for filename in os.listdir(folder):
        if filename.endswith(".py") and filename != "__init__.py":
            path = os.path.join(folder, filename)
            name = filename[:-3]
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            modules.append(mod)
    return modules

def get_functions(modules):
    websites = []
    for m in modules:
        if hasattr(m, m.__name__):
            websites.append(getattr(m, m.__name__))
    return websites

def print_results(data, email, start_time, websites):
    print("\n"*3)
    for r in data:
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
    if not data:
        fname = f"osint_{ts}_{email}_results.csv"
        with open(fname, "w", newline="", encoding="utf8") as f:
            f.write("No results found\n")
        print("Results exported to", fname)
        return
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
        out.append({"name": name, "domain": name, "rateLimit": False, "error": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None})

async def main_core(email):
    auto_update()
    modules = import_modules_folder()
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
