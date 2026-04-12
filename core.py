import json
import sys
import requests

def loadmodules():
    with open("modules.json", "r") as f:
        return json.load(f)

def checkemail(email, module):
    method = module.get("method", "GET").upper()
    url = module["url"]
    headers = module.get("headers", {})
    paramname = module.get("param", "email")
    try:
        if method == "POST":
            resp = requests.post(url, headers=headers, data={paramname: email}, timeout=10)
        else:
            resp = requests.get(url, headers=headers, params={paramname: email}, timeout=10)
        if "existsstatus" in module:
            if resp.status_code == module["existsstatus"]:
                return True
            if resp.status_code == module.get("notexistsstatus", 404):
                return False
        if "existsjsonpath" in module:
            data = resp.json()
            keys = module["existsjsonpath"].split(".")
            for key in keys:
                data = data.get(key, {})
            return data == module["existsjsonvalue"]
        if "existsTextInResponse" in module:
            return module["existsTextInResponse"] in resp.text
        if "notexistsTextInResponse" in module:
            return module["notexistsTextInResponse"] not in resp.text
        return None
    except:
        return None

def main(email):
    modules = loadmodules()
    for mod in modules:
        used = checkemail(email, mod)
        if used:
            print(f"email used - {mod['name']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python core.py email@example.com")
        sys.exit(1)
    main(sys.argv[1])
