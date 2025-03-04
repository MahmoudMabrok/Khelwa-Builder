import json
import os
import re
import time
from pytube import Playlist, YouTube
from yt_dlp import YoutubeDL

import wx
import threading

def get_youtube_title(url):
    try:
        # Create a YoutubeDL object
        ydl = YoutubeDL()
        
        # Extract video info
        info_dict = ydl.extract_info(url, download=False)
        
        # Return the title
        return info_dict.get('title', None)
    except Exception as e:
        print(f"Error fetching title: {e}")
        return None

# Function to extract video information manually to avoid pytube's title issues
def get_video_info(video_id, playlist_id, title):
    try:
        return {
            'title': title,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'video_id': video_id,
            'playlist_id': playlist_id
        }
    except Exception as e:
        print(f"Error getting info for video {video_id}: {str(e)}")
        return {
            'title': f"Video {video_id}",
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'video_id': video_id,
            'playlist_id': playlist_id
        }

def extract_playlist_id(url):
    match = re.search(r'list=([\w-]+)', url)
    return match.group(1) if match else None

def process_playlist(playlist_url):
    output_dir = 'playlists'
    os.makedirs(output_dir, exist_ok=True)

    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print(f"Invalid playlist URL: {playlist_url}")
        return

    try:
        output_file = f'{output_dir}/{playlist_id}.json'
        
        # Get playlist and its videos
        try:
            playlist = Playlist(playlist_url)
            playlist_title = playlist.title
        except Exception as e:
            print(f"Error getting playlist title: {str(e)}")
            playlist_title = f"Playlist {playlist_id}"
            
        print(f'Scraping playlist: {playlist_title} (ID: {playlist_id})')
        
        # Get video URLs instead of video objects to avoid pytube title issues
        video_urls = []
        try:
            video_urls = list(playlist.video_urls)
        except Exception as e:
            print(f"Error getting video URLs: {str(e)}")
            
        videos = []
        for video_url in video_urls:
            try:
                # Extract video ID from URL
                vi = YouTube(video_url) 
                video_id_match = re.search(r'v=([\w-]+)', video_url)
                if not video_id_match:
                    print(f'Could not extract video ID from {video_url}')
                    continue
                    
                video_id = video_id_match.group(1)

                title = get_youtube_title(video_url)

                print(f'Processing video: {title} {video_id}')
                
                # Get video info
                video_data = get_video_info(video_id, playlist_id, title)
                videos.append(video_data)
                print(f'Added video: {video_data["title"]}')
                
                # Add a small delay to avoid rate limiting
                time.sleep(1)
            except Exception as e:
                print(f"Error processing video {video_url}: {str(e)}")
        
        playlist_data = {
            'playlist_title': playlist_title,
            'playlist_id': playlist_id,
            'playlist_url': playlist_url,
            'video_count': len(videos),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'videos': videos
        }
            
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
            
        print(f'Completed playlist: {playlist_title} with {len(videos)} videos')
        
    except Exception as e:
        print(f'Error scraping playlist {playlist_url}: {str(e)}')

    print(f'Successfully completed scraping process')

def submit_playlists(event):
    playlist_urls = text_box.GetValue().strip().split('\n')
    threads = []
    for playlist_url in playlist_urls:
        thread = threading.Thread(target=process_playlist, args=(playlist_url,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    wx.MessageBox("Playlists processed successfully", "Success", wx.OK | wx.ICON_INFORMATION)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Khelwa-Builder', size=(800, 600))
        self.panel = wx.Panel(self)
        self.notebook = wx.Notebook(self.panel)

        self.playlist_page = PlaylistPage(self.notebook)
        self.section_page = SectionPage(self.notebook)

        self.notebook.AddPage(self.playlist_page, "Create Playlists")
        self.notebook.AddPage(self.section_page, "Create Sections")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)

        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)

    def on_page_changed(self, event):
        if self.notebook.GetSelection() == 1:  # SectionPage is the second page
            self.section_page.load_playlists()
        event.Skip()

class PlaylistPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Enter playlist URLs (one per line):")
        vbox.Add(label, 0, wx.ALL | wx.EXPAND, 5)

        global text_box
        text_box = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(750, 400))
        vbox.Add(text_box, 1, wx.ALL | wx.EXPAND, 5)

        submit_button = wx.Button(self, label='Submit')
        submit_button.Bind(wx.EVT_BUTTON, submit_playlists)
        vbox.Add(submit_button, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(vbox)

class SectionPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.sections = []
        vbox = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Add Section")
        vbox.Add(label, 0, wx.ALL | wx.EXPAND, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        title_label = wx.StaticText(self, label="Title:")
        hbox.Add(title_label, 0, wx.ALL | wx.CENTER, 5)

        self.title_text = wx.TextCtrl(self)
        hbox.Add(self.title_text, 1, wx.ALL | wx.EXPAND, 5)

        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)

        playlist_label = wx.StaticText(self, label="Playlists:")
        vbox.Add(playlist_label, 0, wx.ALL | wx.EXPAND, 5)

        self.playlist_checkboxes = []
        self.playlist_sizer = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.playlist_sizer, 0, wx.ALL | wx.EXPAND, 5)

        add_button = wx.Button(self, label='Add Selected Playlists to Section')
        add_button.Bind(wx.EVT_BUTTON, self.add_playlists_to_section)
        vbox.Add(add_button, 0, wx.ALL | wx.CENTER, 5)

        self.section_list = wx.ListBox(self)
        vbox.Add(self.section_list, 1, wx.ALL | wx.EXPAND, 5)

        save_button = wx.Button(self, label='Save Sections to JSON')
        save_button.Bind(wx.EVT_BUTTON, self.save_sections_to_json)
        vbox.Add(save_button, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(vbox)

    def get_playlists(self):
        output_dir = 'playlists'
        if not os.path.exists(output_dir):
            return []
        return [f.replace('.json', '') for f in os.listdir(output_dir) if f.endswith('.json')]

    def load_playlists(self):
        self.playlist_sizer.Clear(True)
        self.playlist_checkboxes = []
        for playlist in self.get_playlists():
            checkbox = wx.CheckBox(self, label=playlist)
            self.playlist_checkboxes.append(checkbox)
            self.playlist_sizer.Add(checkbox, 0, wx.ALL | wx.EXPAND, 5)
        self.Layout()

    def add_playlists_to_section(self, event):
        title = self.title_text.GetValue()
        selected_playlists = [cb.GetLabel() for cb in self.playlist_checkboxes if cb.GetValue()]
        if title and selected_playlists:
            for playlist in selected_playlists:
                self.sections.append({
                    'title': title,
                    'playlist_id': playlist
                })
                self.section_list.Append(f"{title} - {playlist}")
            wx.MessageBox(f"Selected playlists added to section '{title}'", "Success", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Please enter a title and select at least one playlist", "Error", wx.OK | wx.ICON_ERROR)

    def save_sections_to_json(self, event):
        sections_data = {'sections': []}
        existing_sections = {}

        # Load existing sections if the file exists
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for section in existing_data.get('sections', []):
                    existing_sections[section['title']] = section

        for section in self.sections:
            playlist_file = f'playlists/{section["playlist_id"]}.json'
            if os.path.exists(playlist_file):
                with open(playlist_file, 'r', encoding='utf-8') as f:
                    playlist_data = json.load(f)
                    category = {
                        'playlist_id': section['playlist_id'],
                        'title': playlist_data[0]['title'],
                        'url': playlist_data[0]['thumbnail']
                    }
                    if section['title'] in existing_sections:
                        # Append new playlists to existing section, ensuring no duplication
                        existing_categories = existing_sections[section['title']]['categories']
                        if category not in existing_categories:
                            existing_categories.append(category)
                    else:
                        existing_sections[section['title']] = {
                            'title': section['title'],
                            'categories': [category]
                        }

        sections_data['sections'] = list(existing_sections.values())

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, ensure_ascii=False, indent=2)
        wx.MessageBox("Sections saved to data.json", "Success", wx.OK | wx.ICON_INFORMATION)

def create_gui():
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    create_gui()
