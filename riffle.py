"""
Riffle
===================

Credits:
- Developer: @flyhighr
- Discord: flyhighr
- Email: shekhar9330@gmail.com
Licensed under GNU GENERAL PUBLIC LICENSE

Feel free to explore, modify, and contribute :>.

"""

import json ,random, threading, time, os, pygame, io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image
import customtkinter as ctk
import tkinter.messagebox as messagebox

class Riffle:
    def __init__(self, root):

        """
    Initialize Riffle,
    Sets up the initial state of the music player, including:
    - Pygame mixer initialization
    - UI configuration
    - Theme settings
    - Player state variables
    - Library loading
    - Event monitoring and progress tracking

    """
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.root = root

        self.themes = { 
        "Lavender": {
            "primary": "#9467bd",
            "secondary": "#c2a5cf",
            "background": "#f0e6ff",
            "text": "#4a4a4a",
            "accent": "#6a5acd",
            "appearance_mode": "light",
            "color_theme": "dark-blue",
            "font_family": "Segoe UI",
            "border_radius": 15,
            "hover_effect": 0.9
        }, 
        "Ocean": {
            "primary": "#4e79a7",
            "secondary": "#6baed6",
            "background": "#e6f2ff",
            "text": "#2c3e50",
            "accent": "#3498db",
            "appearance_mode": "light",
            "color_theme": "blue",
            "font_family": "Roboto",
            "border_radius": 20,
            "hover_effect": 0.85
        },
        "Forest": {
            "primary": "#3cb371",
            "secondary": "#2e8b57",
            "background": "#e6f3e6",
            "text": "#2d4a2d",
            "accent": "#228b22",
            "appearance_mode": "light",
            "color_theme": "green",
            "font_family": "Open Sans",
            "border_radius": 10,
            "hover_effect": 0.95
        },
        
        "Pastel": {
            "primary": "#ff9ff3",
            "secondary": "#a29bfe",
            "background": "#f8e6ff",
            "text": "#2d3436",
            "accent": "#6c5ce7",
            "appearance_mode": "light",
            "color_theme": "blue",
            "font_family": "Comic Sans MS",
            "border_radius": 18,
            "hover_effect": 0.85
        },
        "Sun": {
            "primary": "#f39c12",
            "secondary": "#d35400",
            "background": "#fef5e7",
            "text": "#34495e",
            "accent": "#e67e22",
            "appearance_mode": "light",
            "color_theme": "dark-blue",
            "font_family": "Trebuchet MS",
            "border_radius": 20,
            "hover_effect": 0.85
        },
        "Arctic": {
            "primary": "#3498db",
            "secondary": "#2980b9",
            "background": "#e9f7ef",
            "text": "#2c3e50",
            "accent": "#1abc9c",
            "appearance_mode": "light",
            "color_theme": "blue",
            "font_family": "Calibri",
            "border_radius": 25,
            "hover_effect": 0.8
        },

        "Midnight": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "background": "#1a2633",
            "text": "#ecf0f1",
            "accent": "#3498db",
            "appearance_mode": "dark",
            "color_theme": "dark-blue",
            "font_family": "Lato",
            "border_radius": 12,
            "hover_effect": 0.7
        },
        "Royal Midnight": {
            "primary": "#8e44ad",
            "secondary": "#9b59b6",
            "background": "#2c3e50",
            "text": "#ecf0f1",
            "accent": "#e74c3c",
            "appearance_mode": "dark",
            "color_theme": "dark-blue",
            "font_family": "Verdana",
            "border_radius": 16,
            "hover_effect": 0.75
        }, # Add More themes if you want
            }
        
        # Default is Lavender
        self.current_theme_name = "Lavender"
        self.current_theme = self.themes.get(
        self.current_theme_name, 
        list(self.themes.values())[0]  
        )

        ctk.set_appearance_mode(self.current_theme["appearance_mode"])
        ctk.set_default_color_theme(self.current_theme["color_theme"])

        self.root.title("Riffle")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.playlists = {}
        self.current_playlist_name = None
        self.current_track_index = None
        self.is_playing = False
        self.event_thread = None
        self.shuffle_mode = False
        self.repeat_mode = 0  # 0: No Repeat, 1: Repeat One, 2: Repeat All
        self.current_track_position = 0
        self.total_track_length = 0
        self.library_file = "lib.json"

        self.load_library()
        self.start_event_monitoring()
        self.create_ui()
        self.apply_current_theme()
        self.start_progress_tracking()


    def create_ui(self):
        """
    Builds the main window layout with:
    - Left sidebar for playlists
    - Main content area
    - Track display
    - Playback controls
    - Volume slider
    - Theme selection dropdown

    """
        self.root.configure(padx=20, pady=20)
        main_container = ctk.CTkFrame(self.root, corner_radius=10)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=3)
        main_container.grid_rowconfigure(0, weight=1)
        left_sidebar = ctk.CTkFrame(main_container, width=250, corner_radius=10)

        left_sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_sidebar.grid_propagate(False)
        ctk.CTkLabel(left_sidebar, text="Playlists", font=("Arial", 20, "bold")).pack(pady=10)

        self.playlist_listbox = ctk.CTkScrollableFrame(left_sidebar, width=230)
        self.playlist_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.update_playlist_listbox()

        playlist_btn_frame = ctk.CTkFrame(left_sidebar, fg_color="transparent")
        playlist_btn_frame.pack(pady=10)
        self.new_playlist_btn = ctk.CTkButton(playlist_btn_frame, text="New Playlist", command=self.create_playlist)
        self.new_playlist_btn.pack(side="left", padx=5)
        self.delete_playlist_btn = ctk.CTkButton(playlist_btn_frame, text="Delete Playlist", command=self.delete_playlist)
        self.delete_playlist_btn.pack(side="left", padx=5)
        content_area = ctk.CTkFrame(main_container, corner_radius=10)

        content_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        content_area.grid_rowconfigure(4, weight=1)

        track_display_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        track_display_frame.pack(pady=10, fill="x")
        self.album_art = ctk.CTkLabel(track_display_frame, text="🎵", font=("Arial", 50))
        self.album_art.pack(side="left", padx=10)
        self.track_display = ctk.CTkLabel(track_display_frame, text="No Track Selected", font=("Arial", 18))
        self.track_display.pack(side="left", padx=10)
        self.track_listbox = ctk.CTkScrollableFrame(content_area, height=200)
        self.track_listbox.pack(padx=20, pady=10, fill="x")
        add_to_playlist_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        add_to_playlist_frame.pack(pady=10)
        self.add_to_playlist_btn = ctk.CTkButton(add_to_playlist_frame, text="Add to Playlist", command=self.add_track_to_playlist)
        self.add_to_playlist_btn.pack()
        progress_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        progress_frame.pack(pady=10, padx=20, fill="x")
        self.current_time_label = ctk.CTkLabel(progress_frame, text="0:00", width=50)
        self.current_time_label.pack(side="left")

        self.progress_slider = ctk.CTkSlider(
            progress_frame, 
            from_=0, to=100, 
            command=self.on_progress_slider_move,
            width=600
        )
        self.progress_slider.pack(side="left", expand=True, padx=10)
        self.total_time_label = ctk.CTkLabel(progress_frame, text="0:00", width=50)
        self.total_time_label.pack(side="left")
        control_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        control_frame.pack(pady=10)
        self.prev_btn = ctk.CTkButton(control_frame, text="⏮️ Previous", command=self.play_previous)
        self.prev_btn.pack(side="left", padx=5)
        self.play_btn = ctk.CTkButton(control_frame, text="▶️ Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5)
        self.next_btn = ctk.CTkButton(control_frame, text="⏭️ Next", command=self.play_next)
        self.next_btn.pack(side="left", padx=5)
        additional_controls = ctk.CTkFrame(content_area, fg_color="transparent")
        additional_controls.pack(pady=10)
        self.repeat_btn = ctk.CTkButton(additional_controls, text="🔁 Repeat", command=self.toggle_repeat)
        self.repeat_btn.pack(side="left", padx=5)
        self.shuffle_btn = ctk.CTkButton(additional_controls, text="🔀 Shuffle", command=self.toggle_shuffle)
        self.shuffle_btn.pack(side="left", padx=5)

        volume_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        volume_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(volume_frame, text="Volume:").pack(side="left")
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, 
                                           command=self.adjust_volume)
        self.volume_slider.set(50)
        self.volume_slider.pack(side="left", expand=True, padx=10)
        self.volume_percentage = ctk.CTkLabel(volume_frame, text="50%", width=50)
        self.volume_percentage.pack(side="left")

        menu_bar = ctk.CTkFrame(self.root, fg_color="transparent")
        menu_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.open_folder_btn = ctk.CTkButton(menu_bar, text="Open Folder", command=self.load_music_folder)
        self.open_folder_btn.pack(side="left", padx=5)
        self.add_files_btn = ctk.CTkButton(menu_bar, text="Add Files", command=self.add_music_files)
        self.add_files_btn.pack(side="left", padx=5)
        menu_bar = ctk.CTkFrame(self.root, fg_color="transparent")
        menu_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.open_folder_btn = ctk.CTkButton(menu_bar, text="Open Folder", command=self.load_music_folder)
        self.open_folder_btn.pack(side="left", padx=5)
        self.add_files_btn = ctk.CTkButton(menu_bar, text="Add Files", command=self.add_music_files)
        self.add_files_btn.pack(side="left", padx=5)
        self.theme_var = ctk.StringVar(value=self.current_theme_name)
        self.theme_dropdown = ctk.CTkOptionMenu(
            menu_bar, 
            values=list(self.themes.keys()), 
            command=self.change_theme,
            variable=self.theme_var
        )
        self.theme_dropdown.pack(side="left", padx=5)

    def apply_current_theme(self):

        """
    Apply the selected theme across all UI elements.
    
    Updates:
    - Button styles
    - Label colors and fonts
    - Slider appearances
    - Overall UI color scheme

    """
        theme = self.current_theme
        font_family = theme["font_family"]
        border_radius = theme["border_radius"]
        self.root.configure(
            fg_color=theme["background"]
        )
        
        buttons_to_theme = [
            self.new_playlist_btn, 
            self.delete_playlist_btn, 
            self.add_to_playlist_btn,
            self.prev_btn, 
            self.play_btn, 
            self.next_btn, 
            self.repeat_btn, 
            self.shuffle_btn,
            self.open_folder_btn,
            self.add_files_btn
        ]
        
        for button in buttons_to_theme:
            button.configure(
                fg_color=theme["primary"], 
                hover_color=theme["secondary"],
                text_color=theme["text"],
                font=(font_family, 12, "bold"),
                corner_radius=border_radius
            )

        label_widgets = [
            self.track_display, 
            self.current_time_label, 
            self.total_time_label
        ]
        
        for label in label_widgets:
            label.configure(
                text_color=theme["text"],
                font=(font_family, 14)
            )

        self.progress_slider.configure(
            progress_color=theme["accent"],
            fg_color=theme["secondary"]
        )

        self.volume_slider.configure(
            progress_color=theme["accent"],
            fg_color=theme["secondary"]
        )

        self.playlist_listbox.configure(fg_color=theme["background"])
        self.track_listbox.configure(fg_color=theme["background"])

    def change_theme(self, theme_name):
        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]
        ctk.set_appearance_mode(self.current_theme["appearance_mode"])
        ctk.set_default_color_theme(self.current_theme["color_theme"])
        self.apply_current_theme()
        self.save_library()

    def play_track(self):
        if not self.current_playlist_name or self.current_playlist_name not in self.playlists:
            return
        playlist = self.playlists[self.current_playlist_name]

        if not playlist or self.current_track_index is None or self.current_track_index < 0:
            self.current_track_index = 0
        self.current_track_index = self.current_track_index % len(playlist)
        track_path = playlist[self.current_track_index]
        if not os.path.exists(track_path):
            self.handle_missing_track(track_path)

            if not self.playlists[self.current_playlist_name]:
                self.track_display.configure(text="No Track Available")
                self.album_art.configure(image=None)
                self.is_playing = False
                self.play_btn.configure(text="▶️ Play")
                pygame.mixer.music.stop()
                return
            
            if self.current_track_index >= len(self.playlists[self.current_playlist_name]):
                self.current_track_index = 0

            track_path = self.playlists[self.current_playlist_name][self.current_track_index]

        try:
            audio = MP3(track_path)
            self.total_track_length = audio.info.length
        except Exception as e:
            print(f"Error getting track length: {e}")
            self.total_track_length = 0

        try:
            pygame.mixer.music.load(track_path)
            if self.current_track_position > 0:
                pygame.mixer.music.play(start=self.current_track_position)
            else:
                pygame.mixer.music.play()
           
            track_name = os.path.basename(track_path)
            self.track_display.configure(text=track_name)
            album_art = self.extract_album_art(track_path)
            self.album_art.configure(image=album_art)
            self.play_btn.configure(text="⏸️ Pause")
            self.is_playing = True

        except Exception as e:
            messagebox.showerror(
                "Track Error", 
                f"Could not play track '{os.path.basename(track_path)}'. Error: {str(e)}"
            )
            self.handle_missing_track(track_path)

    def handle_missing_track(self, track_path):
        """
        Handle a missing track by removing it from the current playlist
        and showing an error message.
    
        Args:
            track_path (str): Path of the missing track
        """
        if self.current_playlist_name and track_path in self.playlists[self.current_playlist_name]:
            self.playlists[self.current_playlist_name].remove(track_path)

            self.save_library()
            self.update_track_listbox()

            messagebox.showerror(
                "Track Not Found", 
                f"The track '{os.path.basename(track_path)}' could not be found. It has been removed from the playlist."
            )

    def toggle_play(self):
        """
    Toggle between play and pause states.
    
    Manages:
    - Starting playback from first track if no track is selected
    - Pausing current track
    - Saving current track position
    - Updating play/pause button

    """
        if not self.current_playlist_name:
            return
        playlist = self.playlists[self.current_playlist_name]

        if not playlist:
            return

        if not self.is_playing:
            if self.current_track_index is None:
                self.current_track_index = 0

            if not pygame.mixer.music.get_busy():
                self.play_track()
            else:
                pygame.mixer.music.unpause()
            
            self.is_playing = True
            self.play_btn.configure(text="⏸️ Pause")
        else:
            pygame.mixer.music.pause()
            #current position
            current_pos = pygame.mixer.music.get_pos() / 1000
            self.current_track_position += current_pos if current_pos > 0 else 0
            
            self.is_playing = False
            self.play_btn.configure(text="▶️ Play")

    def track_progress(self):

        """
    Continuously track and update track playback progress.
    
    Runs in a background thread to:
    - Update progress slider
    - Update current and total time labels
    - Handle track ending logic

    """
        while True:
            try:
                if not self.current_playlist_name or not self.playlists.get(self.current_playlist_name):
                    time.sleep(1)
                    continue

                playlist = self.playlists[self.current_playlist_name]
                
                if not playlist or self.current_track_index is None or self.current_track_index < 0:
                    time.sleep(1)
                    continue

                self.current_track_index = self.current_track_index % len(playlist)
                track_path = playlist[self.current_track_index]

                audio = MP3(track_path)
                total_length = audio.info.length

                if pygame.mixer.music.get_busy():
                    current_pos = pygame.mixer.music.get_pos() / 1000
                    actual_pos = self.current_track_position + current_pos

                    if actual_pos >= total_length:
                        self.root.after(0, self.track_ended)
                        continue
                    progress = (actual_pos / total_length) * 100
                    self.progress_slider.set(progress)
                    self.current_time_label.configure(text=self.format_time(actual_pos))
                    self.total_time_label.configure(text=self.format_time(total_length))
                    
                time.sleep(1)
            except Exception as e:
                print(f"Error tracking progress: {e}")
                time.sleep(1)

    def on_progress_slider_move(self, val):

        """
    Handle track seeking when progress slider is moved.
    Args:
    - val: Slider position value (0-100)
    Calculates and sets new track position based on slider movement.

    """
        if not self.current_playlist_name or not self.playlists.get(self.current_playlist_name):
            return
        
        playlist = self.playlists[self.current_playlist_name]

        if self.current_track_index is None or self.current_track_index < 0 or self.current_track_index >= len(playlist):
            self.current_track_index = 0

        track_path = playlist[self.current_track_index]
        
        try:
            audio = MP3(track_path)
            total_length = audio.info.length
            new_pos = (val / 100) * total_length
            self.current_track_position = new_pos
            pygame.mixer.music.rewind()
            pygame.mixer.music.play(start=new_pos)
            self.current_time_label.configure(text=self.format_time(new_pos))
            self.total_time_label.configure(text=self.format_time(total_length))

        except Exception as e:
            print(f"Error seeking track: {e}")

    def play_selected_track(self, track_path):
        if not self.current_playlist_name:
            return
        
        playlist = self.playlists[self.current_playlist_name]
        index = playlist.index(track_path)
        self.current_track_index = index
        self.current_track_position = 0
        
        self.play_track()
    
    def track_ended(self):

        """
    Handle logic when a track finishes playing.
    
    Manages track progression based on:
    - Repeat mode (No Repeat, Repeat One, Repeat All)
    - Shuffle mode

    """
        if not self.current_playlist_name or not self.playlists.get(self.current_playlist_name):
            return
        
        playlist = self.playlists[self.current_playlist_name]
        
        if not playlist:
            return
        self.current_track_position = 0

        if self.repeat_mode == 1:  # Repeat One
            self.play_track()
        elif self.shuffle_mode:
            self.current_track_index = random.randint(0, len(playlist) - 1)
            self.play_track()
        elif self.repeat_mode == 2:  # Repeat All
            self.current_track_index = (self.current_track_index + 1) % len(playlist)
            self.play_track()
        else:
            self.current_track_index = (self.current_track_index + 1) % len(playlist)
            self.play_track()
    
    def play_next(self):
        if not self.current_playlist_name:
            return
        
        playlist = self.playlists[self.current_playlist_name]
        
        if playlist:
            self.current_track_index = (self.current_track_index + 1) % len(playlist)
            self.current_track_position = 0
            self.play_track()
    
    def play_previous(self):
        if not self.current_playlist_name:
            return
        
        playlist = self.playlists[self.current_playlist_name]
        
        if playlist:
            self.current_track_index = (self.current_track_index - 1) % len(playlist)
            self.current_track_position = 0
            self.play_track()

    def start_event_monitoring(self):

        """
    Start a background thread to monitor Pygame events.
    
    Continuously checks for track end events and triggers appropriate actions.
    Uses a daemon thread to allow clean program exit.

    """
        def monitor_events():
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.USEREVENT:
                       
                        self.root.after(0, self.track_ended)
                time.sleep(0.1)

        # Use daemon thread to allow program to exit cleanly
        self.event_thread = threading.Thread(target=monitor_events, daemon=True)
        self.event_thread.start()

    def start_progress_tracking(self):
        progress_thread = threading.Thread(target=self.track_progress, daemon=True)
        progress_thread.start()
    
    def load_library(self):
        try:
            with open(self.library_file, 'r') as f:
                library_data = json.load(f)
                self.playlists = library_data.get('playlists', {"Default": []})
                self.current_theme_name = library_data.get('current_theme', 'Lavender')
                self.current_theme = self.themes.get(
                    self.current_theme_name, 
                    list(self.themes.values())[0]
                )
                ctk.set_appearance_mode(self.current_theme["appearance_mode"])
                ctk.set_default_color_theme(self.current_theme["color_theme"])
            
        except FileNotFoundError:
            self.playlists = {"Default": []}
            self.current_theme_name = 'Lavender'
            self.current_theme = self.themes['Lavender']
            self.save_library()

    def save_library(self):
        with open(self.library_file, 'w') as f:
            json.dump({
                'playlists': self.playlists,
                'current_theme': self.current_theme_name
            }, f, indent=4)
    
    def load_music_folder(self):
        if not self.current_playlist_name:
            messagebox.showerror("Error", "Select a playlist first!")
            return
        
        folder_path = ctk.filedialog.askdirectory()
        if folder_path:
            new_tracks = [
                os.path.join(folder_path, filename) 
                for filename in os.listdir(folder_path) 
                if filename.lower().endswith(('.mp3', '.wav', '.ogg'))
            ]
            unique_tracks = [
                track for track in new_tracks 
                if track not in self.playlists[self.current_playlist_name]
            ]

            self.playlists[self.current_playlist_name].extend(unique_tracks)
            self.update_track_listbox()
            self.save_library()

    def add_music_files(self):
        if not self.current_playlist_name:
            messagebox.showerror("Error", "Select a playlist first!")
            return
        files = ctk.filedialog.askopenfilenames(filetypes=[
            ("Audio Files", "*.mp3 *.wav *.ogg")
        ])
        unique_tracks = [
            file for file in files 
            if file not in self.playlists[self.current_playlist_name]
        ]

        self.playlists[self.current_playlist_name].extend(unique_tracks)
        self.update_track_listbox()
        self.save_library()
    
    def create_playlist(self):
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name:", title="New Playlist")
        name = dialog.get_input()
        
        if name and name not in self.playlists:
            self.playlists[name] = []
            self.update_playlist_listbox()
            self.save_library()
    
    def delete_playlist(self):
        if not self.playlists or len(self.playlists) <= 1:
            from tkinter import messagebox
            messagebox.showerror("Error", "Cannot delete the last playlist!")
            return
    
        dialog = ctk.CTkInputDialog(text="Enter Playlist Name to Delete:", title="Delete Playlist")
        name = dialog.get_input()
    
        if name in self.playlists and name != "Default":
            del self.playlists[name]
            self.update_playlist_listbox()
            self.save_library()
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", "Playlist not found or cannot be deleted!")
    
    def update_playlist_listbox(self):
        for widget in self.playlist_listbox.winfo_children():
            widget.destroy()

        for playlist_name in self.playlists:
            btn = ctk.CTkButton(
                self.playlist_listbox, 
                text=playlist_name, 
                command=lambda name=playlist_name: self.load_playlist(name)
            )
            btn.pack(fill="x", pady=2)
    
    def load_playlist(self, playlist_name):
        if playlist_name in self.playlists:
            self.current_playlist_name = playlist_name
            self.update_track_listbox()
    
    def update_track_listbox(self):
        for widget in self.track_listbox.winfo_children():
            widget.destroy()

        if not self.current_playlist_name:
            return
        
        for track_path in self.playlists[self.current_playlist_name]:
            track_name = os.path.basename(track_path)
            track_label = ctk.CTkButton(
                self.track_listbox, 
                text=track_name, 
                command=lambda path=track_path: self.play_selected_track(path)
            )
            track_label.pack(fill="x", pady=2)
    
    def add_track_to_playlist(self):
        if not self.playlists:
            messagebox.showerror("Error", "Create a playlist first!")
            return

        if not self.current_playlist_name:
            self.current_playlist_name = list(self.playlists.keys())[0]

        files = ctk.filedialog.askopenfilenames(filetypes=[
            ("Audio Files", "*.mp3 *.wav *.ogg")
        ])

        new_tracks = [
            file for file in files 
            if file not in self.playlists[self.current_playlist_name]
        ]

        self.playlists[self.current_playlist_name].extend(new_tracks)

        self.update_track_listbox()
        self.save_library()
  
    def toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        repeat_texts = ["🔁 No Repeat", "🔂 Repeat One", "🔁 Repeat All"]
        self.repeat_btn.configure(text=repeat_texts[self.repeat_mode])
    
    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        shuffle_color = self.current_theme["primary"] if self.shuffle_mode else "white"
        self.shuffle_btn.configure(fg_color=shuffle_color)
    
    def adjust_volume(self, val):
        pygame.mixer.music.set_volume(val/100)
        self.volume_percentage.configure(text=f"{int(val)}%")
    
    def format_time(self, seconds):
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes}:{secs:02d}"
    
    def extract_album_art(self, track_path):
        try:
            audio = ID3(track_path)
            for tag in audio.tags:
                if tag.startswith('APIC'):
                    artwork = tag.data
                    image = Image.open(io.BytesIO(artwork))
                    image = image.resize((200, 200))
                    return ctk.CTkImage(light_image=image, size=(200, 200))
        except Exception:
            pass
        default_image = Image.new('RGB', (150, 150), color='lavender')
        return ctk.CTkImage(light_image=default_image, size=(150, 150))
   
def main():
    root = ctk.CTk()
    Riffle(root)
    root.mainloop()

if __name__ == "__main__":
    main()
