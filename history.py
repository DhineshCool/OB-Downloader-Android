import os
import json
import time
import webbrowser

# Determine the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Constants
GEN_PATH = os.path.expanduser("~/Termux_Downloader")
GEN1_PATH = SCRIPT_DIR  # Ensure GEN1_PATH is the same as the script's location
HISTORY_PATH = os.path.join(GEN_PATH, "history.txt")
TEMP_LOC = os.path.join(GEN_PATH, "temp.txt")
MAIN_SCRIPT = os.path.join(GEN1_PATH, "main.py")
FALLBACK_SCRIPT = os.path.join(GEN1_PATH, "YTD_Android.py")

def get_script_to_run():
    """Determine which script to run: main.py or YTD_Android.py"""
    if os.path.isfile(MAIN_SCRIPT):
        return MAIN_SCRIPT
    elif os.path.isfile(FALLBACK_SCRIPT):
        return FALLBACK_SCRIPT
    else:
        print(f"Error: Neither {MAIN_SCRIPT} nor {FALLBACK_SCRIPT} found.")
        exit()

def ensure_history_file():
    """Ensure the history file exists"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    # If the file does not exist, create it
    if not os.path.isfile(HISTORY_PATH):
        with open(HISTORY_PATH, 'w') as file:
            file.write("")

def history_mod():
    """Modify and interact with the download history"""
    ensure_history_file()

    start = time.time()
    histlist = []

    # Read the history file
    with open(HISTORY_PATH, 'r+') as f:
        for jsonObj in f:
            Dict = json.loads(jsonObj)
            histlist.append(Dict)

    histlist2 = str(histlist).replace("'", '"')
    histlist3 = histlist2.replace("\\", "/")
    input_dict = json.loads(histlist3)

    print("\nHistory: \n")
    for i in input_dict:
        print(i["SNo"] + ")", i["Name"] + "||", i["Site"])

    end = time.time()
    print(f"\nListing time: {(end-start)*10**3:.02f}mS\n")
    print("\nWhat to do!? \n")
    print("Select 1 to redownload from history: \nSelect 2 to revisit the site of download: \nSelect 3 to clear history: \nSkip to close this script:\n")
    choice = input("Your Choice:")

    if choice == "1":
        ask = input("\nEnter the SNo:")
        output_dict = [a for a in input_dict if a["SNo"] == ask]
        for j in output_dict:
            print(j["SNo"] + ")", j["Name"] + "||", j["Site"])
            url = j["URL"]
            print("\n")
            script_to_run = get_script_to_run()
            os.system(f'python "{script_to_run}" "{url}"')
            exit()
    elif choice == "2":
        ask = input("\nEnter the SNo:")
        output_dict = [a for a in input_dict if a["SNo"] == ask]
        for j in output_dict:
            url = j["URL"]
            webbrowser.open(url)
            exit()
    elif choice == "3":
        confirm = input("\nType YES to confirm clear history:\n")
        if confirm == "YES":
            os.remove(HISTORY_PATH)
            exit()
        else:
            exit()
    else:
        exit()

def temp_mod():
    """Modify and interact with the temporary link"""
    temp_link = open(TEMP_LOC, 'r').readlines()[0]

    print("\nPreviously failed link:")
    print("\n" + temp_link + "\n")
    print("What to do:\n 1. To Resume or attempt redownload\n 2. To open the site with link\n >Skip to exit\n")
    sel = input("Enter: ")

    if sel == "1":
        print("Attempting Redownload.....")
        script_to_run = get_script_to_run()
        os.system(f'python "{script_to_run}" "{temp_link}"')
    elif sel == "2":
        print("Opening the link in browser or supported app.....")
        webbrowser.open(temp_link)
    else:
        print("Skipping....")
        exit()

if os.path.isfile(TEMP_LOC):
    if input("\nPreviously failed to download exists..Want to resume it(type 'y') or skip to view history: ") == "y":
        temp_mod()
    else:
        history_mod()
else:
    history_mod()
