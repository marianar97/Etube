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
topics1 = ['computer science', 'algorithms', 'web development', 'python']
topics2 = ['compilers', 'java', 'javascript', 'numpy', 'sklearn']
topics3 = ['Machine Learning', 'Large Lenguage Models', 'Data Structures'] 
topics4 = ['React', 'Django Web development', 'CSS', 'Javascript']
                                                                             
@login_required                  
def home(request):
    home_playlists = Playlist.objects.all()
    info = []
    for playlist in home_playlists:
        el = {}
        el['title'] = playlist.title if len(playlist.title) < 26 else playlist.title[:24]+'...'
        el['playlist_thumbnail'] = playlist.thumbnail
        el['duration'] = get_duration(playlist.total_mins)
        c = Channel.objects.get(id=playlist.channel_id)
        el['channel_thumbnail'] = c.thumbnail
        el['channel_name'] = c.name
        info.append(el)
    
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    context = {'items': info, 'picture': extra_data['picture']}
    return render(request, 'socialnetwork/home.html', context)

def login_view(request):
    return render(request, 'socialnetwork/login.html')

def register_view(request):
    return render(request, 'socialnetwork/register.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))

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
        type="playlist"
    )
    return request.execute()['items']

def get_playlist_videos_channels(items: list):
    playlists = []
    channels = []
    for item in items:
        playlist = {}
        channel = {}
        playlist['playlist_id'] = item['id']['playlistId']
        playlist['title'] = item['snippet']['title']
        playlist['thumbnail'] = item['snippet']['thumbnails']['medium']['url']
        channel_id = item['snippet']['channelId']
        playlist['channel_id'] = channel_id
        channel_name, channel_thumbnail = get_channel_info(channel_id)
        duration, videos = get_playlists_videos_and_duration(playlist['playlist_id'])
        playlist['duration'] = duration
        channel['id'] = channel_id
        channel['name'] = channel_name
        channel['thumbnail'] = channel_thumbnail
        channels.append(channel)
        playlists.append(playlist)
    
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
        playlists, videos, channels = get_playlist_videos_channels(ans)

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
                print("Error: ", e)
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
                print("ERROR: ", playlist)
                raise Exception(e)
        
        for id, details in videos.items():
            total_mins = details['duration']
            title = details['title']
            thumbnail = details['thumbnail']['default']
            playlist = Playlist.objects.filter(id=id)
            
            try:
                vd = Video(
                    id=id,
                    total_mins=total_mins,
                    title=title,
                    thumbnail=thumbnail)
                vd.save()
                vd.playlist.add(playlist)
                vd.save()
            except Exception as e:
                print("ERROR: ", playlist)
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

            video['playlistId'] = playlist_id
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
            videos[id]['embedHtml'] = video['player']['embedHtml']
            total_mins += duration        

        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break
    
    return total_mins, videos
        
    