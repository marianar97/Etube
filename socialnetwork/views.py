from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from pathlib import Path
from configparser import ConfigParser
from datetime import timedelta
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from .models import Playlist, Video, Channel


CONFIG = ConfigParser()
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG.read(BASE_DIR / "config.ini")

API_KEY =  CONFIG.get("Django", "secret")

youtube = build('youtube', 'v3', developerKey="AIzaSyBGi7F7uIYldLKEXlldexCbJlgXWkio3wA")
topics1 = ['computer science', 'algorithms']
topics2 = ['compilers', 'java', 'javascript', 'numpy', 'sklearn']
topics3 = ['Machine Learning', 'Large Lenguage Models', 'Data Structures'] 
topics4 = ['React', 'Django Web development', 'CSS', 'Javascript']
topics5 = ['web development', 'python']
                                                                             
@login_required                  
def home(request):
    home_playlists = Playlist.objects.all()
    info = []
    for playlist in home_playlists:
        el = {}
        el['id'] = playlist.id
        el['title'] = playlist.title if len(playlist.title) < 26 else playlist.title[:24]+'...'
        el['playlist_thumbnail'] = playlist.thumbnail
        el['duration'] = get_duration(playlist.total_mins)
        c = Channel.objects.get(id=playlist.channel_id)
        el['channel_thumbnail'] = c.thumbnail
        el['channel_name'] = c.name
        info.append(el)
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    context = {'items': info, 'picture': extra_data['picture']}
    # fill_database(topics1)
    # fill_database(topics1, topics2, topics3, topics4, topics5)
    return render(request, 'socialnetwork/home.html', context)

def login_view(request):
    return render(request, 'socialnetwork/login.html')

def register_view(request):
    return render(request, 'socialnetwork/register.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))

@login_required
def course_view(request, playlist_id):
    video_id = request.GET.get("v")
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    playlist = Playlist.objects.get(id=playlist_id)
    videos_in_playlist = Video.objects.filter(playlist__id=playlist_id)
    first_video = Video.objects.get(id=video_id) if video_id else videos_in_playlist[0]
    context = {'playlist': playlist, 'picture': extra_data['picture'], 'videos': videos_in_playlist, 'fvideo':first_video}
    return render(request, 'socialnetwork/course.html', context=context)

def get_query(keywords: list) -> str:
    """
        this method returns a string to query the Youtube API
    """
    query = ""
    for topic in keywords[:-2]:
        query += topic + " | "
    query += keywords[-1]
    return query

def get_playlists_items(topics: list) -> list:
    """
        this method gets the query based on the topics to search
        and using that query fetches the data from Youtube API
        and return the playlists as a lists of dicts where each 
        element is a playlist
    """
    query = get_query(topics)
    request = youtube.search().list(
        part="snippet",
        maxResults=6,
        order="viewCount",
        q=query,
        type="playlist",
        relevanceLanguage="en"
    )
    return request.execute()['items']

def get_playlist_videos_channels(items: list):
    playlists = []
    channels = []
    videos = []

    for item in items:
        playlist = {}
        channel = {}
        playlist['playlist_id'] = item['id']['playlistId']
        playlist['title'] = item['snippet']['title']
        playlist['thumbnail'] = item['snippet']['thumbnails']['medium']['url']
        channel_id = item['snippet']['channelId']
        playlist['channel_id'] = channel_id
        channel_name, channel_thumbnail = get_channel_info(channel_id)
        duration, pl_videos = get_playlists_videos_and_duration(playlist['playlist_id'])
        playlist['duration'] = duration
        channel['id'] = channel_id
        channel['name'] = channel_name
        channel['thumbnail'] = channel_thumbnail
        channels.append(channel)
        playlists.append(playlist)
        videos.append(pl_videos)
    
    return playlists, videos, channels

def get_channel_info(channel_id: str):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    items = request.execute()['items']
    channel_name = items[0]['snippet']['title']
    channel_pic = items[0]['snippet']['thumbnails']['default']['url']
    return channel_name, channel_pic

def get_duration(minutes: str) -> str:
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)} hours {int(minutes)} minutes" if hours > 0 else f"{minutes} minutes"

def fill_database(*args):
    for keywords in args:
        ans = get_playlists_items(keywords)
        playlists, all_videos, channels = get_playlist_videos_channels(ans)
        for channel in channels:
            id_ = channel['id']
            name = channel['name']
            thumbnail = channel['thumbnail']
            try:
                c = Channel(
                        id = id_,
                        name = name,
                        thumbnail = thumbnail,
                )
                c.save()
            except Exception as e:
                print(f"Error creating channel {c} ")
                raise Exception(e)

        for playlist in playlists:
            id = playlist['playlist_id']
            total_mins = playlist['duration']
            title = playlist['title']
            thumbnail = playlist['thumbnail']
            channelId = playlist['channel_id']

            channel = Channel.objects.get(id=channelId)

            try:
                p = Playlist( 
                        id=id,
                        total_mins=total_mins,
                        title=title,
                        thumbnail=thumbnail,
                        channel = channel
                    )
                p.save()
            except Exception as e:
                print(f"ERROR creating playlist: {playlist}")
                raise Exception(e)
        
        for videos in all_videos:
            for id, details in videos.items():
                if details.get('title') == 'Private video' or not 'duration' in details.keys():
                    continue
                total_mins = details['duration']
                title = details['title']
                thumbnail = details['thumbnail']['default']
                playlist_id = details['playlist_id']
                url = details['url']
                playlists = Playlist.objects.filter(id=playlist_id)
                
                try:
                    vd = Video(
                        id=id,
                        total_mins=total_mins,
                        title=title,
                        thumbnail=thumbnail,
                        url=url)
                    vd.save()
                    for p in playlists:
                        vd.playlist.add(p)
                    vd.save()
                except Exception as e:
                    print(f"ERROR creating video : {vd}")
                    raise Exception(e)




def get_video_mins_duration(duration: str) -> int:
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')

    hours = hours_pattern.search(duration)
    minutes = minutes_pattern.search(duration)
    seconds = seconds_pattern.search(duration)

    hours = int(hours.group(1)) if hours else 0
    minutes = int(minutes.group(1)) if minutes else 0
    seconds = int(seconds.group(1) if seconds else 0)

    total_seconds = timedelta(
        hours = hours,
        minutes = minutes,
        seconds = seconds
    ).total_seconds()

    minutes, seconds = divmod(total_seconds, 60)
    return minutes


def get_playlists_videos_and_duration(playlist_id: str) -> int:
    next_page_token = None
    videos = {}
    total_mins = 0
    while True: 
        pl_request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()
        

        ids = []
        for item in pl_response['items']:
            video = {}
            video['title'] = item['snippet']['title']
            # video['description'] = item['snippet']['description']
            video['thumbnail'] = item['snippet']['thumbnails']

            video['playlist_id'] = playlist_id
            id_video = item['snippet']['resourceId']['videoId']
            videos[id_video] = video 
            ids.append(id_video)
            

        vid_request = youtube.videos().list(
            part="contentDetails, player",
            id=",".join(ids)
        )

        vid_response = vid_request.execute()
        for video in vid_response['items']:
            if video['id'] not in videos:
                continue
            
            id = video['id']
            duration = get_video_mins_duration(video['contentDetails']['duration'])
            videos[id]['duration'] = duration
            iframe_string = video['player']['embedHtml']
            match = re.search(r'//([a-zA-Z0-9./_-]+)"', iframe_string)
            src = match.group(1)
            total_mins += duration    
            videos[id]['url'] = '//'+src    

        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break
    
    return total_mins, videos
        
    