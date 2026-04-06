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

async def main_core(email):
    modules = load_modules()
    results = []
    async with trio.open_nursery() as nursery:
        for mod in modules:
            nursery.start_soon(run_module, mod, email, results)
    print_results(results, email)

async def run_module(module_func, email, results):
    try:
        output = await module_func(email, httpx.AsyncClient(), [])
        # Normalize output to dict
        if not isinstance(output, dict):
            raise ValueError(f"Module returned {type(output).__name__}, expected dict")
        exists = output.get("exists", False)
        status = "[USED]" if exists else "[NOT USED]"
        results.append({"name": module_func.__name__, "status": status})
    except Exception as e:
        results.append({"name": module_func.__name__, "status": f"[ERROR: {e}]"})
    await trio.sleep(0.01)

def print_results(results, email):
    for r in results:
        print()
        print(f"{r['name']} {r['status']}")
    print()
    export_csv(results, email)

def export_csv(results, email):
    filename = f"osint_{int(time.time())}_{email}_results.csv"
    fieldnames = ["domain", "status"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({"domain": r["name"], "status": r["status"]})

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 core.py <email>")
        sys.exit(1)
    email = sys.argv[1]
    if not is_email(email):
        print("Invalid email address")
        sys.exit(1)
    trio.run(main_core, email)

if __name__ == "__main__":
    main()
