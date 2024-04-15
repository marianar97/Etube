from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from googleapiclient.discovery import build
from pathlib import Path
from configparser import ConfigParser
from datetime import timedelta
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from .models import CourseVideo, Playlist, Profile, Video, Channel, Course, UserCourse
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialToken, SocialAccount
from google.oauth2.credentials import Credentials


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


def get_youtube(token):
    client_id = CONFIG.get("ClientSecret", "client_id")
    client_secret = CONFIG.get("ClientSecret", "client_secret")
    token_uri = "https://oauth2.googleapis.com/token"
    credentials = Credentials(
        token=token,
        # refresh_token=refresh_token,
        token_uri=token_uri,  # This is the token endpoint from Google's OAuth server
        client_id=client_id,
        client_secret=client_secret,
        scopes=['https://www.googleapis.com/auth/youtube.readonly']
    )
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def get_user_playlists(youtube):
    """Fetches the user's YouTube playlists."""
    try:
        # This will get the first page of playlists
        request = youtube.playlists().list(
            part="snippet,contentDetails",  # part specifies the properties to be included in response objects
            maxResults=50,  # Adjust the number of results per page
            mine=True  # Set this to True to retrieve playlists of the authenticated user
        )
        return request.execute()['items']  # Executes the request
    except Exception as e:
        # print("An error occurred: %s" % e)
        return None

@login_required
def user_playlists(request):
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    social_account = SocialAccount.objects.get(user=request.user, provider='google')
    token = SocialToken.objects.get(account=social_account)
    access_token = token.token
    youtube = get_youtube(access_token)
    user_playlists_items = get_user_playlists(youtube)
    if not user_playlists_items: #user doesn't have any playlists
        print("no playlists")
        return render(request, 'socialnetwork/playlists.html', {'picture': extra_data['picture']})
    else:
        _update_playlists(request, user_playlists_items)
        home_playlists = request.user.playlist_set.all()
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
        context = {'items': info, 'picture': extra_data['picture']}
        return render(request, 'socialnetwork/playlists.html', context)


def _update_playlists(request, user_playlists_items):
    playlists_to_update = []
    for playlist in user_playlists_items:
        try:
            print(f"request user: {request.user.playlist_set.all()}")
            playlist = request.user.playlist_set.get(id=playlist['id'])
            if not playlist:
                playlists_to_update.append(playlist)
        except Exception as e:
            pass
    
    if playlists_to_update:
        playlists, videos, channels = _get_users_videos(playlists_to_update, youtube)
        save_channels(channels)
        save_playlists(playlists, user=request.user)
        save_videos(videos)

def _get_users_videos(playlists_items, youtube):

    # print(f"playlist_items: {playlists_items}")
    # print("\n"*3)

    # return 
    playlists = []
    videos = []
    channels = []
    
    for item in playlists_items:
        try: 
            playlist = {}
            channel = {}
            playlist['playlist_id'] = item['id']
            playlist['title'] = item['snippet']['title']
            playlist['thumbnail'] = item['snippet']['thumbnails']['medium']['url']
            playlist['channel_id'] = item['snippet']['channelId']
            # print(f"item id: {item['id']}, title: {playlist['title']}")
            channel_name, channel_thumbnail = get_channel_info(playlist['channel_id'])
            duration, pl_videos = _get_videos_of_user_playlists_and_duration(playlist['playlist_id'], youtube)
            duration, pl_videos
            playlist['duration'] = duration
            channel['id'] = playlist['channel_id']
            channel['name'] = channel_name
            channel['thumbnail'] = channel_thumbnail
            channels.append(channel)
            playlists.append(playlist)
            videos.append(pl_videos)
        except Exception as e:
            print(f"Exception in _get_users_videos: {e}")
            continue
    
    return playlists, videos, channels

def _get_videos_of_user_playlists_and_duration(playlist_id, youtube):
    next_page_token = None
    videos = {}
    total_mins  = 0

    while True:
        pl_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50  # You can fetch up to 50 items per request
        )

        pl_response = pl_request.execute()
        # print(f"pl_response: {len(pl_response)}")

        ids = []
        for item in pl_response['items']:
            # print(f"item: {item}")
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


@login_required                  
def home(request):
    home_playlists = Playlist.objects.all()
    info = []
    for playlist in home_playlists:
        if request.user.playlist_set.filter(id=playlist.id).exists():
            continue
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
    
    if Profile.objects.filter(user=request.user).count() == 0:
        new_user_profile = Profile.objects.create(user = request.user, picture = extra_data['picture'])
        username = request.user.username
        # print(f"creating new profile with username={username}")
        new_user_profile.save()
    
    return render(request, 'socialnetwork/home.html', context)

def login_view(request):
    return render(request, 'socialnetwork/login.html')

def register_view(request):
    return render(request, 'socialnetwork/register.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))

@login_required
def profile_view(request, username):
    # print(f"data: {SocialAccount.objects.get(user=request.user).extra_data}")
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    context = {'picture': extra_data['picture']}
    profile = get_object_or_404(Profile, user=request.user)
    if username == request.user.username:
        context['user_info'] = extra_data
        number_of_following = profile.following.count()
        context['number_following'] = number_of_following
        context['profile'] = profile
        return render(request, 'socialnetwork/profile.html', context)
    else:
        user = User.objects.get(username=username)
        user_info = SocialAccount.objects.get(user=user).extra_data
        profile = get_object_or_404(Profile, user=user)
        context = {'user': user, 'profile': profile, 'picture': extra_data['picture'], 'user_info':user_info}
        return render(request, 'socialnetwork/other_profile.html', context)

@login_required
def course_view(request, playlist_id):
    video_id = request.GET.get("v")
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    playlist = Playlist.objects.get(id=playlist_id)
    videos_in_playlist = Video.objects.filter(playlist__id=playlist_id)
    
    # convert the playlist to a course and save it
    course = Course(
            id = playlist.id + request.user.username,
            total_mins = playlist.total_mins,
            title = playlist.title,
            thumbnail = playlist.thumbnail,
            channel = playlist.channel
    )
    course.save()

    # add the many to many relationship and set the percentage completed to 0
    user_course, _ = UserCourse.objects.get_or_create(course=course, user=request.user)
    user_course.save()

    #connect the videos with the course and set the videos to unwatched and cur_secs to 0
    for video in videos_in_playlist:
        course_video, _ = CourseVideo.objects.get_or_create(course=course, video=video)
    
    first_video = Video.objects.get(id=video_id) if video_id else None

    videos = []
    for i, video in enumerate(videos_in_playlist):
        print(f"video {i}: {video.title}")
        v = {}
        v['id'] = video.id 
        v['title'] = video.title 
        cv = CourseVideo.objects.get(course=course, video=video)
        watched = cv.watched
        if not first_video and cv.watched==False:
            first_video = video
        v['watched'] = watched
        videos.append(v)

    if not first_video: first_video = videos_in_playlist[0]

    print(f"first video: {first_video}")
    context = {'course': course, 'picture': extra_data['picture'], 'videos': videos, 'fvideo':first_video}
    return render(request, 'socialnetwork/course.html', context=context)

@login_required
def unfollow(request, username):
    user = User.objects.get(username=username)

    # add user
    request.user.profile.following.remove(user)
    request.user.profile.save()

    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    user = User.objects.get(username=username)
    user_info = SocialAccount.objects.get(user=user).extra_data
    profile = get_object_or_404(Profile, user=user)
    context = {'user': user, 'profile': profile, 'picture': extra_data['picture'], 'user_info':user_info}
    return render(request, 'socialnetwork/other_profile.html', context)

@login_required
def follow(request, username):
    user = User.objects.get(username=username)

    # add user
    request.user.profile.following.add(user)
    request.user.profile.save()

    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    user = User.objects.get(username=username)
    user_info = SocialAccount.objects.get(user=user).extra_data
    profile = get_object_or_404(Profile, user=user)
    context = {'user': user, 'profile': profile, 'picture': extra_data['picture'], 'user_info':user_info}
    return render(request, 'socialnetwork/other_profile.html', context)

def video_watched(request):
    video_id = request.POST.get('videoId')
    course_id = request.POST.get('courseId')

    print(f"got video watched, video_id: {video_id}, course_id: {course_id}")

    video = get_object_or_404(Video, id=video_id)
    course = get_object_or_404(Course, id=course_id)
    course_video = get_object_or_404(CourseVideo, course=course, video=video)

    course_video.watched = True
    course_video.cur_secs = 0 # if watched start from the beggining
    course_video.save()
    response_data = {
        'status': 200,
        'message': 'Video updated as watched',
        'videoId': video_id,
        'courseId': course_id
    }
    return JsonResponse(response_data)

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
        save_channels(channels)
        save_playlists(playlists)
        save_videos(all_videos)

def save_channels(channels: list):
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
            # print(f"Error creating channel {c} ")
            raise Exception(e)
            
def save_playlists(playlists: list, user: User):
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
            if user:
                p.user.add(user)
        except Exception as e:
            # print(f"ERROR creating playlist: {playlist}")
            raise Exception(e)

def save_videos(all_videos: list):
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
                # print(f"ERROR creating video : {vd}")
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

def get_playlists_videos_and_duration(playlist_id: str):
    # print(f"searching for playlist with id {playlist_id}")
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
        
    