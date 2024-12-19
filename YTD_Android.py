import os
import sys
import json
import linecache
import logging
import platform
from termcolor import colored

# Constants
JSON_PATH = os.getenv('JSON_PATH', os.path.expanduser("~/default.json"))
TEMP_LOC = os.getenv('TEMP_LOC', os.path.expanduser("~/temp.txt"))
GEN_PATH = os.getenv('GEN_PATH', os.path.expanduser("~/Termux_Downloader/"))
HISTORY_PATH = os.path.join(GEN_PATH, "history.txt")

# Check if running in Termux and set GEN1_PATH and HISTORY1_PATH
if os.path.exists('/data/data/com.termux/files'):
    GEN1_PATH = os.getenv('GEN1_PATH', os.path.expanduser("~/"))
    HISTORY1_PATH = os.path.join(GEN1_PATH, "history.txt")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def print_version_info():
    """Print version information from the script's first three lines"""
    version = linecache.getline(sys.argv[0], 1).replace("#", "").strip()
    engine = linecache.getline(sys.argv[0], 2).replace("#", "").strip()
    build = linecache.getline(sys.argv[0], 3).replace("#", "").strip()
    logging.info(f"Version: {version}")
    logging.info(f"Engine: {engine}")
    logging.info(f"Build: {build}")
    linecache.clearcache()

def load_or_create_json_config():
    """Load or create the JSON configuration file"""
    if not os.path.isfile(JSON_PATH):
        json_data = {
            "default": [{"code": "", "codec": "", "last_upgrade": "", "history_backup": ""}],
            "1": [{"height": "2160", "res": "4k"}],
            "2": [{"height": "1440", "res": "2k"}],
            "3": [{"height": "1080", "res": "1080p"}],
            "4": [{"height": "720", "res": "720p"}],
            "5": [{"height": "480", "res": "480p"}],
            "6": [{"height": "360", "res": "360p"}],
            "7": [{"height": "240", "res": "240p"}],
            "8": [{"height": "144", "res": "144p"}]
        }
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        with open(JSON_PATH, "w") as file:
            json.dump(json_data, file, indent=4)
        logging.info("JSON config created.")

def ensure_dependencies():
    """Ensure required dependencies are installed"""
    try:
        import ffmpeg
    except ModuleNotFoundError:
        os.system('pip install ffmpeg')
        logging.info("Installed ffmpeg.")
    try:
        import yt_dlp
    except ModuleNotFoundError:
        os.system('pip install --no-deps -U yt_dlp')
        logging.info("Installed yt_dlp.")

def sync_with_drive():
    """Sync history with Google Drive using rclone"""
    loc_path = os.path.dirname(sys.argv[0])
    history_file = HISTORY_PATH
    config = os.path.join(loc_path, "rclone.conf")
    rc_temp = f"rclone --config={config}"

    if not os.path.isfile(config):
        os.system(f"{rc_temp} config")
        logging.info("Configured rclone.")

    with open(config, 'r') as config_file:
        remote = config_file.readline().strip().replace('[', '').replace(']', '') + ":"

    if not os.path.isfile(history_file):
        os.system(f"{rc_temp} copy {remote}/history.txt {GEN_PATH}")
        logging.info("Restored history file from remote.")

    logging.info("Syncing with cloud...")
    os.system(f"{rc_temp} --verbose copy --update {history_file} {remote}")

def update_history(title, site):
    """Update download history"""
    title = title.replace('"', "`").replace("'", "`")
    history_entry = {
        "SNo": str(len(open(HISTORY_PATH, 'r').readlines()) + 1),
        "Name": title[:50],
        "URL": link,
        "Site": site
    }
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    # Create history file if it doesn't exist
    if not os.path.isfile(HISTORY_PATH):
        with open(HISTORY_PATH, 'w') as file:
            file.write("")
    with open(HISTORY_PATH, 'a') as file:
        file.write(json.dumps(history_entry) + "\n")

    # Update HISTORY1_PATH if running in Termux
    if os.path.exists('/data/data/com.termux/files'):
        os.makedirs(os.path.dirname(HISTORY1_PATH), exist_ok=True)
        if not os.path.isfile(HISTORY1_PATH):
            with open(HISTORY1_PATH, 'w') as file:
                file.write("")
        with open(HISTORY1_PATH, 'a') as file:
            file.write(json.dumps(history_entry) + "\n")

    with open(JSON_PATH, "r") as file:
        data = json.load(file)
    if data["default"][0]["history_backup"] == "y":
        sync_with_drive()

    if platform.system() == 'Linux' and 'com.termux' not in os.getenv('PREFIX', ''):
        os.remove(TEMP_LOC)
    logging.info("History updated and temp file removed.")
    sys.exit()

def download_content(opt, site):
    """Download content using yt_dlp"""
    import yt_dlp
    try:
        with yt_dlp.YoutubeDL(opt) as yt:
            info = yt.extract_info(link, download=True)
            title = info.get('title', None)
            update_history(title, site)
    except Exception as e:
        logging.error(f"Error downloading content: {e}")

def download_video(mode):
    """Download video based on the mode"""
    if "playlist" in link:
        path = os.path.join(GEN_PATH, 'Youtube/%(playlist)s/%(title)s.%(ext)s')
        thumb = True
    else:
        path = os.path.join(GEN_PATH, 'Youtube/%(title)s.%(ext)s')
        thumb = True

    with open(JSON_PATH, "r") as file:
        data = json.load(file)

    if mode == "Youtube":
        logging.info("Downloading video from YouTube.")
        code = get_or_update_resolution_code(data)
        j = data[code][0]["height"]
        k = data[code][0]["res"]

        logging.info(f'Note: The video will download in {k} Resolution if YouTube has such resolution. If not, it will download the best available resolution.')
        format = f'bestvideo[height<={j}]+bestaudio[ext=m4a]/best[height<={j}]/best[ext=m4a]'
    elif mode == "best":
        logging.info("Downloading best one from YouTube.")
        format = 'best'
    elif mode == "advanced":
        logging.info("Downloading from YouTube - Advanced mode.")
        os.system(f"yt-dlp -F {link}")
        vid = input('Video id: \n')
        aid = input('Audio id: \n')
        format = f"{vid} + {aid}"
    else:
        link_distributor()

    choice = input("Do you need subtitle? If yes, type 'y' or skip: ").lower() == "y"

    opt = {
        'external_downloader': 'aria2c',
        'outtmpl': path,
        'writesubtitles': choice,
        'writeautomaticsub': choice,
        'merge_output_format': 'mp4',
        'writethumbnail': thumb,
        'format': format,
        'postprocessors': [
            {'key': 'FFmpegEmbedSubtitle', 'already_have_subtitle': False},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
            {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}
        ]
    }
    download_content(opt, site=mode)

def get_or_update_resolution_code(data):
    """Get or update the resolution code in the JSON configuration"""
    if data["default"][0]["code"] == "":
        print('Enter the respective code for Required Resolution:')
        print('[code] - [Resolution]')
        print('1 - 4k')
        print('2 - 2k')
        print('3 - 1080p')
        print('4 - 720p')
        print("5 - 480p")
        print('6 - 360p')
        print('7 - 240p')
        print('8 - 144p')

        code = input('Resolution Code: ')
        data["default"][0]["code"] = code

        with open(JSON_PATH, "w") as file:
            json.dump(data, file)
    else:
        code = data["default"][0]["code"]
        k = data[code][0]["res"]
        choice = input(f"Default resolution is {k}. If you want to download in different resolution type (y) or skip: ").lower()
        if choice == "y":
            print('Enter the respective code for Required Resolution:')
            print('[code] - [Resolution]')
            print('1 - 4k')
            print('2 - 2k')
            print('3 - 1080p')
            print('4 - 720p')
            print("5 - 480p")
            print('6 - 360p')
            print('7 - 240p')
            print('8 - 144p')

            code = input('Resolution Code: ')
            data["default"][0]["code"] = code

            with open(JSON_PATH, "w") as file:
                json.dump(data, file)

    return code

def download_audio(dir_name):
    """Download audio based on the directory name"""
    logging.info(f"Downloading songs from {dir_name}.")
    with open(JSON_PATH, "r") as file:
        data = json.load(file)

    if data["default"][0]["codec"] == "":
        codec = input('Enter the Format of audio (mp3, aac, m4a, flac....): ')
        data["default"][0]["codec"] = codec

        with open(JSON_PATH, "w") as file:
            json.dump(data, file)
    else:
        codec = data["default"][0]["codec"]
        choice = input(f"Default audio codec is {codec}. If you need to download in different codec type (y) or else skip: ").lower()
        if choice == "y":
            codec = input('Enter the Format of audio (mp3, aac, m4a, flac....): ')
            data["default"][0]["codec"] = codec

            with open(JSON_PATH, "w") as file:
                json.dump(data, file)

    path = os.path.join(GEN_PATH, dir_name)
    os.makedirs(path, exist_ok=True)

    if "playlist" in link:
        op_path = os.path.join(path, '%(playlist)s/%(title)s.%(ext)s')
    else:
        op_path = os.path.join(path, '%(title)s.%(ext)s')

    opt = {
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'ignoreerrors': True,
        'outtmpl': op_path,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': codec},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
            {"key": 'EmbedThumbnail', 'already_have_thumbnail': False}
        ]
    }

    site = "Youtube Music" if dir_name == "YTmusic" else "Youtube"
    download_content(opt, site=site)

def download_from_others():
    """Download content from other websites"""
    if "www" in link:
        dir_name = link.split("www.")[1].split(".")[0].capitalize()
    else:
        dir_name = link.split("://")[1].split(".")[0].capitalize()

    logging.info(f"Downloading from {colored(dir_name, 'magenta')}.")
    path = os.path.join(GEN_PATH, dir_name)
    os.makedirs(path, exist_ok=True)

    opt = {
        'outtmpl': os.path.join(path, "%(title).50s.%(ext)s"),
        'external_downloader': 'aria2c'
    }

    try:
        download_content(opt, site=dir_name)
    except Exception as e:
        logging.error(f"Error downloading from {dir_name}: {e}")
        if platform.system() == 'Linux' and 'com.termux' not in os.getenv('PREFIX', ''):
            os.rmdir(path)

def download_from_ftp_or_torrent():
    """Download content from FTP or torrent links"""
    if "magnet" in link:
        logging.info("Downloading Torrent file from Magnet link.")
        path = os.path.join(GEN_PATH, "Torrents")
    else:
        logging.info("Downloading from FTP link.")
        path = os.path.join(GEN_PATH, "Downloads")
    os.makedirs(path, exist_ok=True)
    os.system(f"aria2c -d '{path}' '{link}' --file-allocation=none")

def download_from_drive():
    """Download content from Google Drive"""
    file_id = link.replace("https://drive.google.com/file/d/", "").split("/")[0]
    path = os.path.join(GEN_PATH, "Gdrive")
    os.makedirs(path, exist_ok=True)
    os.system(f"gdown -O '{path}' --id '{file_id}'")

def link_distributor():
    """Distribute links to appropriate download functions"""
    if "drive" in link:
        download_from_drive()
    elif "magnet" in link:
        download_from_ftp_or_torrent()
    elif "music" in link:
        download_audio(dir_name="YTmusic")
    elif "youtube" in link or "youtu.be" in link:
        path = os.path.join(GEN_PATH, 'Youtube')
        os.makedirs(path, exist_ok=True)

        print('Enter \n*(v) for Video \n*(a) for audio \n*(m) for advanced \n*(b) for best')
        T = input('v or a or m or b: ').strip().lower()
        if T == "v":
            download_video(mode="Youtube")
        elif T == "m":
            download_video(mode="advanced")
        elif T == "a":
            logging.info("Downloading Audio track from YouTube.")
            download_audio(dir_name="Youtube")
        elif T == "b":
            download_video(mode="best")
        else:
            link_distributor()
    else:
        try:
            download_from_others()
        except Exception:
            download_from_ftp_or_torrent()

def master_directory():
    """Create master directory and initiate link distribution"""
    os.makedirs(GEN_PATH, exist_ok=True)

    def clean_empty_directories():
        """Remove empty directories"""
        empty_dirs = [root for root, dirs, files in os.walk(GEN_PATH) if not dirs and not files]
        for empty_dir in empty_dirs:
            if platform.system() == 'Linux' and 'com.termux' not in os.getenv('PREFIX', ''):
                os.rmdir(empty_dir)

    clean_empty_directories()
    link_distributor()

if __name__ == "__main__":
    # Print version info
    print_version_info()

    # Ensure JSON config exists
    load_or_create_json_config()

    # Ensure necessary dependencies are installed
    ensure_dependencies()

    # Extract link from arguments
    if len(sys.argv) > 1:
        link = sys.argv[1]
    else:
        logging.error("No link provided.")
        sys.exit(1)

    # Handle temp file operations
    if os.path.isfile(TEMP_LOC):
        os.remove(TEMP_LOC)

    with open(TEMP_LOC, "w") as temp_file:
        temp_file.write(link)

    # Ensure history file exists
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    if not os.path.isfile(HISTORY_PATH):
        with open(HISTORY_PATH, 'w') as file:
            file.write("")

    # Ensure HISTORY1_PATH exists if running in Termux
    if os.path.exists('/data/data/com.termux/files/usr'):
        os.makedirs(os.path.dirname(HISTORY1_PATH), exist_ok=True)
        if not os.path.isfile(HISTORY1_PATH):
            with open(HISTORY1_PATH, 'w') as file:
                file.write("")

    # Start the master directory process
    master_directory()

    # Delete TEMP_LOC if running on Linux but not Termux
    if os.path.isfile(TEMP_LOC) and platform.system() == 'Linux' and 'com.termux' not in os.getenv('PREFIX', ''):
        os.remove(TEMP_LOC)
