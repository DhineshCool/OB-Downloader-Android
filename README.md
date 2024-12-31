# OB Downloader Android (aka Youtube-Downloader-Android)

## History of Development

  Hi all! This script was initially intended to download video and audio from YouTube. Later, it was extended to download videos from almost all sites and social media platforms, torrents, and Google Drive. This script is based on the Termux app for downloading, hence it is called Termux Downloader, Now it is OB-Downloader.

## Additional Information

- The code was ported to work on both Linux environments and Termux by **@cool585**.
- Thanks to the original author, I was motivated to port it to Linux, making my life easier. I hope everyone likes it.
- Due to the Linux support, the name was changed to **OB_Downloader**.

## Developers

- **Owner and Developer:** Dr.Delin ([@DrDelin](https://github.com/DrDelin))
- **Co-Developer and Script Optimizer:** Dr.Senthil Manikandan ([@Senthil360](https://github.com/Senthil360))
- **Co-Developer and Linux Porter:** Dr.Dhinesh Cool ([@cool585](https://github.com/cool585))

## Installation Guide

### For Android (Stable Version)
1. Install Termux from GitHub: [Termux Releases](https://github.com/termux/termux-app/releases)
   - (ARM64 recommended, use ARM only for devices lower than Android 7)
     
2. Open Termux and type the following commands:
   
    ```sh
    pkg up -y -y -y -y
    pkg install git -y
    git clone https://github.com/DhineshCool/OB-Downloader-Android/ -b master --single-branch
    cd OB-Downloader-Android
    sh install.sh
    ```
3. Press **ALLOW** to give storage permission.
4. (Important) For Android 10 or above users: Go to **App Settings -> Termux App Settings -> Allow "Display over other apps"** permission for the script to work properly.

### For Linux (Stable Version)

1. Clone the repository on any terminal:
   
    ```sh
    git clone https://github.com/DhineshCool/OB-Downloader-Android/ -b master --single-branch
    cd OB-Downloader-Android
    ./setup_linux.sh
    ```
2. Ensure all dependencies are downloaded or manually install them.

3. Run the script:

    ```sh
    python YTD_Android.py "https://example.com/video"
    ```
4. save location :
    /home/"username"/OB_Downloader

## Troubleshooting or Repair
If the program is not working properly, showing errors, or not downloading:
1. Open the Termux app.
   
2. Type:

    ```sh
    sh refresh.sh
    ```
3. The program will be clean-installed or returned to factory default.

## Usage Guide

### How to Download Videos or Audio

1. Open the desired video, audio, playlist, or site.
2. Select the **Share** option.
3. Select **TERMUX** from the share list.
4. Your video/audio/playlist will download (Location: Internal storage of your device -> OB-Downloader).
5. For YouTube Downloads:
   - Select **Video / Audio / Best**.
   - Select the required resolution once, it will be set as default (can be changed later).
   - Skip the next step unless you want a custom format.
   - Type **"y"** if you need subtitles (available only if YouTube has them).
   - The script will take care of the rest.

6. For YouTube Music / Audio from YouTube:
   - Type your favorite audio codec (e.g., mp3, m4a, aac, webm, flac...) once as default (can be changed later).
   - The audio will be downloaded in your preferred codec.

7. Note: This script is completely automated, and the program closes itself after downloading.

## Features

### History

1. The name, site of download, and URL of the downloaded files are saved as history.

2. History is visible only by typing a specific code, ensuring privacy.

3. History can be used to:
   - Redownload previously downloaded files.
   - Revisit the site from which the file was downloaded.

4. History can be cleared.
5. Code to see history:

    ```sh
    python history.py
    ```

### Updates

1. Updates are completely automatic.
2. If you face any issues with new updates or have suggestions for new features, please note them in the issue section.

## Beta Channel Installation or Switch Between Stable and Beta (Not Recommended for General Users)

### Beta Channel Installation

1. Open Termux and type the following commands:
    ```sh
    pkg up -y -y -y -y
    pkg install git -y
    git clone https://github.com/DrDelin/Youtube-Downloader-Android/ -b Sigma-D --single-branch
    cd Youtube-Downloader-Android
    sh install.sh
    ```

### Switch Between Stable and Beta
1. Open Termux.
 
2. For the first time only, install vim-gtk:

    ```sh
    pkg install vim-gtk -y
    ```
3. Edit the `refresh.sh` file:

    ```sh
    vi refresh.sh
    ```
4. Change the 12th line:
   - Stable to Beta: change **master** to **Sigma-D**.
   - Beta to Stable: change **Sigma-D** to **master**.

5. Exit vim editor (press `esc`, type `:wq`, and press `enter`).

6. Run:

    ```sh
    sh refresh.sh
    ```

**Warning:** This channel is strictly for developers and may contain bugs. It is recommended to use the stable version.

---
