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
from bs4 import BeautifulSoup
builtins.BeautifulSoup = BeautifulSoup

from axomosint.localuseragent import ua
from axomosint.instruments import TrioProgress

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

async def run_module(module_func, email, results):
    try:
        client = httpx.AsyncClient(timeout=15)
        out = []
        await module_func(email, client, out)
        await client.aclose()
        if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
            entry = out[0]
            if entry.get("exists"):
                results.append({"name": entry.get("domain") or module_func.__name__, "status": "[USED]"})
            else:
                results.append({"name": entry.get("domain") or module_func.__name__, "status": "[NOT USED]"})
        else:
            results.append({"name": module_func.__name__, "status": "[NOT USED]"})
    except Exception as e:
        results.append({"name": module_func.__name__, "status": f"[ERROR: {e}]"})
    await trio.sleep(0.01)

async def main_core(email):
    modules = load_modules()
    results = []
    inst = TrioProgress(len(modules))
    trio.lowlevel.add_instrument(inst)
    async with trio.open_nursery() as nursery:
        for mod in modules:
            nursery.start_soon(run_module, mod, email, results)
    trio.lowlevel.remove_instrument(inst)
    for r in results:
        print()
        print(f"{r['name']} {r['status']}")
    print()
    filename = f"osint_{int(time.time())}_{email}_results.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "status"])
        for r in results:
            writer.writerow([r["name"], r["status"]])

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    email = sys.argv[1]
    if not is_email(email):
        sys.exit(1)
    trio.run(main_core, email)

if __name__ == "__main__":
    main()
