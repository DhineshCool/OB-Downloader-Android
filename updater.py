import os
import sys
import json
import linecache
import requests
import re
from termcolor import colored, cprint
from bs4 import BeautifulSoup
from datetime import datetime, date
import time

start = time.time()

cprint("WELCOME TO OB DOWNLOADER", "cyan", "on_red", attrs=["bold"])

# Local Version and Engine Numbers
LOCAL_PATH = r"/data/data/com.termux/files/home/main.py"
l_version = linecache.getline(LOCAL_PATH, 1)
l_engine = linecache.getline(LOCAL_PATH, 2)

def fetch_version_and_engine(soup):
    """Fetch cloud version and engine numbers from the soup."""
    def fetch_version():
        vindex = soup.find("#Version")
        ver = soup[vindex + len("#Version"):vindex + len("#Version") + 9]
        c_version = "#Version" + ver + "\n"
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", ver.replace(" ", "")):
            return c_version
        else:
            cprint('\n__Update_server_timeout__', 'red')
            return l_version

    def fetch_engine():
        eindex = soup.find("#Engine")
        eng = soup[eindex + len("#Engine"):eindex + len("#Engine") + 5]
        c_engine = "#Engine" + eng + "\n"
        if re.match(r"^\d+\.\d+$", eng.replace(" ", "")):
            return c_engine
        else:
            cprint('\n__Update_server_timeout__', 'red')
            return l_engine

    return fetch_version(), fetch_engine()

try:
    url = "https://github.com/DhineshCool/OB-Downloader-Android/blob/master/YTD_Android.py"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser').text
    c_version, c_engine = fetch_version_and_engine(soup)
    print(f"\nUpdate Server: {colored('ACTIVE', 'green')}\n"
          f"Failsafe Update Verification System By-Passer: {colored('DEACTIVATED', 'green')}\n"
          f"Auto Upgrade System: {colored('ACTIVE', 'green')}\n")
except:
    print(f"\nFailsafe Update Verification System By-Passer: {colored('ACTIVATED', 'red')}\n"
          f"Update Server: {colored('BROKEN OR DOWN', 'red')}\n"
          f"Auto Upgrade System: {colored('ACTIVE', 'green')}\n")
    c_version, c_engine = l_version, l_engine

end = time.time()
print(f"\n[Ping: {(end-start)*10**3:.02f}ms]\n")

def handle_upgrade():
    """Handle upgrade process based on version and engine comparison."""
    if c_engine == l_engine:
        print("\nNo Engine upgrade available from developer...\n")
        auto_upgrade()
    else:
        print("\nNew Engine Upgrade available...\n\nUpgrading...\n")
        record_upgrade_date()
        os.system("sh refresh.sh auto")
        print("Upgraded...!\n")
        os.system(code)

def auto_upgrade():
    """Handle auto upgrade based on version and engine comparison."""
    path = "/data/data/com.termux/files/home/default.json"
    if os.path.isfile(path):
        date1 = date.today().strftime("%d/%m/%Y")
        with open(path, "r") as default_file:
            data = json.load(default_file)
            last_upgrade = data["default"][0].get("last_upgrade", "")
            if not last_upgrade:
                data["default"][0]["last_upgrade"] = date1
                last_upgrade = date1
                with open(path, "w") as default_file_w:
                    json.dump(data, default_file_w, indent=4)
            else:
                print(f"Script previously upgraded on: {colored(last_upgrade, 'blue')}")
            dates_diff = datetime.strptime(date1, "%d/%m/%Y") - datetime.strptime(last_upgrade, "%d/%m/%Y")
            if dates_diff.days > 28:
                print("\nOutdated Binaries, auto upgrading...\n")
                data["default"][0]["last_upgrade"] = date1
                with open(path, "w") as default_file_w:
                    json.dump(data, default_file_w, indent=4)
                os.system("sh refresh.sh auto")
            else:
                print("\nBinaries seem to be new. Auto upgrade skipped...\n\nChecking version update...\n")
    else:
        print("\nChecking version update...\n")

    if c_version == l_version:
        print("\nNo new update...\n")
        os.system(code)
    else:
        print("\nNew version available...\n\nUpdating...\n\n")
        open('/data/data/com.termux/files/home/noobjection.temp', 'a').close()
        os.system("sh refresh.sh auto")
        print("\nUpdated...!\n")
        os.system(code)

def record_upgrade_date():
    """Record the date of upgrade in the default.json file."""
    path = "/data/data/com.termux/files/home/default.json"
    date1 = date.today().strftime("%d/%m/%Y")
    if os.path.isfile(path):
        with open(path, "r") as default_file:
            data = json.load(default_file)
            data["default"][0]["last_upgrade"] = date1
            with open(path, "w") as default_file_w:
                json.dump(data, default_file_w, indent=4)

if __name__ == "__main__":
    code = f"python '/data/data/com.termux/files/home/main.py' '{sys.argv[1]}'"
    if sys.argv[1] != "forced":
        handle_upgrade()
    else:
        record_upgrade_date()
