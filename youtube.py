import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from yt_dlp import YoutubeDL
import threading
import os
from kivy.uix.image import AsyncImage, Image
from kivy.uix.progressbar import ProgressBar

kivy.require('2.0.0')  # Replace with your installed version

class DownloadApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_history = []
        self.downloads_in_progress = {}
        self.available_qualities = []
        self.selected_filetype = 'MP4'  # Default value
        self.selected_quality = '720p'  # Default value

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=[10, 20, 10, 10], spacing=10)  # Left, Top, Right, Bottom padding


        # URL input with thumbnail container
        url_container = BoxLayout(size_hint_y=None, height=40, spacing=10)
        # Thumbnail image
        self.url_thumbnail = AsyncImage(
            size_hint=(None, None),
            size=(160, 90),  # 16:9 aspect ratio, larger size
            pos_hint={'center_y': 0.5}
        )
        

        # URL input with smaller height
        self.url_input = TextInput(
            hint_text='Enter video or playlist URL',
            size_hint=(0.8, None),
            height=40,
            pos_hint={'center_y': 0.5},
            multiline=False,
            use_bubble=True,  # Enables the cut/copy/paste bubble
            use_handles=True  # Enables selection handles
        )
        self.url_input.bind(text=self.on_url_change)
        url_container.add_widget(self.url_thumbnail)
        url_container.add_widget(self.url_input)

        layout.add_widget(url_container)
        
    
        # Style for all buttons
        button_style = {
            'size_hint': (0.5, None),
            'height': 40,
            'background_color': (0.2, 0.6, 1, 1),
            'background_normal': '',
            'pos_hint': {'center_x': 0.5},
            'padding': (20, 10),
            'font_size': '16sp'
        }
    
        # Apply style to all dropdown buttons
        dropdown_button_style = {
            'size_hint_y': None,
            'height': 40,
            'background_color': (0.3, 0.7, 1, 1),
            'background_normal': '',
            'size_hint_x': 0.8
        }
        
        # Playlist selection dropdown
        self.playlist_dropdown = DropDown()
        self.single_button = Button(text="Single Video", **button_style)
        self.single_button.bind(on_release=self.select_single)
        self.playlist_dropdown.add_widget(self.single_button)

        self.playlist_button = Button(text="Full Playlist", **button_style)
        self.playlist_button.bind(on_release=self.select_playlist)
        self.playlist_dropdown.add_widget(self.playlist_button)

        self.playlist_select = Button(text="Choose Download Type", **button_style)
        self.playlist_select.bind(on_release=self.playlist_dropdown.open)
        layout.add_widget(self.playlist_select)
        
        
    
        # Download type button
        self.download_type_button = Button(text='Choose Type', **button_style)
        self.download_type_dropdown = DropDown()
        for type_option in ['Music', 'Video']:
            btn = Button(text=type_option, **dropdown_button_style)
            btn.bind(on_release=lambda btn: self.select_download_type(btn.text))
            self.download_type_dropdown.add_widget(btn)
        self.download_type_button.bind(on_release=self.download_type_dropdown.open)
        layout.add_widget(self.download_type_button)
    
        # File type button
        self.filetype_button = Button(text='Choose File Type', **button_style)
        self.filetype_dropdown = DropDown()
        for file_type in ['MP3', 'MP4']:
            btn = Button(text=file_type, **dropdown_button_style)
            btn.bind(on_release=lambda btn: self.select_filetype(btn.text))
            self.filetype_dropdown.add_widget(btn)
        self.filetype_button.bind(on_release=self.filetype_dropdown.open)
        layout.add_widget(self.filetype_button)
    
        # Quality button
        self.quality_button = Button(text='Choose Quality', **button_style)
        self.quality_dropdown = DropDown()
        
        self.video_qualities = ['8K', '4K', '1080p', '720p', '480p', '360p']
        self.audio_qualities = ['320kbps', '256kbps', '192kbps', '128kbps', '96kbps']
        
        # Initial population with video qualities
        for quality in self.video_qualities:
            btn = Button(text=quality, **dropdown_button_style)
            btn.bind(on_release=lambda btn=btn: self.select_quality(btn.text))
            self.quality_dropdown.add_widget(btn)
        
        self.quality_button.bind(on_release=self.quality_dropdown.open)
        layout.add_widget(self.quality_button)
    
        # Download button with special styling
        button_style['background_color'] = (0.2, 0.8, 0.2, 1)  # Green color for download button
        self.download_button = Button(
            text='Start Download',
            **button_style
        )
        self.download_button.bind(on_release=self.start_download)
        layout.add_widget(self.download_button)
    
        # History section
        self.history_label = Label(
            text='Download History:',
            size_hint=(1, None),
            height=40,
            font_size='18sp'
        )
        layout.add_widget(self.history_label)
    
        self.history_box = ScrollView(size_hint=(0.9, None), height=200, pos_hint={'center_x': 0.5})
        self.history_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.history_box.add_widget(self.history_layout)
        layout.add_widget(self.history_box)
    
        return layout

    def on_url_change(self, instance, value):
        if value:
            try:
                with YoutubeDL({'quiet': True}) as ydl:
                    if 'list=' in value:
                        # Get video ID from playlist URL
                        video_id = value.split('v=')[1].split('&')[0]
                        # Form direct video URL
                        clean_url = f"https://www.youtube.com/watch?v={video_id}"
                        info = ydl.extract_info(clean_url, download=False)
                    else:
                        info = ydl.extract_info(value, download=False)
                    thumbnail_url = info['thumbnail']
                    self.url_thumbnail.source = thumbnail_url
            except:
                self.url_thumbnail.source = ''


    
    def select_single(self, instance):
        self.playlist_select.text = "Single Video"
        self.playlist_dropdown.dismiss()
        self.download_type = 'single'

    def select_playlist(self, instance):
        self.playlist_select.text = "Full Playlist"
        self.playlist_dropdown.dismiss()
        self.download_type = 'playlist'

    def select_download_type(self, text):
        self.download_type_button.text = text
        self.download_type_dropdown.dismiss()

        # Clear and update filetype dropdown based on selection
        self.filetype_dropdown.clear_widgets()
        # Clear and update quality dropdown based on selection
        self.quality_dropdown.clear_widgets()

        if text == "Music":
            file_types = ['MP3', 'WAV', 'AAC', 'FLAC', 'OGG', 'M4A']
            self.filetype_button.text = 'MP3'  # Set default for Music
            # Set audio qualities
            qualities = ['320kbps', '256kbps', '192kbps', '128kbps', '96kbps']
            self.quality_button.text = '192kbps'  # Set default quality
        else:  # Video
            file_types = ['MP4', 'AVI', 'MKV', 'MOV', 'WMV', 'FLV']
            self.filetype_button.text = 'MP4'  # Set default for Video
            # Set video qualities
            qualities = ['8K', '4K', '1080p', '720p', '480p', '360p']
            self.quality_button.text = '720p'  # Set default quality

        for file_type in file_types:
            btn = Button(
                text=file_type,
                size_hint_y=None,
                height=40,
                size_hint_x=0.8,
                background_color=(0.3, 0.7, 1, 1),
                background_normal=''
            )
            btn.bind(on_release=lambda btn=btn: self.select_filetype(btn.text))
            self.filetype_dropdown.add_widget(btn)

        for quality in qualities:
            btn = Button(
                text=quality,
                size_hint_y=None,
                height=40,
                size_hint_x=0.8,
                background_color=(0.3, 0.7, 1, 1),
                background_normal=''
            )
            btn.bind(on_release=lambda btn=btn: self.select_quality(btn.text))
            self.quality_dropdown.add_widget(btn)

    def select_filetype(self, text):
        self.filetype_button.text = text
        self.filetype_dropdown.dismiss()

    def show_download_type_dropdown(self, instance):
        self.download_type_dropdown.open(instance)

    def select_music(self, instance):
        self.selected_download_type.text = "Music"
        self.download_type_dropdown.dismiss()

    def select_video(self, instance):
        self.selected_download_type.text = "Video"
        self.download_type_dropdown.dismiss()

    def show_filetype_dropdown(self, instance):
        self.filetype_dropdown.open(instance)

    def select_mp3(self, instance):
        self.selected_filetype = "MP3"
        self.filetype_dropdown.dismiss()

    def select_mp4(self, instance):
        self.selected_filetype = "MP4"
        self.filetype_dropdown.dismiss()

    def show_quality_dropdown(self, instance):
        self.quality_dropdown.open(instance)

    def update_quality_dropdown(self, qualities):
        self.quality_dropdown.clear_widgets()
        for quality in qualities:
            btn = Button(
                text=quality, 
                size_hint_y=None, 
                height=40,
                size_hint_x=1
            )
            btn.bind(on_release=lambda btn=btn: self.select_quality(btn.text))
            self.quality_dropdown.add_widget(btn)

    def select_quality(self, quality):
        self.quality_button.text = quality
        self.selected_quality = quality
        self.quality_dropdown.dismiss()

    def start_download(self, instance):
        url = self.url_input.text
        if not url:
            return

        # Create a thread to download without blocking the UI
        download_thread = threading.Thread(target=self.download_video, args=(url,))
        download_thread.start()

    def get_download_options(self):
        base_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'socket_timeout': 30,
            'nocheckcertificate': True,
            'quiet': True,
            'noplaylist': self.playlist_select.text == "Single Video",  # Dynamically checks button text
            'no_warnings': True,  # Added to suppress warnings
            'noprogress': True    # Added to suppress progress prints
        }
    
        selected_format = self.filetype_button.text
        selected_quality = self.quality_button.text
    
        format_options = {
            'MP3': {
                'format': 'bestaudio',
                'extract_audio': True,
                'audio_format': 'mp3',
                'audio_quality': 0,
                'writethumbnail': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                'preferredquality': selected_quality[:-4],  # Remove 'kbps' from the quality string
                }, {
                    'key': 'EmbedThumbnail',
                }, {
                    'key': 'FFmpegMetadata',
                }]
            },
            'WAV': {
                'format': 'bestaudio',
                'extract_audio': True,
                'audio_format': 'wav',
                'audio_quality': 0,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': selected_quality[:-4],  # Remove 'kbps' from the quality string
                }]
            },
            'FLAC': {
                'format': 'bestaudio',
                'extract_audio': True,
                'audio_format': 'flac',
                'audio_quality': 0,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                    'preferredquality': selected_quality[:-4],  # Remove 'kbps' from the quality string
                }]
            },
            'MP4': {
                'format': f'bestvideo[height<={selected_quality[:-1]}]+bestaudio/best[height<={selected_quality[:-1]}]',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            },
            'MKV': {
                'format': f'bestvideo[height<={selected_quality[:-1]}]+bestaudio/best[height<={selected_quality[:-1]}]',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mkv'
                }]
            },
            'AVI': {
                'format': f'bestvideo[height<={selected_quality[:-1]}]+bestaudio/best[height<={selected_quality[:-1]}]',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'avi'
                }]
            }
        }
    
        opts = format_options[selected_format]
        opts.update(base_opts)
        return opts

    def download_video(self, url):
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        try:
            ydl_opts = self.get_download_options()
            with YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as e:
            self.update_history(url, f"Failed: {str(e)}")

    def show_playlist_selection(self, playlist_items):
        content = BoxLayout(orientation='vertical', spacing=5)

        # Add check/uncheck all buttons
        check_buttons = BoxLayout(size_hint_y=None, height=40)
        check_all = Button(text='Check All')
        uncheck_all = Button(text='Uncheck All')
        check_buttons.add_widget(check_all)
        check_buttons.add_widget(uncheck_all)
        content.add_widget(check_buttons)

        # Scrollable list of videos with checkboxes
        scroll = ScrollView(size_hint=(1, 1))
        videos_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        videos_layout.bind(minimum_height=videos_layout.setter('height'))

        checkboxes = []
        for item in playlist_items:
            row = BoxLayout(size_hint_y=None, height=40)
            checkbox = CheckBox(size_hint_x=None, width=40)
            label = Label(text=item['title'], halign='left')
            row.add_widget(checkbox)
            row.add_widget(label)
            videos_layout.add_widget(row)
            checkboxes.append((checkbox, item))

        scroll.add_widget(videos_layout)
        content.add_widget(scroll)

    def perform_download(self, video_info):
        download_id = video_info['id']
        self.downloads_in_progress[download_id] = {
            'status': 'downloading',
            'progress': 0,
            'cancel': False
        }

        ydl_opts = {
            'format': f'bestvideo[height={self.selected_quality[:-1]}]+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': self.selected_filetype.lower()
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: self.progress_hook(d, download_id)]
        }

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                progress = int(float(d['downloaded_bytes']) / float(d['total_bytes']) * 100)
                filename = d.get('filename', '').split('/')[-1].split('\\')[-1]
                video_url = d.get('info_dict', {}).get('webpage_url', '')
                
                current_info = self.downloads_in_progress.get(filename, {})
                if not current_info.get('thumbnail'):
                    with YoutubeDL({'quiet': True}) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                        current_info['thumbnail'] = info['thumbnail']
    
                current_info.update({
                    'progress': progress,
                    'status': 'downloading',
                    'type': self.filetype_button.text
                })
    
                self.downloads_in_progress[filename] = current_info
                Clock.schedule_once(lambda dt: self.update_single_line(filename, f"{filename} - {progress}%", current_info))
            except:
                pass
        elif d['status'] == 'finished':
            filename = d.get('filename', '').split('/')[-1].split('\\')[-1]
            current_info = self.downloads_in_progress.get(filename, {})
            Clock.schedule_once(lambda dt: self.update_single_line(filename, f"{filename} - Downloaded as {self.filetype_button.text}", current_info))





    def update_single_line(self, filename, status, current_info):
        # Look for existing row
        for child in self.history_layout.children:
            if isinstance(child, BoxLayout):
                for widget in child.children:
                    if isinstance(widget, Label):
                        widget.text = status
                        return

        # Create new row with proper spacing
        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10,
            padding=[5, 0, 10, 0]
        )

        thumbnail = AsyncImage(
            source=current_info.get('thumbnail', ''),
            size_hint_x=None,
            width=160,
            fit_mode='contain'
        )
    
        status_label = Label(
            text=status,
            size_hint_x=0.7,
            text_size=(None, None),
            halign='left',
            valign='middle'
        )

        row.add_widget(thumbnail)
        row.add_widget(status_label)
        self.history_layout.add_widget(row)

    def redownload(self, url):
        if url:
            self.url_input.text = url
            self.start_download(None)
    
    def mark_as_complete(self, filename):
        for child in self.history_layout.children:
            if isinstance(child, BoxLayout) and filename in str(child.children):
                status_label = child.children[0]
                status_label.text = f"{filename} - Downloaded as {self.filetype_button.text}"
    
    def update_download_line(self, filename, status):
        # Get just the filename without the path
        filename = filename.split('/')[-1].split('\\')[-1]

        download_info = self.downloads_in_progress.get(filename, {})

        # Check existing rows
        for child in self.history_layout.children:
            if isinstance(child, BoxLayout):
                for subchild in child.children:
                    if isinstance(subchild, Label) and filename in subchild.text:
                        child.clear_widgets()
                        self.add_download_row(child, filename, status, download_info)
                        return

        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.add_download_row(row, filename, status, download_info)
        self.history_layout.add_widget(row)

    def add_download_row(self, row, filename, status, download_info):
        # Thumbnail
        if 'thumbnail' in download_info:
            thumbnail = AsyncImage(
                source=download_info['thumbnail'],
                size_hint_x=None,
                width=160,
                allow_stretch=True
            )
            row.add_widget(thumbnail)

        # Status container
        status_container = BoxLayout(orientation='vertical', size_hint_x=0.6, padding=(10, 0))

        # Download progress
        download_bar = ProgressBar(
            max=100,
            value=download_info.get('progress', 0),
            size_hint_y=None,
            height=10
        )

        # Convert progress
        convert_bar = ProgressBar(
            max=100,
            value=100 if download_info.get('status') == 'completed' else 0,
            size_hint_y=None,
            height=10
        )

        status_container.add_widget(Label(text=f"{filename} [{download_info.get('type', '')}]", size_hint_y=None, height=20))
        status_container.add_widget(download_bar)
        status_container.add_widget(convert_bar)

        row.add_widget(status_container)

    def update_history(self, title, status):
        def update(dt):
            history_item = Label(
                text=f"{title} - {status}",
                size_hint_y=None,
                height=30
            )
            self.history_layout.add_widget(history_item)
        Clock.schedule_once(update)

    def retry_download(self, download_id):
        if download_id in self.downloads_in_progress:
            self.downloads_in_progress[download_id] = {
                'status': 'downloading',
                'progress': 0,
                'cancel': False
            }
            # Start new download thread
            download_thread = threading.Thread(target=self.perform_download, 
                                            args=(self.download_history[download_id]['info'],))
            download_thread.start()

if __name__ == '__main__':
    DownloadApp().run()


