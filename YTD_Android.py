import os
import sys
import json
import linecache
import logging
from termcolor import colored

# Constants
JSON_PATH = os.getenv('JSON_PATH', "/data/data/com.termux/files/home/default.json")
TEMP_LOC = os.getenv('TEMP_LOC', "/data/data/com.termux/files/home/temp.txt")
GEN_PATH = os.getenv('GEN_PATH', "/storage/emulated/0/")
HISTORY_PATH = os.getenv('HISTORY_PATH', "/data/data/com.termux/files/home/history.txt")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Version Info
def print_version_info():
    version = linecache.getline(sys.argv[0], 1).replace("#", "")
    engine = linecache.getline(sys.argv[0], 2).replace("#", "")
    build = linecache.getline(sys.argv[0], 3).replace("#", "")

    logging.info(version)
    logging.info(engine)
    logging.info(f"Build: {build}")
    linecache.clearcache()

# Load or Create JSON Config
def load_or_create_json_config():
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
        with open(JSON_PATH, "w") as file:
            json.dump(json_data, file, indent=4)
        logging.info("JSON config created.")

# Ensure Dependencies are Installed
def ensure_dependencies():
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

# Sync with Google Drive
def sync_with_drive():
    loc_path = os.path.dirname(sys.argv[0])
    history_file = os.path.join(loc_path, "history.txt")
    config = os.path.join(loc_path, "rclone.conf")
    rc_temp = f"rclone --config={config}"

    if not os.path.isfile(config):
        os.system(f"{rc_temp} config")
        logging.info("Configured rclone.")

    remote = open(config, 'r').readline().replace('[', '').replace(']', '').replace('\n', '') + ":"

    if not os.path.isfile(history_file):
        os.system(f"{rc_temp} copy {remote}/history.txt {loc_path}")
        logging.info("Restored history file from remote.")

    logging.info("Syncing with cloud...")
    os.system(f"{rc_temp} --verbose copy --update {history_file} {remote}")

# Update History
def update_history(title, site):
    title = title.replace('"', "`").replace("'", "`")
    history_entry = {
        "SNo": str(len(open(HISTORY_PATH, 'r').readlines()) + 1),
        "Name": title[:50],
        "URL": link,
        "Site": site
    }
    with open(HISTORY_PATH, 'a') as file:
        file.write(json.dumps(history_entry) + "\n")

    with open(JSON_PATH, "r") as file:
        data = json.load(file)
    if data["default"][0]["history_backup"] == "y":
        sync_with_drive()

    os.remove(TEMP_LOC)
    logging.info("History updated and temp file removed.")
    sys.exit()

# Download Content
def download_content(opt, site):
    import yt_dlp
    try:
        with yt_dlp.YoutubeDL(opt) as yt:
            info = yt.extract_info(link, download=True)
            title = info.get('title', None)
            update_history(title, site)
    except Exception as e:
        logging.error(f"Error downloading content: {e}")

# Download Video
def download_video(mode):
    if "playlist" in link:
        path = os.path.join(GEN_PATH, 'Termux_Downloader/Youtube/%(playlist)s/%(title)s.%(ext)s')
        thumb = True
    else:
        path = os.path.join(GEN_PATH, 'Termux_Downloader/Youtube/%(title)s.%(ext)s')
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

# Get or Update Resolution Code
def get_or_update_resolution_code(data):
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

# Download Audio
def download_audio(dir_name):
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

    path = os.path.join(GEN_PATH, f"Termux_Downloader/{dir_name}/")
    if not os.path.isdir(path):
        os.mkdir(path)

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

# Download from Other Sites
def download_from_others():
    if "www" in link:
        dir_name = link.split("www.")[1].split(".")[0].capitalize()
    else:
        dir_name = link.split("://")[1].split(".")[0].capitalize()

    logging.info(f"Downloading from {colored(dir_name, 'magenta')}.")
    path = os.path.join(GEN_PATH, f'Termux_Downloader/{dir_name}/')

    if not os.path.isdir(path):
        os.mkdir(path)

    opt = {
        'outtmpl': os.path.join(path, "%(title).50s.%(ext)s"),
        'external_downloader': 'aria2c'
    }

    try:
        download_content(opt, site=dir_name)
    except Exception as e:
        os.rmdir(path)
        logging.error(f"Error downloading from {dir_name}: {e}")

# Download from FTP or Torrent
def download_from_ftp_or_torrent():
    if "magnet" in link:
        logging.info("Downloading Torrent file from Magnet link.")
        path = os.path.join(GEN_PATH, "Termux_Downloader/Torrents/")
    else:
        logging.info("Downloading from FTP link.")
        path = os.path.join(GEN_PATH, "Termux_Downloader/Downloads/")

    if not os.path.isdir(path):
        os.mkdir(path)

    os.system(f"aria2c -d '{path}' '{link}' --file-allocation=none")

# Download from Google Drive
def download_from_drive():
    file_id = link.replace("https://drive.google.com/file/d/", "").split("/")[0]
    path = os.path.join(GEN_PATH, "Termux_Downloader/Gdrive/")
    if not os.path.isdir(path):
        os.mkdir(path)

    os.system(f"gdown -O '{path}' --id '{file_id}'")

# Link Distributor
def link_distributor():
    if "drive" in link:
        download_from_drive()
    elif "magnet" in link:
        download_from_ftp_or_torrent()
    elif "music" in link:
        download_audio(dir_name="YTmusic")
    elif "youtube" in link or "youtu.be" in link:
        path = os.path.join(GEN_PATH, 'Termux_Downloader/Youtube/')
        if not os.path.isdir(path):
            os.mkdir(path)

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

# Master Directory and Initialization
def master_directory():
    path = os.path.join(GEN_PATH, "Termux_Downloader/")
    if not os.path.isdir(path):
        os.mkdir(path)

    def clean_empty_directories():
        empty_dirs = [root for root, dirs, files in os.walk(path) if not dirs and not files]
        for empty_dir in empty_dirs:
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

    # Start the master directory process
    master_directory()
