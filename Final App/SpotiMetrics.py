import urllib.request
from PIL import Image, ImageTk
import spotipy as sp
import requests
import customtkinter as ctk
import math
import os
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import statistics
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

width = 1300
height = 690

class SideBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(corner_radius=0)
        self.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.grid_rowconfigure(12, weight=1)
        self.title = ctk.CTkLabel(self, text="SpotiMetrics", font=ctk.CTkFont(size=25, weight="bold"))
        self.title.grid(row=0, column=0, padx=40, pady=(20, 10))    
        
        self.SongsHeading = ctk.CTkLabel(self, text="Songs", font=ctk.CTkFont(size=20))
        self.SongsHeading.grid(row=1, column=0, padx=40, pady=(20, 10))
        self.SongAnalyseOne = ctk.CTkButton(self, text="Analyse One", corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : master.show_frame(AnalyseOneSongWindow))
        self.SongAnalyseOne.grid(row=2, column=0, padx=20, pady=(0, 12))
        self.SongAnalyseMultiple = ctk.CTkButton(self, text="Analyse Multiple", corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : master.show_frame(AnalyseMultipleSongsWindow))
        self.SongAnalyseMultiple.grid(row=3, column=0, padx=20)
        
        self.ArtistHeading = ctk.CTkLabel(self, text="Artists", font=ctk.CTkFont(size=20))
        self.ArtistHeading.grid(row=4, column=0, padx=40, pady=(20, 10))
        self.ArtistAnalyseOne = ctk.CTkButton(self, text="Analyse One", corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : master.show_frame(AnalyseOneArtistWindow))
        self.ArtistAnalyseOne.grid(row=5, column=0, padx=20)
        
        self.PlaylistsHeading = ctk.CTkLabel(self, text="Playlists", font=ctk.CTkFont(size=20))
        self.PlaylistsHeading.grid(row=6, column=0, padx=40, pady=(20, 10))
        self.PlaylistAnalyseOne = ctk.CTkButton(self, text="Analyse One", corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : master.show_frame(AnalyseOnePlaylistWindow))
        self.PlaylistAnalyseOne.grid(row=7, column=0, padx=20)
        
        self.RecommendationsHeading = ctk.CTkLabel(self, text="Recommendations", font=ctk.CTkFont(size=20))
        self.RecommendationsHeading.grid(row=8, column=0, padx=40, pady=(20, 10))
        self.RecommendationsPlaylists = ctk.CTkButton(self, text="Playlists", corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : master.show_frame(PlaylistRecommendationWindow))
        self.RecommendationsPlaylists.grid(row=9, column=0, padx=20)
        
        self.AppearanceModeHeading = ctk.CTkLabel(self, text="Appearance Mode", font=ctk.CTkFont(size=20))
        self.AppearanceModeHeading.grid(row=10, column=0, padx=10, pady=(160, 10), sticky='s')
        self.AppearannceModeMenu = ctk.CTkOptionMenu(self, values=["System", "Light", "Dark"], command=self.change_appearance_mode_event)
        self.AppearannceModeMenu.grid(row=11, column=0, padx=40, pady=(0, 20), sticky='s')
        
        self.button_list = [self.SongAnalyseOne, self.SongAnalyseMultiple, self.ArtistAnalyseOne, 
                            self.PlaylistAnalyseOne, self.RecommendationsPlaylists]
        
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

class AnalyseOneSongWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # Creating the grid layout for the window
        self.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.grid_rowconfigure(1, weight=1)
        
        # Creating the left column by calling the created class and aligning it to the left of the window
        self.left_column = LeftColumn(self)
        self.left_column.grid(row=1, column=1, sticky='nsew')
        
        # Creating the frame for the search bar and aligning it to the top of the page
        self.search_frame = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.search_frame.grid(row=1, column=1, sticky='nsew')
        # Creating the grid layout for the search frame to space out the widgets
        self.search_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=1)
        self.search_frame.grid_columnconfigure(6, weight=1)
        
        # Creating the search bar and button and formatting them to their correct sizes
        self.SearchBar = ctk.CTkEntry(self.search_frame, placeholder_text="Song Name", height=35)
        self.SearchBar.grid(row=1, column=1, sticky='nsew', padx=10, pady=20, columnspan=5)
        self.SearchButton = ctk.CTkButton(self.search_frame, text="Search", width=30, height=35, corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : self.get_SearchBar())
        self.SearchButton.grid(row=1, column=6, sticky='nw', pady=(20, 0))
        
        ## Creating the frame in the left column where all the results will be displayed
        self.SongResults = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.SongResults.grid(row=2, column=1, padx=(10, 0), pady=0, sticky="nsew", columnspan=2)
        
        # A placeholder results frame 
        self.Results = ctk.CTkFrame(self.SongResults, fg_color='transparent')
        self.Results.grid(row=1, column=0, sticky='nsew')
        
        # Creating the right column by calling the created class and aligning it to the right of the window
        self.right_column = RightColumn(self)
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))

    def get_SearchBar(self):
        ## Getting the song name from the search bar and ensuring only creating a call to the API if the search bar is not empty
        SongName = self.SearchBar.get()
        if SongName == '':
            return
        # Making the call to the Spotify API and getting only the desired results
        raw_song_results = spotify_object.search(SongName, type="track", limit=10)
        song_results = raw_song_results['tracks']['items']
        #Re-instantiating the results frame and right column to clear the previous results
        self.Results.destroy()
        self.right_column.destroy()
        self.right_column = ctk.CTkFrame(self, width=500, corner_radius=0, fg_color='transparent')
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))
        self.right_column.grid_columnconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(1, weight=1)
        # Creating the results frame and displaying the results
        # If there are no relevant songs, display a separate window instead
        if len(song_results) == 0:
            self.Results = NoSearchResultsWindow(self.SongResults)
            self.Results.grid(row=1, column=0, sticky='nsw')
        else:
            self.Results = SearchResultsWindow(self.SongResults, song_results, self.SearchBar, self.right_column, 'song', self)
            self.Results.grid(row=1, column=0, sticky='nsw')

class AnalyseOneArtistWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.grid_rowconfigure(1, weight=1)
        
        self.left_column = LeftColumn(self)
        self.left_column.grid(row=1, column=1, sticky='nsew')
        
        self.search_frame = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.search_frame.grid(row=1, column=1, sticky='nsew')
        self.search_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=1)
        self.search_frame.grid_columnconfigure(6, weight=1)
        
        self.search_bar = ctk.CTkEntry(self.search_frame, placeholder_text="Artist Name", height=35)
        self.search_bar.grid(row=1, column=1, sticky='nsew', padx=10, pady=20, columnspan=5)
        self.search_button = ctk.CTkButton(self.search_frame, text="Search", width=30, height=35, corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : self.get_SearchBar())
        self.search_button.grid(row=1, column=6, sticky='nw', pady=(20, 0))
        
        self.artist_results = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.artist_results.grid(row=2, column=1, padx=(10, 0), pady=0, sticky="nsew", columnspan=2)
        
        self.results = ctk.CTkFrame(self.artist_results, fg_color='transparent')
        self.results.grid(row=1, column=0, sticky='nsew')
        
        self.right_column = RightColumn(self)
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))

    def get_SearchBar(self):
        artist_name = self.search_bar.get()
        if artist_name == '':
            return
        raw_artist_results = spotify_object.search(artist_name, type="artist", limit=10)
        artist_results = raw_artist_results['artists']['items']
        self.results.destroy()
        self.right_column.destroy()
        self.right_column = ctk.CTkFrame(self, width=500, corner_radius=0, fg_color='transparent')
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))
        self.right_column.grid_columnconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(1, weight=1)
        if len(artist_results) == 0:
            self.results = NoSearchResultsWindow(self.artist_results)
            self.results.grid(row=1, column=0, sticky='nsw')
        else:
            self.results = SearchResultsWindow(self.artist_results, artist_results, self.search_bar, self.right_column, 'artist', self)
            self.results.grid(row=1, column=0, sticky='nsw')

class AnalyseMultipleSongsWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.grid_rowconfigure(1, weight=1)
        self.chosen_songs_list = []
        self.chosen_songs_dictionary_list = []
        self.chosen_songs_row_index = 0
        
        self.left_column = LeftColumn(self)
        self.left_column.grid(row=1, column=1, sticky='nsew')
        
        self.search_frame = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.search_frame.grid(row=1, column=1, sticky='nsew')
        self.search_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=1)
        self.search_frame.grid_columnconfigure(6, weight=1)
        
        self.SearchBar = ctk.CTkEntry(self.search_frame, placeholder_text="Song Name", height=35)
        self.SearchBar.grid(row=1, column=1, sticky='nsew', padx=10, pady=20, columnspan=5)
        self.SearchButton = ctk.CTkButton(self.search_frame, text="Search", width=30, height=35, corner_radius=8, font=ctk.CTkFont(size=15), command= lambda : self.get_SearchBar())
        self.SearchButton.grid(row=1, column=6, sticky='nw', pady=(20, 0))
        
        self.SongResults = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.SongResults.grid(row=2, column=1, padx=(10, 0), pady=0, sticky="nsew", columnspan=2)
        
        self.Results = ctk.CTkFrame(self.SongResults, fg_color='transparent')
        self.Results.grid(row=1, column=0, sticky='nsew')
        
        self.right_column = RightColumn(self)
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))

    def get_SearchBar(self):
        SongName = self.SearchBar.get()
        if SongName == '':
            return
        raw_song_results = spotify_object.search(SongName, type="track", limit=10)
        song_results = raw_song_results['tracks']['items']
        self.Results.destroy()
        self.right_column.destroy()
        self.right_column = ctk.CTkFrame(self, width=500, corner_radius=0, fg_color='transparent')
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))
        self.right_column.grid_columnconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(1, weight=1)
        if len(song_results) == 0:
            self.Results = NoSearchResultsWindow(self.SongResults)
            self.Results.grid(row=1, column=0, sticky='nsw')
        else:
            self.Results = SearchResultsWindow(self.SongResults, song_results, self.SearchBar, self.right_column, 'multiplesongs', self)
            self.Results.grid(row=1, column=0, sticky='nsw')
        
    def add_song_to_list(self, song_id, song, frame):
        if len(self.chosen_songs_list) >= 5 or song_id in self.chosen_songs_list:
            return
        self.chosen_songs_list.append(song_id)
        self.chosen_songs_dictionary_list.append(song)   
        frame.configure(fg_color = 'transparent')
        chosen_song_frame = ctk.CTkFrame(frame, corner_radius=8)
        chosen_song_frame.grid(row=self.chosen_songs_row_index+1, column=1, pady=(10, 0), sticky='nsew')
        chosen_song_frame.grid_columnconfigure((1, 2), weight=1)
        printed_song_name = f'{song["name"]} by {song["artists"][0]["name"]}'
        if len(printed_song_name) > 45:
            printed_song_name = f'{printed_song_name[:42]}...'
        else: 
            printed_song_name = printed_song_name.ljust(45)
        song_name_label_frame = ctk.CTkFrame(chosen_song_frame, fg_color='transparent', corner_radius=8)
        song_name_label_frame.grid(row=1, column=1, padx=10, sticky='nsew')
        song_name_label = ctk.CTkLabel(song_name_label_frame, text=printed_song_name, fg_color='transparent')
        song_name_label.grid(row=1, column=1, sticky='w', pady=2)
        song_checkbox = ctk.CTkCheckBox(chosen_song_frame, text='', corner_radius=8, command=lambda : self.remove_item(chosen_song_frame, song_id))
        song_checkbox.grid(row=1, column=2, sticky='e', padx=(0, 20), pady=2)
        self.chosen_songs_row_index += 1

    def empty_list(self):
        self.chosen_songs_list.clear()
        self.chosen_songs_dictionary_list.clear()
        self.chosen_songs_row_index=0
        
    def remove_item(self, song_frame, songid):
        song_frame.destroy()
        self.chosen_songs_list = [d for d in self.chosen_songs_list if d != songid]
        #self.chosen_songs_list.remove(songid)
        self.chosen_songs_dictionary_list = [d for d in self.chosen_songs_dictionary_list if d.get("id") != songid]
        
    def create_selected_song_frames(self, frame):
        if len(self.chosen_songs_list) > 0:
            frame.configure(fg_color = 'transparent')
        self.chosen_songs_row_index = 0
        for i, chosen_song_dict in enumerate(self.chosen_songs_dictionary_list):
            chosen_song_frame = ctk.CTkFrame(frame, corner_radius=8)
            chosen_song_frame.grid(row=i+1, column=1, pady=(10, 0), sticky='nsew')
            chosen_song_frame.grid_columnconfigure((1, 2), weight=1)
            printed_song_name = f'{chosen_song_dict["name"]} by {chosen_song_dict["artists"][0]["name"]}'
            if len(printed_song_name) > 45:
                printed_song_name = f'{printed_song_name[:42]}...'
            else: 
                printed_song_name = printed_song_name.ljust(45)
            song_name_label_frame = ctk.CTkFrame(chosen_song_frame, fg_color='transparent', corner_radius=8)
            song_name_label_frame.grid(row=1, column=1, padx=10, sticky='nsew')
            song_name_label = ctk.CTkLabel(song_name_label_frame, text=printed_song_name, fg_color='transparent')
            song_name_label.grid(row=1, column=1, sticky='w', pady=2)
            song_checkbox = ctk.CTkCheckBox(chosen_song_frame, text='', corner_radius=8, command=lambda : self.remove_item(chosen_song_frame, chosen_song_dict['id']))
            song_checkbox.grid(row=1, column=2, sticky='e', padx=(0, 20), pady=2)
            self.chosen_songs_row_index += 1
            
    def create_radar_chart(self, frame):
        if len(self.chosen_songs_list) == 0:
            return
        song_audio_features = spotify_object.audio_features(self.chosen_songs_list)
        audio_features_list = ['Acousticness', 'Danceability', 'Energy', 'Valence']
        features_list = []
        for i, feature_set in enumerate(song_audio_features):
            features_list.append([feature_set['acousticness'], feature_set['danceability'], feature_set['energy'], feature_set['valence']])
            features_list[i] = [*features_list[i], features_list[i][0]]
        audio_features_list = [*audio_features_list, audio_features_list[0]]
        
        label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(audio_features_list))
        fig, ax = plt.subplots(figsize=(10,10), subplot_kw=dict(polar=True), facecolor='#2B2B2B')
        for feature_set in features_list:
            ax.plot(label_loc, feature_set, lw=2)
            ax.fill(label_loc, feature_set, alpha=0.3)
        ax.set_facecolor("#2B2B2B")
        lines, labels = plt.thetagrids(np.degrees(label_loc), labels=audio_features_list)
        ax.tick_params(axis='both', which='major', pad=30, labelsize=15)
        ax.set_ylim(0, 1)
        legends = []
        for i in range(len(song_audio_features)):
            song_name = self.chosen_songs_dictionary_list[i]['name']
            if len(song_name) > 20:
                song_name = f'{song_name[:17]}...'
                x_anchor = 1.6
                x_length = 450
            else:
                x_anchor = 1.4
                x_length = 400
            legends.append(Patch(facecolor=f'C{i}', alpha=0.5, label=song_name)) 
        ax.legend(handles=legends,
            bbox_to_anchor=(x_anchor, 0.2), fontsize=20, 
            frameon=True, labelcolor = 'white', facecolor='None')
        edge_color = (1, 1, 1, 1) 
        ax.spines['polar'].set_color(edge_color) 
        ax.tick_params(axis='both', colors='white')
        ax.grid(color='white', alpha=0.5)
        plt.savefig('images/foundimages/analysemultiplesongs/radargraph.png', dpi=300, bbox_inches='tight')
        
        self.radar_graph_label_frame = ctk.CTkFrame(frame, corner_radius=8)
        self.radar_graph_label_frame.grid(row=8, column=1, sticky='nsew')
        self.radar_graph_label_frame.grid_columnconfigure(1, weight=1)
        self.radar_graph_label = ctk.CTkLabel(self.radar_graph_label_frame, text='Radar Graph', corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent')
        self.radar_graph_label.grid(row=1, column=1, pady=(2, 0), sticky='nsew')
        self.radar_graph_image = ctk.CTkImage(light_image=Image.open(f'images/foundimages/analysemultiplesongs/radargraph.png'), size=(x_length, 295))
        self.radar_graph = ctk.CTkLabel(self.radar_graph_label_frame, image=self.radar_graph_image, text='')
        self.radar_graph.grid(row=2, column=1, sticky='nsew', padx=10, pady=10)

class AnalyseOnePlaylistWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.grid_rowconfigure(1, weight=1)
        
        self.left_column = LeftColumn(self)
        self.left_column.grid(row=1, column=1, sticky='nsew')
        self.left_column.grid_columnconfigure(1, weight=1)
        
        self.right_column = RightColumn(self)
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))
        
        self.search_frame = ctk.CTkFrame(self.left_column, corner_radius=8)
        self.search_frame.grid(row=1, column=1, sticky='nsw', padx=(10, 0), pady=20)
        self.search_frame.grid_columnconfigure(1, weight=1)
        
        self.user_playlists_text = ctk.CTkLabel(self.search_frame, text='User Playlists', fg_color='transparent', height=35, corner_radius=8, width=480)
        self.user_playlists_text.grid(row=1, column=1, sticky='nsew', pady=3)
        
        self.playlist_results = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.playlist_results.grid(row=2, column=1, padx=(10, 0), pady=0, sticky="nsw")
        self.playlist_results.grid_columnconfigure(1, weight=1)
        
        self.get_playlists()
        
        if len(self.playlists) > 0:
            self.user_playlists_frame = UserPlaylistsFrame(self.playlist_results, self.playlists, self.right_column, 'analyse')
            self.user_playlists_frame.grid(row=1, column=1, sticky='nsew')
        else:
            self.no_results_frame = NoResultsFrame(self.playlist_results)
            self.no_results_frame.grid(row=1, column=1, sticky='nsew')
        
    def get_playlists(self):
        self.loading_popup = PopupWindow(self, 'Loading Application')
        #Make a call to the Spotify AI to retrieve the first 50 playlist of the user 
        self.raw_playlists = spotify_object.current_user_playlists(limit=50)
        self.playlists = self.raw_playlists["items"]

        #Loop to ensure that all user playlists are obtained if they have more than 50 playlists
        self.offset = 50
        while self.raw_playlists['next']:
            self.raw_playlists = spotify_object.current_user_playlists(limit=50, offset=self.offset)
            self.extra_playlists = self.raw_playlists["items"]
            #Decreases the total playists remaining and increases the offset used in the Spotify API csll
            self.offset += 50
            #Adds all extra playlists to the list of playlists
            for playlist in self.extra_playlists:
                self.playlists.append(playlist)
        self.loading_popup.withdraw()
        return self.playlists

class PlaylistRecommendationWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.grid_rowconfigure(1, weight=1)
        
        self.left_column = LeftColumn(self)
        self.left_column.grid(row=1, column=1, sticky='nsew')
        self.left_column.grid_columnconfigure(1, weight=1)
        
        self.right_column = RightColumn(self)
        self.right_column.grid(row=1, column=2, sticky='nsew', padx=(0, 10))
        
        self.search_frame = ctk.CTkFrame(self.left_column, corner_radius=8)
        self.search_frame.grid(row=1, column=1, sticky='nsw', padx=(10, 0), pady=20)
        self.search_frame.grid_columnconfigure(1, weight=1)
        
        self.user_playlists_text = ctk.CTkLabel(self.search_frame, text='User Playlists', fg_color='transparent', height=35, corner_radius=8, width=480)
        self.user_playlists_text.grid(row=1, column=1, sticky='nsew', pady=3)
        
        self.playlist_results = ctk.CTkFrame(self.left_column, fg_color='transparent')
        self.playlist_results.grid(row=2, column=1, padx=(10, 0), pady=0, sticky="nsw")
        self.playlist_results.grid_columnconfigure(1, weight=1)
        
        self.get_playlists()
        
        if len(self.playlists) > 0:
            self.user_playlists_frame = UserPlaylistsFrame(self.playlist_results, self.playlists, self.right_column, 'recommend')
            self.user_playlists_frame.grid(row=1, column=1, sticky='nsew')
        else:
            self.no_results_frame = NoResultsFrame(self.playlist_results)
            self.no_results_frame.grid(row=1, column=1, sticky='nsew')
        
    def get_playlists(self):
        self.loading_popup = PopupWindow(self, 'Loading Application')
        #Make a call to the Spotify AI to retrieve the first 50 playlist of the user 
        self.raw_playlists = spotify_object.current_user_playlists(limit=50)
        self.playlists = self.raw_playlists["items"]

        #Loop to ensure that all user playlists are obtained if they have more than 50 playlists
        self.offset = 50
        while self.raw_playlists['next']:
            self.raw_playlists = spotify_object.current_user_playlists(limit=50, offset=self.offset)
            self.extra_playlists = self.raw_playlists["items"]
            #Decreases the total playists remaining and increases the offset used in the Spotify API csll
            self.offset += 50
            #Adds all extra playlists to the list of playlists
            for playlist in self.extra_playlists:
                self.playlists.append(playlist)
        self.loading_popup.withdraw()
        return self.playlists

class UserPlaylistsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, userplaylists, rightcolumn, type):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)
        self.configure(fg_color='transparent', width=460, height=530, corner_radius=8)
        self.userplaylists = userplaylists
        self.rightcolumn = rightcolumn
        self.type = type
        self.playlist_checkboxes = [] 

        self.no_playlists_popup = None

        for i, playlist in enumerate(self.userplaylists):
            checkbox_var = ctk.BooleanVar()
            playlist_frame = ctk.CTkFrame(self, corner_radius=8)
            playlist_frame.grid(row=i+1, column=1, pady=(0, 10), sticky='nsew')
            playlist_frame.grid_columnconfigure(3, weight=1)
            
            image_location = f'images/foundimages/analyseoneplaylist/image{i}.png'
            images_list = playlist['images']
            if len(images_list) > 0:
                image_url = images_list[0]['url']
                urllib.request.urlretrieve(image_url, image_location)
            else:
                image_location='images/noimagefound.png'
            
            printed_playlist_name = playlist['name']
            if len(printed_playlist_name) > 40:
                printed_playlist_name = f'{printed_playlist_name[:37]}...'
            else:
                printed_playlist_name = printed_playlist_name.ljust(40)

            playlist_image = ctk.CTkImage(light_image=Image.open(image_location), size=(40, 40))
            image_label = ctk.CTkLabel(playlist_frame, image=playlist_image, text="", corner_radius=20)
            image_label.grid(row=1, column=0, pady=3, padx=(0, 10), sticky='w')
            playlist_title = ctk.CTkLabel(playlist_frame, text=printed_playlist_name, fg_color="transparent")
            playlist_title.grid(row=1, column=2, sticky='w')
            playlist_check_box = ctk.CTkCheckBox(playlist_frame, text='', variable=checkbox_var, command=lambda index=i: self.on_checkbox_clicked(index))
            playlist_check_box.grid(row=1, column=3, sticky='e')
            self.playlist_checkboxes.append(checkbox_var)

        self.playlist_submit_button = ctk.CTkButton(master, text='Analyse', corner_radius=8, height=40, font=ctk.CTkFont(size=15), command=lambda: self.analyse_item())
        self.playlist_submit_button.grid(row=2, column=1, sticky='nsew', pady=(5, 0))
        
    def on_checkbox_clicked(self, index):
        for i, checkbox_var in enumerate(self.playlist_checkboxes):
            if i != index:
                checkbox_var.set(False)
        
    def analyse_item(self):
        playlist = None
        playlist_index = 0
        for i, checkbox_var in enumerate(self.playlist_checkboxes):
            if checkbox_var.get():
                playlist = self.userplaylists[i]
                playlist_index = i
                break
        
        if playlist['tracks']['total'] > 15:
            if self.type == 'analyse':
                self.analysed_song_window = AnalysedPlaylistWindow(self.rightcolumn, playlist, playlist_index)
                self.analysed_song_window.grid(row=1, column=1, sticky='nwe') 
            else:
                self.recommendations_frame = RecommendationsFrame(self.rightcolumn, playlist, playlist_index)
                self.recommendations_frame.grid(row=1, column=1, sticky='nwe')
        else:
            if self.no_playlists_popup is None or not self.no_playlists_popup.winfo_exists():
                self.no_playlists_popup = PopupWindow(self, 'This playlist has less than 15 songs and cannot be analysed.')
                self.no_playlists_popup.after(100, self.no_playlists_popup.lift)
            else:
                self.no_playlists_popup.focus()
                self.no_playlists_popup.after(100, self.no_playlists_popup.lift)
                return

class RecommendationsFrame(ctk.CTkFrame):
    def __init__(self, master, playlist, playlist_index):
        super().__init__(master)
        self.configure(fg_color='transparent')
        self.playlist = playlist
        self.playlist_index = playlist_index 
        
        # Ensures that all displayed playlist details are within a maximum character limit of 65 characters for the playlist name and 120 characters for the playlist description
        printable_playlist_name = f"{self.playlist['name'][:65]}..." if len(self.playlist['name']) > 68 else self.playlist['name']
        playlist_description = f"{self.playlist['description'][:117]}..." if len(self.playlist['description']) > 120 else self.playlist['description']
        # Indicates whether the playlist is collaborative or not by checking whether the collaobrative key value in the playlist dictionary is true or not 
        playlist_collaborative_status = '(Collaborative)' if self.playlist['collaborative'] else '(Not Collaborative)'
        printable_playlist_information = f'{playlist_description} {playlist_collaborative_status}'
        # Sets the image url to the correct image in the playlist images list using the playlist_index parameter if there is at least one image url in the playlist dictionary, otherwise sets the image url to the no image found image
        image_url = f'images/foundimages/analyseoneplaylist/image{playlist_index}.png' if len(self.playlist['images']) > 0 else 'images/noimagefound.png'

        # Defines the grid layout of the frame
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((1, 2, 3, 4), weight=1)
        
        # Defines the popup window as none originally to make sure no duplicates are created
        self.success_popup = None
        
        # Defines the frame that will contain the playlist cover image and the playlist name and description
        self.cover_frame = CoverFrame(self, image_url, printable_playlist_name, printable_playlist_information)
        self.cover_frame.grid(row=1, column=1, padx=(0, 10), pady=(20, 11), sticky='new')
        
        # Defines the frame that will contain the entry box for the amount of songs to be recommended
        self.input_amount_of_songs_row = ctk.CTkFrame(self, corner_radius=8, fg_color='transparent')
        self.input_amount_of_songs_row.grid(row=2, column=1, padx=(0, 10), pady=(0, 11), sticky='new')
        self.input_amount_of_songs_row.grid_columnconfigure((1,2,3), weight=1)
        self.input_amount_of_songs_row.grid_rowconfigure(1, weight=1)
        
        self.amount_title_frame = ctk.CTkFrame(self.input_amount_of_songs_row, corner_radius=8)
        self.amount_title_frame.grid(row=1, column=1, sticky='new', columnspan=2, padx=(0, 10))
        self.amount_title_frame.grid_columnconfigure(1, weight=1)
        self.amount_title_frame.grid_rowconfigure(1, weight=1)
        
        self.amount_title = ctk.CTkLabel(self.amount_title_frame, text='Amount of Songs to Recommend (1-100):', fg_color='transparent')
        self.amount_title.grid(row=1, column=1, sticky='new', pady=4)
        
        # Defines the entry box for the amount of songs to be recommended and assigns it a validation command to ensure that only numbers are entered
        self.validate_amount_input_command = self.register(self.validate_amount_input)
        self.amount_entry = ctk.CTkEntry(self.input_amount_of_songs_row, corner_radius=8, fg_color='transparent', height=35, validate="key", validatecommand=(self.validate_amount_input_command, "%P"))
        self.amount_entry.grid(row=1, column=3, sticky='new')
        
        # Defines the frame that will contain the playlist's information
        self.playlist_information_frame = ctk.CTkFrame(self, corner_radius=8, fg_color='transparent')
        self.playlist_information_frame.grid(row=3, column=1, padx=(0, 10), pady=(0, 11), sticky='new')
        self.playlist_information_frame.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7), weight=1)
        self.playlist_information_frame.grid_columnconfigure(1, weight=1)
        
        self.playlist_details_title_frame = ctk.CTkFrame(self.playlist_information_frame, corner_radius=8)
        self.playlist_details_title_frame.grid(row=1, column=1, sticky='new', columnspan=2)
        self.playlist_details_title_frame.grid_columnconfigure(1, weight=1)
        self.playlist_details_title = ctk.CTkLabel(self.playlist_details_title_frame, text='Playlist Details:', fg_color='transparent')
        self.playlist_details_title.grid(row=1, column=1, sticky='new', pady=4)
        
        self.playlist_name_title_frame = ctk.CTkFrame(self.playlist_information_frame, corner_radius=8, fg_color='transparent')
        self.playlist_name_title_frame.grid(row=2, column=1, sticky='new')
        self.playlist_name_title_frame.grid_columnconfigure(1, weight=1)
        self.playlist_name_title = ctk.CTkLabel(self.playlist_name_title_frame, text='Name: (Leave empty for default)', fg_color='transparent')
        self.playlist_name_title.grid(row=1, column=1, sticky='new', pady=4)
        
        # Defines the entry box for the playlist name and assigns it a validation command to ensure that the name is not longer than 100 characters
        self.validate_name_input_command = self.register(self.validate_name_input)
        self.playlist_name_entry = ctk.CTkEntry(self.playlist_information_frame, corner_radius=8, height=35, fg_color='transparent', placeholder_text="Playlist Name (Max 100 Characters)", validate="key", validatecommand=(self.validate_name_input_command, "%P"))
        self.playlist_name_entry.grid(row=4, column=1, sticky='new')
        
        self.playlist_description_title_frame = ctk.CTkFrame(self.playlist_information_frame, corner_radius=8, fg_color='transparent')
        self.playlist_description_title_frame.grid(row=5, column=1, sticky='new')
        self.playlist_description_title_frame.grid_columnconfigure(1, weight=1)
        self.playlist_description_title_frame = ctk.CTkLabel(self.playlist_description_title_frame, text='Descrption: (Leave empty for default)', fg_color='transparent')
        self.playlist_description_title_frame.grid(row=1, column=1, sticky='new', pady=4)
        
        # Defines the entry box for the playlist description and assigns it a validation command to ensure that the description is not longer than 300 characters
        self.validate_description_input_command = self.register(self.validate_description_input)
        self.playlist_description_entry = ctk.CTkEntry(self.playlist_information_frame, corner_radius=8,fg_color='transparent', height=35, placeholder_text="Playlist Description (Max 300 Characters)", validate="key", validatecommand=(self.validate_description_input_command, "%P"))
        self.playlist_description_entry.grid(row=6, column=1, sticky='new')

        # Defines the submit button and assigns it a command to call the recommend_song function
        self.submit_button = ctk.CTkButton(self.playlist_information_frame, text='Submit', corner_radius=8, height=35, command= lambda: self.recommend_song())
        self.submit_button.grid(row=7, column=1, sticky='new', pady=(12, 0))

    # Defines the function that will validate the amount of songs input
    def validate_amount_input(self, text):
        if text == "":
            return True
        return text.isdigit() and 1 <= int(text) <= 100
    
    # Defines the function that will validate the playlist name input
    def validate_name_input(self, text):
        if len(text) > 100:
            return False
        
    # Defines the function that will validate the playlist description input
    def validate_description_input(self, text):
        if len(text) > 300:
            return False
        
    # Defines the function that will recommend the songs
    def recommend_song(self):
        # If statement to check if the user has entered a number of songs to recommend
        number_of_songs = self.amount_entry.get()
        if number_of_songs == "":
            self.error_popup = PopupWindow(self, "Please enter a number between 1 and 100") 
            self.error_popup.after(100, self.error_popup.lift)
            return
        else: 
            number_of_songs = int(number_of_songs)
        # Obtains the user entered playlist name and description
        playlist_name = self.playlist_name_entry.get()
        playlist_description = self.playlist_description_entry.get()

        # Obtains the playlist's ID and makes a call to the Spotify API to retrieve the first 50 items in the playlist
        playlist_id = self.playlist['id']
        playlist_items_response = spotify_object.playlist_items(playlist_id, limit=50)
        
        # Adds the first 50 songs id's to a list
        playlist_songs_ids = []
        for song in playlist_items_response["items"]:
            playlist_songs_ids.append(song["track"]["id"])
            print(f"Retrieved {len(playlist_songs_ids)} Song Ids")
        # While loop to retrieve all of the songs in the playlist by checking whether there is a next page of songs
        while playlist_items_response["next"]:
            playlist_items_response = spotify_object.next(playlist_items_response)
            for song in playlist_items_response["items"]:
                playlist_songs_ids.append(song["track"]["id"])
                print(f"Retrieved {len(playlist_songs_ids)} Song Ids")

        # Splits the list of song id's into lists of 50 to make calls to the Spotify API to retrieve the songs
        song_id_lists = [playlist_songs_ids[x:x+50] for x in range(0, len(playlist_songs_ids), 50)]
        # Retrives the song information and song audio features for each song in the playlist by iterating through the list of song id lists
        playlist_songs = []
        playlist_songs_audio_features = []
        for song_id_list in song_id_lists:
            songs = spotify_object.tracks(song_id_list)
            songs_audio_features = spotify_object.audio_features(song_id_list)
            playlist_songs.extend(songs["tracks"])
            playlist_songs_audio_features.extend(songs_audio_features)
            print(f"Retrieved {len(playlist_songs)} Songs")

        # Creates a dictionary of the audio features required and adds each audio feature value to the list within the dictionary
        audio_features_values_dict = {"energy": [], "speechiness": [],  "danceability": [], "valence": []}
        for audio_features in playlist_songs_audio_features:
            audio_features_values_dict["danceability"].append(audio_features["danceability"])
            audio_features_values_dict["energy"].append(audio_features["energy"])
            audio_features_values_dict["speechiness"].append(audio_features["speechiness"])
            audio_features_values_dict["valence"].append(audio_features["valence"])
        # Creates a dictionary of the processed audio features and adds the average, standard deviation, min and max of each audio feature to the dictionary
        processed_audio_features_values_dict = {"danceability": {}, "energy": {}, "speechiness": {}, "valence": {}}
        for audio_feature in processed_audio_features_values_dict:
            processed_audio_features_values_dict[audio_feature]["average"] = sum(audio_features_values_dict[audio_feature]) / len(audio_features_values_dict[audio_feature])
            processed_audio_features_values_dict[audio_feature]["standard_deviation"] = statistics.stdev(audio_features_values_dict[audio_feature])
            calculated_min_audio_feature = processed_audio_features_values_dict[audio_feature]["average"] - processed_audio_features_values_dict[audio_feature]["standard_deviation"]
            '''.
                The min and max are calculated under the assumption that the values of each song follow a normal distribution
                The min is calculated by subtracting the standard deviation from the average
                The max is calculated by adding the standard deviation to the average
                Therefore the recommended songs should fall within the middle 68% of the normal distribution values
            '''
            processed_audio_features_values_dict[audio_feature]["min"] = calculated_min_audio_feature if calculated_min_audio_feature > 0 else 0
            processed_audio_features_values_dict[audio_feature]["max"] = processed_audio_features_values_dict[audio_feature]["average"] + processed_audio_features_values_dict[audio_feature]["standard_deviation"]

        # Obtains all artists in the playlist and creates a dictionary of the artists and the number of times they appear in the playlist
        playlist_artists_dict = {}
        playlist_artists_ids = []
        playlist_artists_ids_dict = {}
        for song in playlist_songs:
            for artist in song["artists"]:
                if artist["name"] not in playlist_artists_dict:
                    playlist_artists_dict[f"{artist['name']}"] = 1
                    playlist_artists_ids_dict[f"{artist['id']}"] = 1
                    playlist_artists_ids.append(artist["id"])
                else:
                    playlist_artists_dict[f"{artist['name']}"] += 1
                    playlist_artists_ids_dict[f"{artist['id']}"] += 1

        # Obtains the two most popular artists in the playlist
        popular_artists = []
        popular_artists_ids = []
        for i in range(1, 3):
            popular_artists.append(sorted(playlist_artists_dict, key=playlist_artists_dict.get)[-i])
            popular_artists_ids.append(sorted(playlist_artists_ids_dict, key=playlist_artists_ids_dict.get)[-i])

        # Splits the list of artist id's into lists of 50 to make calls to the Spotify API to retrieve the artists' information by iterating through the list of artist id lists
        artist_id_lists = [playlist_artists_ids[x:x+50] for x in range(0, len(playlist_artists_ids), 50)]
        playlist_artists = []
        playlist_genres_dict = {}
        for artist_id_list in artist_id_lists:
            artists = spotify_object.artists(artist_id_list)
            playlist_artists.extend(artists["artists"])
            print(f"Retrieved {len(playlist_artists)} Artists")
        # Creates a dictionary of the genres and the number of times they appear in the playlist
            for artist in artists["artists"]:
                for genre in artist["genres"]:
                    if genre not in playlist_genres_dict:
                        playlist_genres_dict[genre] = 1
                    else:
                        playlist_genres_dict[genre] += 1
        # Obtains the two most popular genres in the playlist
        popular_genres = []
        for i in range(1, 3):
            popular_genres.append(sorted(playlist_genres_dict, key=playlist_genres_dict.get)[-i])

        # Obtains the user's top songs and checks whether a song in the playlist features in their top songs to obtain a seed track for the recommendation
        user_top_songs = spotify_object.current_user_top_tracks(limit=50)
        playlist_top_songs = []
        for user_top_song in user_top_songs["items"]:
            if user_top_song["id"] in playlist_songs_ids:
                if len(playlist_top_songs) < 1:
                    playlist_top_songs.append(user_top_song["id"])
        if len(playlist_top_songs) == 0:
            playlist_top_songs.append(playlist_songs_ids[-i])
        print('Obtained Top Song')

        # Makes a call to the Spotify API to obtain the recommended songs
        recommended_songs = spotify_object.recommendations(seed_artists=popular_artists_ids, seed_genres=popular_genres, seed_tracks=playlist_top_songs,
                                                        min_danceability=processed_audio_features_values_dict["danceability"]["min"],
                                                        max_danceability=processed_audio_features_values_dict["danceability"]["max"],
                                                        target_danceability=processed_audio_features_values_dict["danceability"]["average"],
                                                        min_energy=processed_audio_features_values_dict["energy"]["min"],
                                                        max_energy=processed_audio_features_values_dict["energy"]["max"],
                                                        target_energy=processed_audio_features_values_dict["energy"]["average"],
                                                        min_speechiness=processed_audio_features_values_dict["speechiness"]["min"],
                                                        max_speechiness=processed_audio_features_values_dict["speechiness"]["max"],
                                                        target_speechiness=processed_audio_features_values_dict["speechiness"]["average"],
                                                        min_valence=processed_audio_features_values_dict["valence"]["min"],
                                                        max_valence=processed_audio_features_values_dict["valence"]["max"],
                                                        target_valence=processed_audio_features_values_dict["valence"]["average"],
                                                        limit=number_of_songs)
        
        # Checks whether the recommended songs are less than the number of songs to add to the playlist
        if len(recommended_songs["tracks"]) < number_of_songs:
            recommended_songs_uris = []
            for recommended_song in recommended_songs["tracks"]:
                recommended_songs_uris.append(recommended_song["uri"])
                popup_message = f'Only {len(recommended_songs_uris)} songs were recommended into a new playlist in your library. Try again with a bigger playlist or a smaller number of songs to add.'
        else:
            # Checks for the amount of duplicate songs in the recommended songs
            recommended_songs_uris = []
            recommended_songs_names = []
            for recommended_song in recommended_songs["tracks"]: 
                if (recommended_song["id"] not in playlist_songs_ids) and (recommended_song["id"] not in recommended_songs_uris):
                        recommended_songs_uris.append(recommended_song["uri"])
                        recommended_songs_names.append(f'{recommended_song["name"]} by {recommended_song["artists"][0]["name"]}')
            amount_of_songs_to_add = number_of_songs - len(recommended_songs_uris)
            loop_count = 0
            # If there are duplicate songs, the function will make more calls to the Spotify API to obtain more recommended songs
            while amount_of_songs_to_add > 0:
                recommended_songs = spotify_object.recommendations(seed_artists=popular_artists_ids, seed_genres=popular_genres, seed_tracks=playlist_top_songs,
                                                            min_danceability=processed_audio_features_values_dict["danceability"]["min"],
                                                            max_danceability=processed_audio_features_values_dict["danceability"]["max"],
                                                            target_danceability=processed_audio_features_values_dict["danceability"]["average"],
                                                            min_energy=processed_audio_features_values_dict["energy"]["min"],
                                                            max_energy=processed_audio_features_values_dict["energy"]["max"],
                                                            target_energy=processed_audio_features_values_dict["energy"]["average"],
                                                            min_speechiness=processed_audio_features_values_dict["speechiness"]["min"],
                                                            max_speechiness=processed_audio_features_values_dict["speechiness"]["max"],
                                                            target_speechiness=processed_audio_features_values_dict["speechiness"]["average"],
                                                            min_valence=processed_audio_features_values_dict["valence"]["min"],
                                                            max_valence=processed_audio_features_values_dict["valence"]["max"],
                                                            target_valence=processed_audio_features_values_dict["valence"]["average"],
                                                            limit = 100)
                for recommended_song in recommended_songs["tracks"]: 
                    if (recommended_song["id"] not in playlist_songs_ids) and (recommended_song["id"] not in recommended_songs_uris):
                        recommended_songs_uris.append(recommended_song["uri"])
                        amount_of_songs_to_add -= 1
                        if amount_of_songs_to_add == 0:
                            loop_count += 1
                            break
                loop_count += 1
            popup_message = f'Your playlist has been created!'

        # Defines the default playlist name and description
        default_playlist_name = f'SpotiMetrics Song Recommendations - {self.playlist["name"]}'
        default_playlist_description = f'SpotiMetrics Song Recommendations based on the {self.playlist["name"]} playlist. This playlist was created using SpotiMetrics'
        # Sets the playlist name and description to the default if the user does not enter a name or description
        if playlist_name == "":
            playlist_name = default_playlist_name
        if playlist_description == "":
            playlist_description = default_playlist_description
        # Creates the playlist and adds the recommended songs to the playlist
        new_playlist = spotify_object.user_playlist_create(user=user["id"], name=(playlist_name), description=(playlist_description))
        add_playlist_songs = spotify_object.user_playlist_add_tracks(user=user["id"], playlist_id=new_playlist["id"], tracks=recommended_songs_uris)

        # Creates a popup window to notify the user that the playlist has been created
        if self.success_popup is None or not self.success_popup.winfo_exists():
            self.success_popup = PopupWindow(self, popup_message)
            self.success_popup.after(20, self.success_popup.lift)
        else:
            self.success_popup.after(20, self.success_popup.lift)

class AnalysedPlaylistWindow(ctk.CTkFrame):
    def __init__(self, master, playlist, playlist_index):
        super().__init__(master)
        self.configure(fg_color='transparent')
        self.playlist = playlist
        self.playlist_index = playlist_index 
        
        self.create_loading_popup()

        printable_playlist_name = f"{self.playlist['name'][:65]}..." if len(self.playlist['name']) > 68 else self.playlist['name']
        playlist_description = f"{self.playlist['description'][:117]}..." if len(self.playlist['description']) > 120 else self.playlist['description']
        playlist_collaborative_status = '(Collaborative)' if self.playlist['collaborative'] else '(Not Collaborative)'
        printable_playlist_information = f'{playlist_description} {playlist_collaborative_status}'
        image_url = f'images/foundimages/analyseoneplaylist/image{playlist_index}.png' if len(self.playlist['images']) > 0 else 'images/noimagefound.png'
        
        printable_item_count = f"Items: {self.playlist['tracks']['total']}"
        printable_status = f"Status: {'Public' if self.playlist['public'] else 'Private'}"
        
        playlist_items_response = spotify_object.playlist_items(self.playlist['id'], limit=50)
        playlist_songs_ids = []
        
        for song in playlist_items_response["items"]:
            playlist_songs_ids.append(song["track"]["id"])
            print(f"Retrieved {len(playlist_songs_ids)} Song Ids")
        while playlist_items_response["next"]:
            playlist_items_response = spotify_object.next(playlist_items_response)
            for song in playlist_items_response["items"]:
                playlist_songs_ids.append(song["track"]["id"])
                print(f"Retrieved {len(playlist_songs_ids)} Song Ids")

        song_id_lists = [playlist_songs_ids[x:x+50] for x in range(0, len(playlist_songs_ids), 50)]
        playlist_songs = []
        playlist_songs_audio_features = []
        for song_id_list in song_id_lists:
            songs = spotify_object.tracks(song_id_list)
            songs_audio_features = spotify_object.audio_features(song_id_list)
            playlist_songs.extend(songs["tracks"])
            playlist_songs_audio_features.extend(songs_audio_features)
            print(f"Retrieved {len(playlist_songs)} Songs")

        audio_features_values_dict = {"energy": [], "speechiness": [],  "danceability": [], "valence": []}
        for audio_features in playlist_songs_audio_features:
            audio_features_values_dict["danceability"].append(audio_features["danceability"])
            audio_features_values_dict["energy"].append(audio_features["energy"])
            audio_features_values_dict["speechiness"].append(audio_features["speechiness"])
            audio_features_values_dict["valence"].append(audio_features["valence"])
        processed_audio_features_values_dict = {"danceability": {}, "energy": {}, "speechiness": {}, "valence": {}}
        for audio_feature in processed_audio_features_values_dict:
            processed_audio_features_values_dict[audio_feature]["average"] = sum(audio_features_values_dict[audio_feature]) / len(audio_features_values_dict[audio_feature])

        audio_features_row_one = [[processed_audio_features_values_dict['speechiness']["average"], processed_audio_features_values_dict['danceability']["average"]], ['Average Speechiness', 'Average Danceability']]
        audio_features_row_two = [[processed_audio_features_values_dict['energy']["average"], processed_audio_features_values_dict['valence']["average"]], ['Average Energy', 'Average Happiness']]
        audio_feature_rows = [audio_features_row_one, audio_features_row_two]

        playlist_artists_dict = {}
        playlist_artists_ids = []
        playlist_artists_ids_dict = {}
        for song in playlist_songs:
            for artist in song["artists"]:
                if artist["name"] not in playlist_artists_dict:
                    playlist_artists_dict[f"{artist['name']}"] = 1
                    playlist_artists_ids_dict[f"{artist['id']}"] = 1
                    playlist_artists_ids.append(artist["id"])
                else:
                    playlist_artists_dict[f"{artist['name']}"] += 1
                    playlist_artists_ids_dict[f"{artist['id']}"] += 1

        popular_artists = []
        popular_artists_ids = []
        for i in range(1, 6):
            popular_artists.append(f'{i}. {sorted(playlist_artists_dict, key=playlist_artists_dict.get)[-i]} - {playlist_artists_dict[sorted(playlist_artists_dict, key=playlist_artists_dict.get)[-i]]} Songs\n')
            popular_artists_ids.append(sorted(playlist_artists_ids_dict, key=playlist_artists_ids_dict.get)[-i])

        artist_id_lists = [playlist_artists_ids[x:x+50] for x in range(0, len(playlist_artists_ids), 50)]
        playlist_artists = []
        playlist_genres_dict = {}
        for artist_id_list in artist_id_lists:
            artists = spotify_object.artists(artist_id_list)
            playlist_artists.extend(artists["artists"])
            print(f"Retrieved {len(playlist_artists)} Artists")
            for artist in artists["artists"]:
                for genre in artist["genres"]:
                    if genre not in playlist_genres_dict:
                        playlist_genres_dict[genre] = 1
                    else:
                        playlist_genres_dict[genre] += 1
        popular_genres = []
        for i in range(1, 6):
            popular_genres.append(f'{i} {sorted(playlist_genres_dict, key=playlist_genres_dict.get)[-i].capitalize()} - {playlist_genres_dict[sorted(playlist_genres_dict, key=playlist_genres_dict.get)[-i]]} Songs\n')
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((1, 2, 3, 4), weight=1)
        
        self.cover_frame = CoverFrame(self, image_url, printable_playlist_name, printable_playlist_information)
        self.cover_frame.grid(row=1, column=1, padx=(0, 10), pady=(20, 0), sticky='new')
        
        self.playlist_details_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.playlist_details_frame.grid(row=2, column=1, padx=(0, 10), pady=(0, 11), sticky='nsew')
        self.playlist_details_frame.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.playlist_details_frame.grid_rowconfigure(1, weight=1)
        
        self.item_count_frame = InformationLabelFrame(self.playlist_details_frame, printable_item_count)
        self.item_count_frame.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky='nsew')
        
        self.status_frame = InformationLabelFrame(self.playlist_details_frame, printable_status)
        self.status_frame.grid(row=1, column=2, pady=(10, 0), sticky='nsew')
        
        self.textboxes_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.textboxes_frame.grid(row=3, column=1, padx=(0, 10), pady=(0, 11), sticky='nsew')
        self.textboxes_frame.grid_columnconfigure(1, weight=1)
        self.textboxes_frame.grid_rowconfigure((1, 2), weight=1)
        
        self.top_artists_textbox = ctk.CTkTextbox(self.textboxes_frame, corner_radius=8, height=135)
        self.top_artists_textbox.grid(row=1, column=1, sticky='nsew', pady=(0, 11))
        self.top_artists_textbox.insert('0.0', 'Top Artists: \n\n' + ''.join(popular_artists))
        self.top_artists_textbox.configure(state='disabled')
        
        self.top_genres_textbox = ctk.CTkTextbox(self.textboxes_frame, corner_radius=8, height=135)
        self.top_genres_textbox.grid(row=2, column=1, sticky='nsew')
        self.top_genres_textbox.insert('0.0', 'Top Genres: \n\n' + ''.join(popular_genres))
        self.top_genres_textbox.configure(state='disabled')
        
        self.playlist_audio_features_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.playlist_audio_features_frame.grid(row=4, column=1, padx=(0, 10), sticky='nsew')
        self.playlist_audio_features_frame.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.playlist_audio_features_frame.grid_rowconfigure((1, 2), weight=1)
        
        for i, playlist_audio_feature_row in enumerate(audio_feature_rows):
            self.playlist_audio_feature_frame = InformationSliderFrame(self.playlist_audio_features_frame, playlist_audio_feature_row[1][0], playlist_audio_feature_row[0][0])
            self.playlist_audio_feature_frame.grid(row=i+1, column=1, pady=(0, 10), padx=(0, 10), sticky='nsew')
            
            self.playlist_audio_feature_frame = InformationSliderFrame(self.playlist_audio_features_frame, playlist_audio_feature_row[1][1], playlist_audio_feature_row[0][1])
            self.playlist_audio_feature_frame.grid(row=i+1, column=2, pady=(0, 10), sticky='nsew')
            
        self.delete_loading_popup()
            
    def create_loading_popup(self):
        self.loading_popup = PopupWindow(self, 'Analysing Playlist...')
        self.loading_popup.after(20, self.loading_popup.lift)
    
    def delete_loading_popup(self):
        self.loading_popup.destroy()

class NoSearchResultsWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color='transparent')
        
        self.SongsHeading = ctk.CTkLabel(self, text="No Results", font=ctk.CTkFont(size=20))
        self.SongsHeading.grid(row=1, column=1, sticky="nsew")

class SearchResultsWindow(ctk.CTkFrame):
    def __init__(self, master, items, searchbar, rightcolumn, type, parent):
        super().__init__(master)
        self.items = items
        self.searchbar = searchbar
        self.rightcolumn = rightcolumn
        self.ItemCheckBoxes = []
        self.configure(height=720, fg_color='transparent')
        self.grid_columnconfigure((1, 2), weight=1)
        self.type = type
        
        if self.type == 'multiplesongs':
            self.button_text = 'Add'
        else:
            self.button_text = 'Analyse'

        self.items_results_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.items_results_frame.grid(row=1, column=1, columnspan=2)
        self.items_results_frame.grid_columnconfigure(1, weight=1)
        
        if self.type == 'song':
            image_folder = 'analyseonesong' 
        elif self.type == 'multiplesongs':
            image_folder = 'analysemultiplesongs'
        else:
            image_folder = 'analyseoneartist'
            
        for i, item in enumerate(self.items):
            checkbox_var = ctk.BooleanVar()
            ItemFrame = ctk.CTkFrame(self.items_results_frame)
            ItemFrame.grid(row=i+1, column=1, pady=(0, 10), sticky='nsew')
            ItemFrame.grid_columnconfigure(3, weight=1)
            image_location = f'images/foundimages/{image_folder}/image{i}.png'
            if self.type == 'song' or self.type == 'multiplesongs':
                image_url = item['album']['images'][1]["url"]
                urllib.request.urlretrieve(image_url, image_location)
                printed_item_name = f'{item["name"]} by {item["artists"][0]["name"]}'
            else:
                if len(item['images']) > 1:
                    image_url = item['images'][1]["url"]
                    urllib.request.urlretrieve(image_url, image_location)
                else:
                    image_location = 'images/noimagefound.png'
                printed_item_name = item["name"]
            if len(printed_item_name) > 40:
                printed_item_name = f'{printed_item_name[:37]}...'
            else:
                if self.type == 'artist':
                    printed_item_name = printed_item_name.ljust(60)
            item_image = ctk.CTkImage(light_image=Image.open(image_location), size=(40, 40))
            image_label = ctk.CTkLabel(ItemFrame, image=item_image, text="", corner_radius=20)
            image_label.grid(row=1, column=0, pady=3, sticky='w')
            item_title = ctk.CTkLabel(ItemFrame, text=printed_item_name, fg_color="transparent")
            item_title.grid(row=1, column=2, sticky='w')
            ItemCheckBox = ctk.CTkCheckBox(ItemFrame, text='', variable=checkbox_var, command=lambda index=i: self.on_checkbox_clicked(index))
            ItemCheckBox.grid(row=1, column=3, sticky='e', padx=(20, 0))
            self.ItemCheckBoxes.append(checkbox_var)
        
        self.item_submit_button = ctk.CTkButton(self, text=self.button_text, corner_radius=8, height=40, font=ctk.CTkFont(size=15), command=lambda: self.analyse_item(parent))
        self.item_submit_button.grid(row=11, column=1, sticky='nsew', padx=(0, 10))
        self.clear_button = ctk.CTkButton(self, text="Clear Results", corner_radius=8, height=40, font=ctk.CTkFont(size=15), command=lambda: self.clear_results(parent))
        self.clear_button.grid(row=11, column=2, sticky='ewns')

        if type == 'multiplesongs':
            self.chosen_songs_frame = ctk.CTkFrame(self.rightcolumn, corner_radius=8, fg_color='transparent')
            self.chosen_songs_frame.grid(row=1, column=1, sticky='nsew', pady=(20, 0))
            self.chosen_songs_frame.grid_columnconfigure(1, weight=1)
            self.chosen_songs_title_frame = ctk.CTkFrame(self.chosen_songs_frame, corner_radius=8, height=35)
            self.chosen_songs_title_frame.grid(row=1, column=1, pady=(0, 8), sticky='new')
            self.chosen_songs_title_frame.grid_columnconfigure(1, weight=1)
            self.chosen_songs_title = ctk.CTkLabel(self.chosen_songs_title_frame, text='Chosen Songs (Max 5) - Click Checkbox to Remove', corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent')
            self.chosen_songs_title.grid(row=1, column=1, sticky='new', pady=(4, 4))
            
            self.chosen_songs_frame_items = ctk.CTkFrame(self.chosen_songs_frame, corner_radius=8)
            self.chosen_songs_frame_items.grid(row=2, column=1, pady=(0, 10), sticky='new')
            self.chosen_songs_frame_items.grid_columnconfigure(1, weight=1)
            parent.create_selected_song_frames(self.chosen_songs_frame_items)
            
            self.chosen_songs_button = ctk.CTkButton(self.chosen_songs_frame, text='Analyse Chosen Songs', corner_radius=8, font=ctk.CTkFont(size=15), height=30, command = lambda : parent.create_radar_chart(self.chosen_songs_frame))
            self.chosen_songs_button.grid(row=7, column=1, sticky='new', pady=(0, 10))
            
    def on_checkbox_clicked(self, index):
        for i, checkbox_var in enumerate(self.ItemCheckBoxes):
            if i != index:
                checkbox_var.set(False)
    
    def analyse_item(self, parent):
        item = None
        item_index = 0
        for i, checkbox_var in enumerate(self.ItemCheckBoxes):
            if checkbox_var.get():
                item = self.items[i]
                item_index = i
                break
        if item is not None:
            item_id = item['id']
            if self.type == 'song':
                raw_item_audio_features = spotify_object.audio_features(item_id)
                item_audio_features = raw_item_audio_features[0]
                analysed_item_window = AnalysedSongWindow(self.rightcolumn, item, item_audio_features, item_index)
                analysed_item_window.grid(row=1, column=1, sticky='nwe') 
            elif self.type == 'multiplesongs':
                parent.add_song_to_list(item_id, item, self.chosen_songs_frame_items)
            else:
                raw_artist_top_tracks = spotify_object.artist_top_tracks(item_id)
                artist_top_tracks = raw_artist_top_tracks["tracks"]
                
                headers = {
                    'user-agent': 'SpotiMetrics'
                }
                payload = {
                    'api_key': '0da9ed9dd5a93797fb3482737cd2ed5d',
                    'method': 'artist.getInfo',
                    'artist': f'{item["name"]}',
                    'autocorrect': '1',
                    'format': 'json'
                }
                lastfm_data = requests.get('https://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
                analysed_item_window = AnalysedArtistWindow(self.rightcolumn, item, artist_top_tracks, item_index, lastfm_data.json())
                analysed_item_window.grid(row=1, column=1, sticky='nwe') 
        else:
            return

    def clear_results(self, parent):
        self.searchbar.delete(0, ctk.END)
        self.items_results_frame.destroy()
        if self.type == 'multiplesongs':
            parent.empty_list()
            self.chosen_songs_frame_items.destroy()
        self.rightcolumn.destroy()
        self.item_submit_button.destroy()
        self.clear_button.destroy()

class AnalysedSongWindow(ctk.CTkFrame):
    def __init__(self, master, song, song_audio_features, song_index):
        super().__init__(master)
        self.configure(fg_color='transparent')
        #Assigning all variables to the object for easy variable calling
        self.song = song
        self.song_audio_features = song_audio_features
        self.song_index = song_index
        
        # Ensuring that the`song name is not too long to fit in the window
        printable_song_name = f'{self.song["name"]} {"(Explicit)" if self.song["explicit"] else ""}' 
        if len(printable_song_name) > 68:
            printable_song_name = f'{self.song["name"][:65]}... {"(Explicit)" if self.song["explicit"] else ""}' 
        #Loops through all artists associated with the song and creates a list of their names separated by commas
        song_artists_details = self.song['artists']
        song_artists = []
        for artist in range(len(song_artists_details)):
            song_artists.append(song_artists_details[artist]['name'])
        printable_artists = 'By '
        for artist in range(len(song_artists)):
            #If the artist is the last artist in the list, no comma will be added after his name
            if artist < (len(song_artists) - 1):
                printable_artists += (song_artists[artist] + ', ')
            else:
                printable_artists += song_artists[artist]
        
        #converts the duration to the songs from miliseconds to minutes:secondss by creating a string  
        song_duration_ms = self.song['duration_ms']
        song_minutes_decimal = song_duration_ms / 60000
        song_minutes = math.floor(song_minutes_decimal)
        song_seconds_decimal = song_minutes_decimal - song_minutes
        # converts all seconds to two digits (5 seconds becomes 05)
        song_seconds = f"{math.floor(song_seconds_decimal*60):02}"
        song_duration = f"{song_minutes}:{song_seconds}"    
        
        #Obtains the key of the song using pitch class notation and the 'key' and 'mode' audio features and prints them into a string
        pitch_class_notation = {-1: 'Unknown', 0: 'C', 1: 'C#/D♭', 2: 'D', 3: 'D#/E♭', 4: 'E', 5: 'F', 6: 'F#/G♭', 7: 'G', 8: 'G#/A♭', 9: 'A', 10: 'A#/B♭', 11: 'B'}
        song_mode = self.song_audio_features['mode']
        if song_mode == 1:
            song_modality = 'Major'
        else:
            song_modality = 'Minor'
        song_key = f"{pitch_class_notation[self.song_audio_features['key']]} {song_modality}"
        
        # Creates a list of all the song details to be displayed in the radar graph
        self.song_details_row_one = [f'Duration: {song_duration}', f'Time Signature: {self.song_audio_features["time_signature"]}/4', f'Popularity: {self.song["popularity"]}']
        self.song_details_row_two = [f'Key: {song_key}', f'Loudness: {round(self.song_audio_features["loudness"], 2)} dB', f'Tempo: {round(self.song_audio_features["tempo"], 2)} BPM']
        self.song_details = [self.song_details_row_one, self.song_details_row_two]
        
        self.song_audio_features_row_one = [[self.song_audio_features['speechiness'], self.song_audio_features['danceability']], ['Speechiness', 'Danceability']]
        self.song_audio_features_row_two = [[self.song_audio_features['energy'], self.song_audio_features['valence']], ['Energy', 'Happiness']]
        self.song_audio_features = [self.song_audio_features_row_one, self.song_audio_features_row_two]
        
        audio_features_list = ['Speechiness', 'Danceability', 'Energy', 'Valence']
        song_audio_features_graph_values = [self.song_audio_features_row_one[0][0], self.song_audio_features_row_one[0][1], self.song_audio_features_row_two[0][0], self.song_audio_features_row_two[0][1]]
        
        # Retrieving all relevant album details  and formatting them to be displayed
        song_album_details = self.song['album']
        printable_album_name = f"Album Name: {song_album_details['name']}"
        if len(printable_album_name) > 63:
            printable_album_name = f"Album Name: {song_album_details['name'][:60]}..."
        printable_album_release_date = f"Release Date: {song_album_details['release_date']}"
        printable_album_type = f"Album Type: {song_album_details['type'].capitalize()}"
        printabe_album_number_of_songs = f"Total Songs: {song_album_details['total_tracks']}"

        # Creating the grid layout of the window
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((1, 2, 3, 4), weight=1)
        
        # Creating the main cover frame by calling the CoverFrame class and passing the revelant parameters
        self.cover_frame = CoverFrame(self, f'images/foundimages/analyseonesong/image{song_index}.png', printable_song_name, printable_artists)
        self.cover_frame.grid(row=1, column=1, padx=(0, 10), pady=(20, 0), sticky='new')
        
        # Displaying all the song details by calling the InformationLabelFrame class and passing the revelant parameters
        self.song_details_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.song_details_frame.grid(row=2, column=1, padx=(0, 10), pady=(0, 11), sticky='nsew')
        self.song_details_frame.grid_columnconfigure((1, 2, 3), weight=1, uniform='column')
        self.song_details_frame.grid_rowconfigure((1, 2), weight=1)
        for i, song_detail in enumerate(self.song_details):
            # Each LabelFrame uses different padx values to ensure the labels are aligned correctly
            self.song_detail_label_frame1 = InformationLabelFrame(self.song_details_frame, self.song_details[i][0])
            self.song_detail_label_frame1.grid(row=i, column=1, pady=(10, 0), sticky='nsew')
            
            self.song_detail_label_frame2 = InformationLabelFrame(self.song_details_frame, self.song_details[i][1])
            self.song_detail_label_frame2.grid(row=i, column=2, padx=10, pady=(10, 0), sticky='nsew')
            
            self.song_detail_label_frame3 = InformationLabelFrame(self.song_details_frame, self.song_details[i][2])
            self.song_detail_label_frame3.grid(row=i, column=3, pady=(10, 0), sticky='nsew')
        
        # Diplaying the numerical audio features value in the slider format by calling the InformationSliderFrame class and passing the revelant parameters
        self.song_audio_features_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.song_audio_features_frame.grid(row=3, column=1, padx=(0, 10), sticky='nsew')
        self.song_audio_features_frame.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.song_audio_features_frame.grid_rowconfigure((1, 2), weight=1)
        
        for i, song_audio_feature_row in enumerate(self.song_audio_features):
            self.song_audio_feature_frame = InformationSliderFrame(self.song_audio_features_frame, song_audio_feature_row[1][0], song_audio_feature_row[0][0])
            self.song_audio_feature_frame.grid(row=i+1, column=1, pady=(0, 10), padx=(0, 10), sticky='nsew')
            
            self.song_audio_feature_frame2 = InformationSliderFrame(self.song_audio_features_frame, song_audio_feature_row[1][1], song_audio_feature_row[0][1])
            self.song_audio_feature_frame2.grid(row=i+1, column=2, pady=(0, 10), sticky='nsew')
        
        self.song_other_details_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.song_other_details_frame.grid(row=4, column=1, padx=(0, 10), pady=(0, 10), sticky='nsew')
        self.song_other_details_frame.grid_rowconfigure(1, weight=1)
        self.song_other_details_frame.grid_columnconfigure((1, 2), weight=1, uniform='column')
        
        # Creating the radar graph by calling the RadarGraph class and passing the revelant parameters
        self.song_radar_graph_frame = RadarGraph(self.song_other_details_frame, audio_features_list, song_audio_features_graph_values, [15, 10], [5, 10], [210, 180])
        self.song_radar_graph_frame.grid(row=1, column=1, padx=(0, 10), sticky='nsew')
        
        # Formatting and printing the album details in their own frame which is aligned to the bottom right of the window
        self.song_album_frame = ctk.CTkFrame(self.song_other_details_frame)
        self.song_album_frame.grid(row=1, column=2, sticky='nsew')
        self.song_album_frame.grid_rowconfigure(1, weight=1)
        self.song_album_frame.grid_columnconfigure(1, weight=1)
        
        self.song_album_label_frame = ctk.CTkFrame(self.song_album_frame, corner_radius=8, fg_color='transparent')
        self.song_album_label_frame.grid(row=1, column=1, pady=(5, 0), sticky='new')
        self.song_album_label_frame.grid_columnconfigure(1, weight=1)
        self.song_album_label_frame.grid_rowconfigure((1, 2, 3, 4, 5), weight=1)
        self.song_album_label = ctk.CTkLabel(self.song_album_label_frame, text='Album Details', corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent')
        self.song_album_label.grid(row=1, column=1, sticky='nsew')
        self.song_album_name_label = ctk.CTkLabel(self.song_album_label_frame, text=printable_album_name, corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent', wraplength=220, justify='left')
        self.song_album_name_label.grid(row=2, column=1, sticky='nw')
        self.song_album_release_date_label = ctk.CTkLabel(self.song_album_label_frame, text=printable_album_release_date, corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent', wraplength=220, justify='left')
        self.song_album_release_date_label.grid(row=3, column=1, sticky='nw')
        self.song_album_type_label = ctk.CTkLabel(self.song_album_label_frame, text=printable_album_type, corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent', wraplength=220, justify='left')
        self.song_album_type_label.grid(row=4, column=1, sticky='nw')
        self.song_album_total_songs_label = ctk.CTkLabel(self.song_album_label_frame, text=printabe_album_number_of_songs, corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent', wraplength=220, justify='left')
        self.song_album_total_songs_label.grid(row=5, column=1, sticky='nw')

class AnalysedArtistWindow(ctk.CTkFrame):
    def __init__(self, master, artist, artist_top_tracks, artist_index, lastfm_data):
        super().__init__(master)
        self.configure(fg_color='transparent')
        self.artist = artist
        self.artist_top_tracks = artist_top_tracks
        self.lastfm_data = lastfm_data

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((1, 2, 3, 4, 5), weight=1)
        
        printable_artist_name = self.artist['name'] 
        if len(printable_artist_name) > 68:
            printable_song_name = f'{self.artist["name"][:65]}...' 
        
        self.artist_followers = artist['followers']['total']
        self.formatted_artist_followers = '{:,}'.format(self.artist_followers).replace(',', ' ')
        self.printable_artist_followers = f'Followers: {self.formatted_artist_followers}'
        self.printable_artist_popularity = f"Popularity: {artist['popularity']}"
        self.artist_details = [self.printable_artist_followers, self.printable_artist_popularity]
        self.padxlist = [0, 10]
        
        self.cover_frame = CoverFrame(self, f'images/foundimages/analyseoneartist/image{artist_index}.png', printable_artist_name, '')
        self.cover_frame.grid(row=1, column=1, padx=(0, 10), pady=(20, 0), sticky='new')
        
        self.artist_bio = lastfm_data['artist']['bio']['content']
        if len(self.artist_bio) > 0:
            index_of_a_tag = self.artist_bio.find('<a')
            if index_of_a_tag != -1:
                self.artist_bio = self.artist_bio[:index_of_a_tag]
        else:
            self.artist_bio = 'No Bio Available'
        
        self.artist_genres = artist["genres"]
        self.printable_genres = ''
        if len(self.artist_genres) > 0:
            for genre in range(len(self.artist_genres)):
                #Last artist in the list is added without a comma
                if genre < (len(self.artist_genres) - 1):
                    self.printable_genres += (self.artist_genres[genre].capitalize() + ', ')
                else:
                    self.printable_genres += self.artist_genres[genre].capitalize()
        else:
            self.printable_genres = 'No Genres Available'

        self.artist_details_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.artist_details_frame.grid(row=2, column=1, padx=(0, 10), pady=(0, 11), sticky='nsew')
        self.artist_details_frame.grid_columnconfigure((1, 2), weight=1, uniform='column')
        self.artist_details_frame.grid_rowconfigure(1, weight=1)
        
        self.printable_top_tracks = ''
        for i, track in enumerate(self.artist_top_tracks):
            self.printable_top_tracks = self.printable_top_tracks + f'{i+1}. {track["name"]} \n'

        for i, artist_detail in enumerate(self.artist_details):
            self.artist_detail_label_frame = InformationLabelFrame(self.artist_details_frame, artist_detail)
            self.artist_detail_label_frame.grid(row=1, column=i+1, pady=(10, 0), padx=(self.padxlist[i], 0), sticky='nsew')
        
        self.artist_bio_textbox = ctk.CTkTextbox(self, corner_radius=8, height=165)
        self.artist_bio_textbox.grid(row=3, column=1, sticky='nsew', pady=(0, 11))
        self.artist_bio_textbox.insert('0.0', 'Artist Bio (from last.fm): \n\n' + self.artist_bio)
        self.artist_bio_textbox.configure(state='disabled')
        
        self.artist_genres_textbox = ctk.CTkTextbox(self, corner_radius=8, height=80)
        self.artist_genres_textbox.grid(row=4, column=1, sticky='nsew', pady=(0, 11))
        self.artist_genres_textbox.insert('0.0', 'Artist Genres: \n\n' + self.printable_genres)
        self.artist_genres_textbox.configure(state='disabled')
        
        self.artist_top_tracks_textbox = ctk.CTkTextbox(self, corner_radius=8, height=165)
        self.artist_top_tracks_textbox.grid(row=5, column=1, sticky='nsew')
        self.artist_top_tracks_textbox.insert('0.0', 'Artist Top Tracks: \n\n' + self.printable_top_tracks)
        self.artist_top_tracks_textbox.configure(state='disabled')

class LeftColumn(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.configure(height=720, corner_radius=0, fg_color='transparent')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

class RightColumn(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.configure(height=720, corner_radius=0, fg_color='transparent')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

class CoverFrame(ctk.CTkFrame):
    def __init__(self, master, image_url, main_name, secondary_info):
        super().__init__(master)
        self.image_url = image_url
        self.main_name = main_name
        self.secondary_info = secondary_info
        
        # Creating the image object by finding the relevant image using the image_url parameter
        self.image = ctk.CTkImage(light_image=Image.open(self.image_url), size=(136, 136))
        self.image_label = ctk.CTkLabel(self, image=self.image, text='')
        self.image_label.grid(row=1, column=1, sticky='nsw', padx=10, pady=10, rowspan=2)
        # Displaying the main name and secondary info of the artist/album/track
        self.main_name_label = ctk.CTkLabel(self, text=self.main_name, fg_color='transparent', font=ctk.CTkFont(size=24), justify='left', wraplength=330)
        self.main_name_label.grid(row=1, column=2, sticky='nw', padx=(0, 10), pady=(15, 0))
        self.secondary_info_label = ctk.CTkLabel(self, text=self.secondary_info, fg_color='transparent', font=ctk.CTkFont(size=15), justify='left', wraplength=330)
        self.secondary_info_label.grid(row=2, column=2, sticky='nw', padx=(0, 10), pady=(0, 10))

class InformationLabelFrame(ctk.CTkFrame):
    def __init__(self, master, text):
        super().__init__(master)
        self.text = text
        self.configure(corner_radius=8, height=35)
        self.grid_columnconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(self, text=self.text, font=ctk.CTkFont(size=15), corner_radius=8, fg_color='transparent')
        self.label.grid(row=1, column=1, sticky='ew', pady=9)

class InformationSliderFrame(ctk.CTkFrame):
    def __init__(self, master, title, slider_value):
        super().__init__(master)
        self.title = title
        self.slider_value = slider_value
        self.grid_columnconfigure((1, 2), weight=1)
        self.grid_rowconfigure((1, 2), weight=1)
        
        self.title_frame = ctk.CTkFrame(self, corner_radius=8, fg_color='transparent')
        self.title_frame.grid(row=1, column=1, sticky='nsew', pady=(5, 4), padx=(15, 0))
        self.title_frame.grid_columnconfigure(1, weight=1)
        self.title_label = ctk.CTkLabel(self.title_frame, text=self.title, corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent')
        self.title_label.grid(row=1, column=1, sticky='nsew')
        self.information_slider = ctk.CTkSlider(self, from_=0, to=1, state='disabled', hover=False)
        self.information_slider.set(slider_value)
        self.information_slider.grid(row=2, column=1, pady=(0, 10), sticky='nsew', padx=(15, 0))

class RadarGraph(ctk.CTkFrame):
    def __init__(self, master, graph_labels, graph_values, padx_list, pady_list, size_list):
        super().__init__(master)
        self.grid_rowconfigure((1, 2), weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.graph_labels = graph_labels
        self.graph_values = graph_values
        self.padx_list = padx_list
        self.pady_list = pady_list
        self.size_list = size_list
        
        # Adding the final value to the start of the list to ensure that the plotted points formed a closed polygon
        audio_features_list = [*self.graph_labels, self.graph_labels[0]]
        song_audio_features_graph_values = [*self.graph_values, self.graph_values[0]]
        # Creating the borders of the graph 
        label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(audio_features_list))
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor='#2B2B2B')
        # Plotting the graph and filling in the axis area
        ax.plot(label_loc, song_audio_features_graph_values, lw=2)
        ax.fill(label_loc, song_audio_features_graph_values, alpha=0.3)
        ax.set_facecolor("#2B2B2B")
        lines, labels = plt.thetagrids(np.degrees(label_loc), labels=audio_features_list, color='white')
        edge_color = (1, 1, 1, 1) 
        ax.spines['polar'].set_color(edge_color) 
        ax.tick_params(axis='both', colors='white')
        ax.grid(color='white', alpha=0.5)
        ax.set_ylim(0, 1)
        # Saving the final image to the user's computer so it can be accessed by the program
        plt.savefig('images/foundimages/analyseonesong/radargraph.png', dpi=300, bbox_inches='tight')
        
        # Creating the radar graph image object and displaying it within its frame
        self.radar_graph_label_frame = ctk.CTkFrame(self, corner_radius=8, fg_color='transparent')
        self.radar_graph_label_frame.grid(row=1, column=1, pady=(5, 0), sticky='nsew')
        self.radar_graph_label_frame.grid_columnconfigure(1, weight=1)
        self.radar_graph_label = ctk.CTkLabel(self.radar_graph_label_frame, text='Radar Graph', corner_radius=8, font=ctk.CTkFont(size=15), fg_color='transparent')
        self.radar_graph_label.grid(row=1, column=1, sticky='nsew')
        self.radar_graph_image = ctk.CTkImage(light_image=Image.open(f'images/foundimages/analyseonesong/radargraph.png'), size=(size_list[0], size_list[1]))
        self.radar_graph = ctk.CTkLabel(self, image=self.radar_graph_image, text='')
        self.radar_graph.grid(row=2, column=1, sticky='nsew', padx=(padx_list[0], padx_list[1]), pady=(pady_list[0], pady_list[1]))

class PopupWindow(ctk.CTkToplevel):
    def __init__(self, master, text):
        super().__init__(master)
        self.text = text
        self.title("SpotiMetrics Popup Window")
        self.geometry("1000x300")

        self.label = ctk.CTkLabel(self, text=self.text, justify='center', anchor='center', font=ctk.CTkFont(size=15))
        self.label.grid(row=1, column=1, padx=20, pady=20)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SpotiMetrics")
        self.geometry(f"{width}x{height}")
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.loading_popup = PopupWindow(self, 'Loading Application...')
        
        side_bar = SideBar(self)
        side_bar.grid(row=0, column=1, sticky="nsew")
        
        self.frames = {}
        
        for F in (AnalyseOneSongWindow, AnalyseMultipleSongsWindow, AnalyseOneArtistWindow, AnalyseOnePlaylistWindow, PlaylistRecommendationWindow):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=2, sticky="nsew")
            frame.configure(fg_color='transparent')
        self.show_frame(AnalyseOneSongWindow)
        
        self.loading_popup.destroy()
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Removes all images from the foundimages folder so that the program can be run multiple times without the user having to manually delete the images
images_folder = 'images/foundimages'
for folder in os.listdir(images_folder):
    for file in os.listdir(f'{images_folder}/{folder}'):
        os.remove(os.path.join(f'{images_folder}/{folder}', file))

spotify_client_id = "client_id_here"
spotify_client_secret = "client_secret_here"
spotify_redirect_uri = "redirect_uri_here"
#Defines the required scopes required for the program to work 
spotify_scope = "user-library-read user-read-private playlist-read-private playlist-read-collaborative user-follow-read user-top-read playlist-modify-public playlist-modify-private"

#Authenticates the user with the Spotify API through the OAuth Code Flow
oauth_object = sp.SpotifyOAuth(client_id=spotify_client_id, 
                                    client_secret=spotify_client_secret,
                                    redirect_uri=spotify_redirect_uri, 
                                    scope=spotify_scope,
                                    show_dialog=True)

#Retrieves the user's access token
token_dict = oauth_object.get_access_token()
token = token_dict['access_token']

#Connects the user to the Spotify API using their access token and retrieves their relevant information
spotify_object = sp.Spotify(auth=token)
user = spotify_object.current_user()

app = App()
app.resizable(False, False)
app.protocol("WM_DELETE_WINDOW", app.quit)
app.mainloop()

ctk.set_appearance_mode("Dark")
