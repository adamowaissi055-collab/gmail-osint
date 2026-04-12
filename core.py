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
        
        if resp.status_code >= 500:
            return {"status": "error", "message": f"Server error HTTP {resp.status_code}"}
        
        if "existsstatus" in module:
            if resp.status_code == module["existsstatus"]:
                return {"status": "success", "exists": True}
            if resp.status_code == module.get("notexistsstatus", 404):
                return {"status": "success", "exists": False}
            return {"status": "error", "message": f"Unexpected status code {resp.status_code}"}
        
        if "existsjsonpath" in module:
            try:
                data = resp.json()
            except:
                return {"status": "error", "message": "Invalid JSON response"}
            keys = module["existsjsonpath"].split(".")
            for key in keys:
                if not isinstance(data, dict):
                    return {"status": "error", "message": "JSON path invalid"}
                data = data.get(key, {})
            if data == module["existsjsonvalue"]:
                return {"status": "success", "exists": True}
            return {"status": "success", "exists": False}
        
        if "existsTextInResponse" in module:
            if module["existsTextInResponse"] in resp.text:
                return {"status": "success", "exists": True}
            return {"status": "success", "exists": False}
        
        if "notexistsTextInResponse" in module:
            if module["notexistsTextInResponse"] not in resp.text:
                return {"status": "success", "exists": True}
            return {"status": "success", "exists": False}
        
        return {"status": "error", "message": "No detection method configured"}
    
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection failed"}
    except requests.exceptions.TooManyRedirects:
        return {"status": "error", "message": "Too many redirects"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}

def main(email):
    modules = loadmodules()
    results = []
    
    for mod in modules:
        result = checkemail(email, mod)
        if result["status"] == "error":
            print(f"ERROR - {mod['name']}: {result['message']}")
        elif result["exists"]:
            print(f"email used - {mod['name']}")
            results.append(mod["name"])
    
    if results:
        print(f"\nTotal found: {len(results)} - {', '.join(results)}")
    else:
        print("\nNo emails found in use")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python core.py email@example.com")
        sys.exit(1)
    main(sys.argv[1])
