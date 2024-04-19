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

youtube = build('youtube', 'v3', developerKey=CONFIG.get("Django", "api_key"))
topics1 = ['computer science', 'algorithms']
topics2 = ['compilers', 'java', 'javascript', 'numpy', 'sklearn']
topics3 = ['Machine Learning', 'Large Lenguage Models', 'Data Structures'] 
topics4 = ['React', 'Django Web development', 'CSS', 'Javascript']
topics5 = ['web development', 'python']

@login_required
def all_user_courses_view(request):
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    user_courses = UserCourse.objects.filter(user=request.user)
    not_started = []
    in_progress = []
    done = []
    for user_course in user_courses:
        # print(f"% completed {user_course.perc_completed}" )
        course = user_course.course
        el = {}
        el['id'] = course.id
        el['title'] = course.title if len(course.title) < 26 else course.title[:24]+'...'
        el['course_thumbnail'] = course.thumbnail
        el['duration'] = get_duration(course.total_mins)
        c = Channel.objects.get(id=course.channel_id)
        el['channel_thumbnail'] = c.thumbnail
        el['channel_name'] = c.name
        if user_course.perc_completed == 0:
            not_started.append(el)
        elif user_course.perc_completed == 1:
            done.append(el)
        else:
            in_progress.append(el)

    # print(f"Not started: {not_started}")
    # print(f"In progress: {in_progress}")
    # print(f"done: {done}")
    context = {'picture': extra_data['picture'], 'not_started': not_started, 'in_progress': in_progress, 'done': done, 'tab':'my_courses'}
    return render(request, 'socialnetwork/user_courses.html', context)

@login_required
def user_playlists(request):
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    social_account = SocialAccount.objects.get(user=request.user, provider='google')
    token = SocialToken.objects.get(account=social_account)
    access_token = token.token
    youtube = get_youtube(access_token)
    user_playlists_items = get_user_playlists(youtube)
    if not user_playlists_items: #user doesn't have any playlists
        return render(request, 'socialnetwork/playlists.html', {'picture': extra_data['picture'], 'tab': 'user_playlists'})
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
        context = {'items': info, 'picture': extra_data['picture'], 'tab':'user_playlists'}
        return render(request, 'socialnetwork/playlists.html', context)

@login_required                  
def home(request):
    if not SocialAccount.objects.filter(user=request.user).exists():
        # Redirect the user to a page indicating they need to link a social account
        return render(request, 'socialnetwork/login.html')

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
    context = {'items': info, 'picture': extra_data['picture'], 'tab':'home'}
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
        user_courses = UserCourse.objects.filter(user=request.user)
        context['num_courses'] = user_courses.count()
        return render(request, 'socialnetwork/profile.html', context)
    else:
        print(f"all users: {User.objects.all()}")
        user = User.objects.get(username=username)
        user_info = SocialAccount.objects.get(user=user).extra_data
        user_courses = UserCourse.objects.filter(user=user)
        profile = get_object_or_404(Profile, user=user)
        user_courses = UserCourse.objects.filter(user=user)
        courses = []
        for user_course in user_courses:
            # print(f"% completed {user_course.perc_completed}" )
            course = user_course.course
            el = {}
            el['id'] = course.id
            el['title'] = course.title if len(course.title) < 26 else course.title[:24]+'...'
            el['course_thumbnail'] = course.thumbnail
            el['duration'] = get_duration(course.total_mins)
            c = Channel.objects.get(id=course.channel_id)
            el['channel_thumbnail'] = c.thumbnail
            el['channel_name'] = c.name
            courses.append(el)

        context = {'user': user, 'profile': profile, 'picture': extra_data['picture'], 'user_info':user_info, 'num_courses': user_courses.count(), 'courses': courses}
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
            channel = playlist.channel,
            playlist=playlist
    )
    course.save()

    # add the many to many relationship and set the percentage completed to 0
    user_course, _ = UserCourse.objects.get_or_create(course=course, user=request.user)
    user_course.save()

    #connect the videos with the course and set the videos to unwatched and cur_secs to 0
    for i, video in enumerate(videos_in_playlist):
        course_video, _ = CourseVideo.objects.get_or_create(course=course, video=video, position=i)
        course_video.save()
    
    first_video = Video.objects.get(id=video_id) if video_id else None

    videos = []
    for i, video in enumerate(videos_in_playlist):
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

    context = {'playlist': playlist,  'course': course, 'picture': extra_data['picture'], 'videos': videos, 'fvideo':first_video, 'perc_completed': int(user_course.perc_completed * 100)}
    return render(request, 'socialnetwork/course.html', context=context)

@login_required
def user_course_video_view(request, course_id):
    print(f"course_id: {course_id}")
    video_id = request.GET.get("v")
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    course = get_object_or_404(Course, id=course_id)

    user_course = get_object_or_404(UserCourse, user=request.user, course=course)
    courses_videos = CourseVideo.objects.filter(course=course).order_by('position')

    first_video = Video.objects.get(id=video_id) if video_id else None

    videos = []
    for course_video in courses_videos:
        video = course_video.video
        v = {}
        v['id'] = video.id 
        v['title'] = video.title 
        cv = CourseVideo.objects.get(course=course, video=video)
        watched = cv.watched
        if not first_video and cv.watched==False:
            first_video = video
        v['watched'] = watched
        videos.append(v)

    if not first_video: first_video = courses_videos[0].video

    context = {'course': course, 'picture': extra_data['picture'], 'videos': videos, 'fvideo':first_video, 'perc_completed': int(user_course.perc_completed * 100)}
    return render(request, 'socialnetwork/user_course_play.html', context=context)

@login_required
def unfollow(request, username):
    user = User.objects.get(username=username)

    # add user
    request.user.profile.following.remove(user)
    request.user.profile.save()

    return redirect(reverse('profile',kwargs={'username':username}))

@login_required
def follow(request, username):
    user = User.objects.get(username=username)

    # add user
    request.user.profile.following.add(user)
    request.user.profile.save()
    return redirect(reverse('profile',kwargs={'username':username}))

def video_watched(request):
    video_id = request.POST.get('videoId')
    course_id = request.POST.get('courseId')
    
    user_course = UserCourse.objects.filter(course_id=course_id).order_by('id').first()
    if not user_course:
        # If there is at least one user with the course, get the user object
        response_data = {
            'status': 404,
            'message': f'User not found for course: {course_id}',
        }
        return JsonResponse(response_data)
    elif user_course.user.username != request.user.username:
        response_data = {
            'status': 401,
            'message': f'User is not allowed to update that course',
        }
        return JsonResponse(response_data)


    video = get_object_or_404(Video, id=video_id)
    course = get_object_or_404(Course, id=course_id)
    course_video = get_object_or_404(CourseVideo, course=course, video=video)

    course_video.watched = True
    course_video.cur_secs = 0 # if watched start from the beggining
    course_video.save()

    course_videos = CourseVideo.objects.filter(course=course)
    total_num_videos = course_videos.count()
    total_watched_videos = 0
    for cv in course_videos:
        if cv.watched == True:
            total_watched_videos +=1
    percentage_watched = total_watched_videos / total_num_videos

    user_course = get_object_or_404(UserCourse, user=request.user, course=course)
    user_course.perc_completed = percentage_watched
    user_course.save()
    
    response_data = {
        'status': 200,
        'message': 'Video updated as watched',
        'videoId': video_id,
        'courseId': course_id,
        'perc_completed': int(percentage_watched*100)
    }
    return JsonResponse(response_data)

@login_required
def all_public_courses(request):
    home_courses = Course.objects.all()
    info = []
    for course in home_courses:
        if request.user.course_set.filter(id=course.id).exists():
            continue
        el = {}
        el['id'] = course.id
        el['title'] = course.title if len(course.title) < 26 else course.title[:24]+'...'
        el['playlist_thumbnail'] = course.thumbnail
        el['duration'] = get_duration(course.total_mins)
        user = UserCourse.objects.filter(course=course).first().user
        profile = get_object_or_404(Profile, user=user)
        el['channel_thumbnail'] = profile.picture
        el['channel_name'] = user.username
        info.append(el)
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    context = {'items': info, 'picture': extra_data['picture'], 'tab':'public_courses'}
    # fill_database(topics1)
    # fill_database(topics1, topics2, topics3, topics4, topics5)
    return render(request, 'socialnetwork/all_public_courses.html', context)

@login_required
def find_playlist_id(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    playlist = course.playlist
    return redirect(reverse('course', kwargs={'playlist_id': playlist.id}))

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

def _update_playlists(request, user_playlists_items):
    playlists, videos, channels = _get_users_videos(user_playlists_items, youtube)
    save_channels(channels)
    save_playlists(playlists, user=request.user)
    save_videos(videos)

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
        print("An error occurred: %s" % e)
        return None

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
    youtube = build('youtube', 'v3', developerKey="AIzaSyDtsJ92iKmspU1G1mblmnRjmV1IjLr4LrY")
    request = youtube.search().list(
        part="snippet",
        maxResults=6,
        order="viewCount",
        q=query,
        type="playlist",
        relevanceLanguage="en"
    )
    ans = request.execute()['items']
    return ans

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
            
def save_playlists(playlists: list, user=None):
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
        