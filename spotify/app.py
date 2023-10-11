from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')

from io import BytesIO
import base64

app = Flask(__name__)

# Load the Spotify dataset
data = pd.read_csv('spotify-2023.csv', encoding='latin-1')
data['streams'] = pd.to_numeric(data['streams'], errors='coerce')
data['streams'] = pd.to_numeric(data['streams'], errors='coerce').astype('Int64')

@app.route('/', methods=['GET', 'POST'])
def index():
    # Artist Analysis
    num_tracks = len(data)
    num_unique_artists = len(data['artist(s)_name'].unique())

    # KPIs
    kpi_data = {
        'Number of Tracks': num_tracks,
        'Number of Unique Artists': num_unique_artists
    }

    # Top 10 Artists with Most Songs
    top_artists_songs = data['artist(s)_name'].value_counts().head(10)

    # Create a horizontal Matplotlib bar chart for top artists with most songs
    plt.figure(figsize=(10, 6))
    ax1 = top_artists_songs[::-1].plot(kind='barh', color='skyblue')  # Reverse the order for a horizontal chart
    plt.xlabel('Number of Songs')
    plt.ylabel('Artist')
    plt.title('Top 10 Artists with Most Songs')
    # plt.savefig('static/top_artists_songs.png')  # Save the plot to a file

    # Add labels for the number of songs on each bar
    for i, v in enumerate(top_artists_songs[::-1]):
        ax1.text(v, i, str(v), color='blue', va='center', fontweight='bold')

    # Save the Matplotlib plot to a BytesIO object
    img_data_songs = BytesIO()
    plt.savefig(img_data_songs, format='png')
    img_data_songs.seek(0)
    img_base64_songs = base64.b64encode(img_data_songs.read()).decode('utf-8')

    # Top 10 Artists with Most Streams
    top_artists_streams = data.groupby('artist(s)_name')['streams'].sum().nlargest(10)

    # Create a horizontal Matplotlib bar chart for top artists with most streams
    plt.figure(figsize=(10, 6))
    ax2 = top_artists_streams[::-1].plot(kind='barh', color='lightcoral')  # Reverse the order for horizontal chart
    plt.xlabel('Number of Streams')
    plt.ylabel('Artist')
    plt.title('Top 10 Artists with Most Streams')

    # Add labels for the number of streams on each bar
    for i, v in enumerate(top_artists_streams[::-1]):
        ax2.text(v, i, str(v), color='blue', va='center', fontweight='bold')

    # Save the Matplotlib plot to a BytesIO object
    img_data_streams = BytesIO()
    plt.savefig(img_data_streams, format='png')
    img_data_streams.seek(0)
    img_base64_streams = base64.b64encode(img_data_streams.read()).decode('utf-8')

    # Top 10 Artists with Most Playlists
    top_artists_playlists = data.groupby('artist(s)_name')['in_spotify_playlists'].sum().nlargest(10)

    # Create a horizontal Matplotlib bar chart for top artists with most playlists
    plt.figure(figsize=(10, 6))
    ax3 = top_artists_playlists[::-1].plot(kind='barh', color='lightgreen')  # Reverse the order for horizontal chart
    plt.xlabel('Number of Playlists')
    plt.ylabel('Artist')
    plt.title('Top 10 Artists with Most Playlists in Spotify')

    # Add labels for the number of playlists on each bar
    for i, v in enumerate(top_artists_playlists[::-1]):
        ax3.text(v, i, str(v), color='blue', va='center', fontweight='bold')

    # Save the Matplotlib plot to a BytesIO object
    img_data_playlists = BytesIO()
    plt.savefig(img_data_playlists, format='png')
    img_data_playlists.seek(0)
    img_base64_playlists = base64.b64encode(img_data_playlists.read()).decode('utf-8')

    # Top 10 Artists with Most Playlists in Apple
    top_artists_playlists_apple = data.groupby('artist(s)_name')['in_apple_playlists'].sum().nlargest(10)

    # Create a horizontal Matplotlib bar chart for top artists with most playlists in Apple
    plt.figure(figsize=(10, 6))
    ax4 = top_artists_playlists_apple[::-1].plot(kind='barh', color='lightblue')  # Reverse the order for horizontal chart
    plt.xlabel('Number of Playlists')
    plt.ylabel('Artist')
    plt.title('Top 10 Artists with Most Playlists in Apple')

    # Add labels for the number of playlists in Apple on each bar
    for i, v in enumerate(top_artists_playlists_apple[::-1]):
        ax4.text(v, i, str(v), color='blue', va='center', fontweight='bold')

    # Save the Matplotlib plot to a BytesIO object
    img_data_playlists_apple = BytesIO()
    plt.savefig(img_data_playlists_apple, format='png')
    img_data_playlists_apple.seek(0)
    img_base64_playlists_apple = base64.b64encode(img_data_playlists_apple.read()).decode('utf-8')


    # Filter the table data based on the submitted artist name filter
    artist_filter = request.form.get('artistFilter', '')
    filtered_data = data[data['artist(s)_name'].str.contains(artist_filter, case=False)]

    return render_template('index.html',
                           kpi_data=kpi_data,
                           img_base64_songs=img_base64_songs,
                           img_base64_streams=img_base64_streams,
                           img_base64_playlists=img_base64_playlists,
                           img_base64_playlists_apple=img_base64_playlists_apple,
                           track_data=filtered_data,
                           artist_filter=artist_filter)






@app.route('/track_analysis')
def track_analysis():
    # Top 10 Tracks by Stream
    top_tracks_streams = data.nlargest(10, 'streams')[['track_name', 'streams']]
    top_tracks_streams = top_tracks_streams.set_index('track_name')['streams'].to_dict()

    # Top 10 Tracks by Playlists
    top_tracks_playlists = data.nlargest(10, 'in_spotify_playlists')[['track_name', 'in_spotify_playlists']]
    top_tracks_playlists = top_tracks_playlists.set_index('track_name')['in_spotify_playlists'].to_dict()

    # Top 10 Tracks by Spotify Playlists
    top_tracks_spotify = data.nlargest(10, 'in_spotify_playlists')[['track_name', 'in_spotify_playlists']]
    top_tracks_spotify = top_tracks_spotify.set_index('track_name')['in_spotify_playlists'].to_dict()

    # Top 10 Tracks by Apple Playlists
    top_tracks_apple = data.nlargest(10, 'in_apple_playlists')[['track_name', 'in_apple_playlists']]
    top_tracks_apple = top_tracks_apple.set_index('track_name')['in_apple_playlists'].to_dict()

    # Top 10 Tracks by Deezer Playlists
    top_tracks_deezer = data.nlargest(10, 'in_deezer_playlists')[['track_name', 'in_deezer_playlists']]
    top_tracks_deezer = top_tracks_deezer.set_index('track_name')['in_deezer_playlists'].to_dict()

    return render_template('track_analysis.html',
                           top_tracks_streams=top_tracks_streams,
                           top_tracks_playlists=top_tracks_playlists,
                           top_tracks_spotify=top_tracks_spotify,
                           top_tracks_apple=top_tracks_apple,
                           top_tracks_deezer=top_tracks_deezer)

if __name__ == '__main__':
    app.run(debug=True)



