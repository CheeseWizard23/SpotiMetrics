#Imports all libraries required
import spotipy
import json
import math
from textwrap import dedent
import plotly.express as px
import pandas as pd

#Module for analysing specific songs
def analyse_song():
    song_name_search = input('\nPlease Enter The Name Of The Song You Would Like To Search: \n')
    #Makes a call to the Spotify API to retrive all relevant songs from the user input
    raw_song_results = spotify_object.search(song_name_search, type="track", limit=10)
    song_results = raw_song_results['tracks']['items']
    #Prints out all relvant songs by looping through the array of songs
    print("The Closest Songs Found Are: \n------------------------------------------------")
    x= 1
    for song in song_results:
        print(f"{x}. {song['name']} by {song['artists'][0]['name']}")
        x += 1
    print("------------------------------------------------")
    # While loop to ensure user input does not cause erorrs as it should only be a number from 1 to 10 inclusive
    selected_song_number = input('Please Select The Number Of The Song You Would Like To Analyse: ')
    while selected_song_number not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        print('Please enter a number from 1 to 10 (inclusive)')
        selected_song_number = input('Please Select The Number Of The Song You Would Like To Analyse: ')

    #Retrieves the specific song that the user has chosen from the list
    song_index = int(selected_song_number) - 1
    song = song_results[song_index]

    #Loops through all artists associated with the song and creates a list of their names separated by commas
    song_artists_details = song['artists']
    song_artists = []
    for artist in range(len(song_artists_details)):
        song_artists.append(song_artists_details[artist]['name'])
    printable_artists = ''
    for artist in range(len(song_artists)):
        #If the artist is the last artist in the list, no comma will be added after his name
        if artist < (len(song_artists) - 1):
            printable_artists += (song_artists[artist] + ', ')
        else:
            printable_artists += song_artists[artist]

    #converts the duration to the songs from miliseconds to minutes:secondss by creating a string  
    song_duration_ms = song['duration_ms']
    song_minutes_decimal = song_duration_ms / 60000
    song_minutes = math.floor(song_minutes_decimal)
    song_seconds_decimal = song_minutes_decimal - song_minutes
    # converts all seconds to two digits (5 seconds becomes 05)
    song_seconds = f"{math.floor(song_seconds_decimal*60):02}"
    song_duration = f"{song_minutes}:{song_seconds}"

    #Converts boolean variable to 'yes'/'n' strings
    if song['explicit'] == True:
        explicit = 'Yes'
    else:
        explicit = 'No'

    #Makes a call to the Spotify API to their audio_features endpoint to retrieve the audio features statistics of the song
    song_id = song['id']
    raw_song_audio_features = spotify_object.audio_features(song_id)
    song_audio_features = raw_song_audio_features[0]

    #Processes the instrumentalness numerical value into a string that users can better understand
    song_instrumentalness_data = song_audio_features['instrumentalness']
    if song_instrumentalness_data <= 0.1:
        song_instrumentalness = 'Contains Vocals'
    elif song_instrumentalness_data <= 0.3:
        song_instrumentalness = 'Is Likely to Contains Vocals'
    else: 
        song_instrumentalness = 'Is Likely to be an Instrumental Track'

    #Obtains the key of the song using pitch class notation and the 'key' and 'mode' audio features and prints them into a string
    pitch_class_notation = {-1: 'Unknown', 0: 'C', 1: 'C#/D♭', 2: 'D', 3: 'D#/E♭', 4: 'E', 5: 'F', 6: 'F#/G♭', 7: 'G', 8: 'G#/A♭', 9: 'A', 10: 'A#/B♭', 11: 'B'}
    song_mode = song_audio_features['mode']
    if song_mode == 1:
        song_modality = 'Major'
    else:
        song_modality = 'Minor'
    song_key = f"{pitch_class_notation[song_audio_features['key']]} {song_modality}"

    #Obtains all information from the song object about its album 
    song_album_details = song['album']

    #Prints all song attributes
    print(dedent(f"""
        ------------------------------------------------
        Song Name: {song['name']}
        Song Artists: {printable_artists}
        Song Duration: {song_duration}
        Explicit: {explicit}
        Popularity Rating (0-100): {song['popularity']}
        
        Acousticness (0-1): {song_audio_features['acousticness']}
        Danceability (0-1): {song_audio_features['danceability']}
        Energy (0-1): {song_audio_features['energy']}
        Instrumentalness: {song_instrumentalness}
        Key: {song_key}
        Loudness: {song_audio_features['loudness']} dB
        Tempo: {song_audio_features['tempo']} BPM
        Time Signature: {song_audio_features['time_signature']}/4
        Valence (0-1): {song_audio_features['valence']}
        ------------------------------------------------
        
        -----------------------------------------------
        Album Name: {song_album_details['name']}
        Album Release Date: {song_album_details['release_date']}
        Album Type: {song_album_details['type'].capitalize()}
        Total Number of Songs: {song_album_details['total_tracks']}
        ------------------------------------------------
    """))

    generate_graph_input = input("Enter 'y' To Generate A Radar Graph Of The Obtained Data (Enter Anything Else to Skip): ")
    if generate_graph_input == 'y':
        #Creates a radar graph of the numerical characteristics of the song
        
        #Creates a two-dimensional array of the characteristics and their values
        df = pd.DataFrame(dict(
        Value = [song_audio_features['acousticness'], 
                song_audio_features['danceability'], 
                song_audio_features['energy'],
                song_audio_features['valence']
                ],
        Audio_Feature = ['Acousticness', 'Danceability', 'Energy', 'Valence']
        ))
        
        #Creates and displays the radar graphs
        graph = px.line_polar(df, r='Value', theta='Audio_Feature', line_close=True)
        graph.update_traces(fill='toself')
        graph.show()
    
    restart() #Calls the restart module

#Module for obtaining information about artists
def search_artists():
    artist_name_search = input('\nPlease Enter The Name Of The Artist You Would Like To Search: \n')
    #Makes a call to the Spotify API to retrive all relevant artists  from the user input
    raw_artist_results = spotify_object.search(artist_name_search, type="artist", limit=10)
    artist_results = raw_artist_results['artists']['items']
    #Prints out all relvant artists by looping through the array of artists
    print("The Closest Artists Found Are: \n------------------------------------------------")
    x = 1
    for artist in artist_results:
        print(f"{x}. {artist['name']}")
        x += 1
    print("------------------------------------------------")
    # While loop to ensure user input does not cause erorrs
    selected_artist_number = input('Please Select The Number Of The Artist You Would Like To Search: ')
    while selected_artist_number not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        print('Please enter a number from 1 to 10 (inclusive)')
        selected_artist_number = input('Please Select The Number Of The Artist You Would Like To Analyse: ')

    #Retrieves the specific artist that the user has chosen from the list
    artist_index = int(selected_artist_number) - 1
    artist = artist_results[artist_index]
    
    #Retrieves the genres of the artist from the artist objects and creates a string of genres separated by commas
    artist_genres = artist["genres"]
    printable_genres = ''
    for genre in range(len(artist_genres)):
        #Last artist in the list is added without a comma
        if genre < (len(artist_genres) - 1):
            printable_genres += (artist_genres[genre] + ', ')
        else:
            printable_genres += artist_genres[genre]        
    
    #Makes a call to the Spotify API to retrive the artist's top songs
    artist_id = artist["id"]
    raw_artist_top_tracks = spotify_object.artist_top_tracks(artist_id)
    artist_top_tracks = raw_artist_top_tracks["tracks"]

    #Prints all information about the artist
    print(dedent(f"""
        ------------------------------------------------
        Artist Name: {artist['name']}
        Artist Followers: {artist['followers']['total']}
        Artist Genres: {printable_genres}
        Popularity Rating (0-100): {artist['popularity']}
        ------------------------------------------------
    """))
    print('------------------------------------------------')
    #Prints the top tracks of the artists line-by-line by looping through the retrieed list of top songd
    print('Top Tracks:')
    for track in range(len(artist_top_tracks)):
        print(artist_top_tracks[track]['name'])
    print('------------------------------------------------')
    restart() #Calls the restart module

# Module to retrieve all user playlists
def get_playlists():
    #Make a call to the Spotify AI to retrieve the first 50 playlist of the user 
    raw_playlists = spotify_object.current_user_playlists(limit=50)
    playlists = raw_playlists["items"]
    
    #Loop to ensure that all user playlists are obtained if they have more than 50 playlists
    offset = 50
    total_playlists = raw_playlists["total"] 
    while total_playlists >= 50:
        raw_extra_playlists = spotify_object.current_user_playlists(limit=50, offset=offset)
        extra_playlists = raw_extra_playlists["items"]
        #Decreases the total playists remaining and increases the offset used in the Spotify API csll
        total_playlists -= 50
        offset += 50
        #Adds all extra playlists to the list of playlists
        for x in range(len(extra_playlists)):
            playlists.append(extra_playlists[x])
    
    #Outputs the number of playlists to the user
    print(f"\nYou Have {len(playlists)} Playlists.")
    #Prints all playlist names to an external text file by looping through the list
    f = open("playlist_names.txt", "w")
    for playlist in range(len(playlists)):
        f.write(playlists[playlist]['name'] + '\n')
    f.close()
    print("A Printout Of Your Playlist Names Has Been Provided In playlist_names.txt")
    restart() #Calls the restart module

def main():
    #Input for user to decide what part of the program to run
    program_decider = input("Please Press \n  1 To Analyse A Song\n  2 To Get Information About An Artist\n  3 To View Your Playlists (demo)\n  4 To Quit\n")
    #Loop to ensure that the user input is valid
    while program_decider not in ['1', '2', '3', '4']:
        print('Please Provide A Valid Input')
        program_decider = input("Please Press \n  1 To Analyse A Song\n  2 To Get Information About An Artist\n  3 To View Your Playlists (demo)\n  4 To Quit\n")

    #Process the user input and calls the corresponding function 
    if program_decider == '1':
        analyse_song()
    elif program_decider == '2':
        search_artists()
    elif program_decider == '3':
        get_playlists()
    else:
        quit() #Quits the program

# Restart module
def restart():
    print('\n')
    restart_input = input('Would You Like To Use The Program Again? Press \n  1 to Restart\n  2 to Quit\n')
    #Loop to ensure that the user input is valid
    while restart_input not in ['1', '2']:
        print('Please Provide A Valid Input')
        restart_input = input('Would You Like To Use The Program Again? Press \n  1 to Restart\n  2 to Quit\n')
    
    if restart_input == '1':
        print('\n')
        main() #Calls the main module
    else:
        quit()

#Defines the Spotify application details 
spotify_client_id = "ca8c02f458a04e6298de27379aafc59f"
spotify_client_secret = "25877b75b30d417cae31612513481fca"
spotify_redirect_uri = "http://localhost:7777/callback"
#Defines the required scopes required for the program to work 
spotify_scope = "user-library-read user-read-private playlist-read-private playlist-read-collaborative"

#Authenticates the user with the Spotify API through the OAuth Code Flow
oauth_object = spotipy.SpotifyOAuth(client_id=spotify_client_id, 
                                    client_secret=spotify_client_secret,
                                    redirect_uri=spotify_redirect_uri, 
                                    scope=spotify_scope,
                                    show_dialog=True)

#Retrieves the user's access token
token_dict = oauth_object.get_access_token()
token = token_dict['access_token']

#Connects the user to the Spotify API using their access token and retrieves their relevant information
spotify_object = spotipy.Spotify(auth=token)
user = spotify_object.current_user()

print(f"\nHello {user['display_name']}")
print("Welcome to SpotiMetrics: Song Analyser and Information Provider [Prototype]")
main() #Calls the main module