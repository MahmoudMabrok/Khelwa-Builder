# YouTube Playlist Scraper

This project is a Python-based application that allows users to scrape and manage YouTube playlists. It provides a graphical user interface (GUI) built with `wxPython` and uses libraries like `pytube` and `yt-dlp` to extract playlist and video data. The scraped data is saved in JSON format for further use.

## Features

- **Scrape YouTube Playlists**: Extract video titles, URLs, thumbnails, and more from YouTube playlists.
- **Multi-Platform Support**: The application can be built and run on Windows, macOS, and Linux.
- **GUI Interface**: A user-friendly interface for entering playlist URLs and managing scraped data.
- **Save Data to JSON**: Scraped playlist data is saved in JSON files for easy access and integration with other tools.
- **Threading Support**: Multiple playlists can be processed simultaneously using threading.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.x
- `wxPython` (for the GUI)
- `pytube` (for YouTube playlist and video data extraction)
- `yt-dlp` (for fetching video titles and metadata)
- `pyinstaller` (for building the executable)

You can install the required Python libraries using the following command:

```bash
pip install wxPython pytube yt-dlp pyinstaller
```


## Installation
- Clone the repository:
```bash
git clone https://github.com/your-username/youtube-playlist-scraper.git
cd youtube-playlist-scraper
```

- Install the dependencies:
```bash
    pip install -r requirements.txt
```

- Run the application:
```bash
python app.py
```

## Build Executable

To build an executable for your platform, run the following command:

```bash
pyinstaller --onefile app.py
```