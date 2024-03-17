from django.shortcuts import render
from googleapiclient.discovery import build
from pathlib import Path
from configparser import ConfigParser
from datetime import timedelta
import re


home_playlists = []
CONFIG = ConfigParser()
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG.read(BASE_DIR / "config.ini")
API_KEY =  CONFIG.get("Django", "secret")

youtube = build('youtube', 'v3', developerKey="AIzaSyBV-BZ5NyoTzSMvVbSxeB2WnBrHJbno7tA")

home_playlists = [{'playlist_id': 'PL8dPuuaLjXtNlUrzyH5r6jN9ulIgZBpdo', 'title': 'Computer Science', 'thumbnail': 'https://i.ytimg.com/vi/tpIctyqH29Q/mqdefault.jpg', 'channel_name': 'CrashCourse', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_lg5FWsf908Wgf_VJAHb9Kmt0JLP1ZHLNcR1QL7jQ=s88-c-k-c0x00ffffff-no-rj', 'duration': '7.0H54.0M'}, {'playlist_id': 'PLEbnTDJUr_IcPtUXFy2b1sGRPsLFMghhS', 'title': 'Compiler Design - GATE Co...', 'thumbnail': 'https://i.ytimg.com/vi/Qkwj65l_96I/mqdefault.jpg', 'channel_name': 'Ravindrababu Ravula', 'channel_thumbnail': 'https://yt3.ggpht.com/sU1WSe4rymN_DdgTbyIQBQvn2qXxlemHg0EmTM3qKoP286D2XdGkh9AfYsf19t3mu5HygLPWflA=s88-c-k-c0x00ffffff-no-rj', 'duration': '9.0H40.0M'}, {'playlist_id': 'PLKKfKV1b9e8r_GAb4BQNc2ZSh6S7NwK9W', 'title': 'Python for Class 12', 'thumbnail': 'https://i.ytimg.com/vi/f2PMfGfBOPo/mqdefault.jpg', 'channel_name': 'Apni Kaksha', 'channel_thumbnail': 'https://yt3.ggpht.com/ihsWXKohHPRkXNqYSaTvO548Lbcc2eCexL3GoYP8JQw_-SzZwA0-xvg2EFVuxUmnU0TDTRc6mW0=s88-c-k-c0x00ffffff-no-rj', 'duration': '7.0H29.0M'}, {'playlist_id': 'PLUl4u3cNGP63WbdFxL8giv4yhgdMGaZNA', 'title': '6.0001 Introduction to Co...', 'thumbnail': 'https://i.ytimg.com/vi/nykOeWgQcHM/mqdefault.jpg', 'channel_name': 'MIT OpenCourseWare', 'channel_thumbnail': 'https://yt3.ggpht.com/e1KUKBD5xAGuyy68Y-q3JECx8XkRGYSZLy9DbZfaVZuDPiaTFbgrc67j5VYFBpvQdu8K-xVBTw=s88-c-k-c0x00ffffff-no-rj', 'duration': '9.0H58.0M'}, {'playlist_id': 'PLqftY2uRk7oXvERQEgATSr-KzAh8WLW_D', 'title': 'NPTEL: Joy of computing u...', 'thumbnail': 'https://i.ytimg.com/vi/Y3Ri2GdYfYg/mqdefault.jpg', 'channel_name': 'RAY P', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_mZ_A7F4nl6SMfLtST9VZoCM-eeo31WwcJDyKy8KA=s88-c-k-c0x00ffffff-no-rj', 'duration': '32.0H11.0M'}, {'playlist_id': 'PLhQjrBD2T3817j24-GogXmWqO5Q5vYy0V', 'title': 'CS50&#39;s Introduction t...', 'thumbnail': 'https://i.ytimg.com/vi/OvKCESUCWII/mqdefault.jpg', 'channel_name': 'CS50', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_mgE42XQIRxm6pgYMt7sxQOXK04s5QfOJGHgWlQYA=s88-c-k-c0x00ffffff-no-rj', 'duration': '15.0H54.0M'}, {'playlist_id': 'PLu0W_9lII9agiCUZYRsvtGTXdxkzPyItg', 'title': 'Web Development Tutorials...', 'thumbnail': 'https://i.ytimg.com/vi/6mbwJ2xhgzM/mqdefault.jpg', 'channel_name': 'CodeWithHarry', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_krnyU9zev1u94JYs4opG8p1sYE3HQ9oButitIb7A=s88-c-k-c0x00ffffff-no-rj', 'duration': '34.0H43.0M'}, {'playlist_id': 'PLu0W_9lII9agS67Uits0UnJyrYiXhDS6q', 'title': 'Java Tutorials For Beginn...', 'thumbnail': 'https://i.ytimg.com/vi/ntLJmHOJ0ME/mqdefault.jpg', 'channel_name': 'CodeWithHarry', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_krnyU9zev1u94JYs4opG8p1sYE3HQ9oButitIb7A=s88-c-k-c0x00ffffff-no-rj', 'duration': '28.0H42.0M'}, {'playlist_id': 'PLfqMhTWNBTe3LtFWcvwpqTkUSlB32kJop', 'title': 'Java &amp; DSA Course for...', 'thumbnail': 'https://i.ytimg.com/vi/yRpLlJmRo2w/mqdefault.jpg', 'channel_name': 'Apna College', 'channel_thumbnail': 'https://yt3.ggpht.com/nhDLqeIgXMJBDIrX2bXavvHoWX0tsslDEh7k2xZ1P0W8b_CMRVigp2kxJubYEVwBcBlogZDe=s88-c-k-c0x00ffffff-no-rj', 'duration': '33.0H17.0M'}, {'playlist_id': 'PLu0W_9lII9ahR1blWXxgSlL4y9iQBnLpR', 'title': 'JavaScript Tutorials for ...', 'thumbnail': 'https://i.ytimg.com/vi/ER9SspLe4Hg/mqdefault.jpg', 'channel_name': 'CodeWithHarry', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_krnyU9zev1u94JYs4opG8p1sYE3HQ9oButitIb7A=s88-c-k-c0x00ffffff-no-rj', 'duration': '21.0H36.0M'}, {'playlist_id': 'PLS1QulWo1RIbfTjQvTdj8Y6yyq4R7g-Al', 'title': 'Java Tutorial For Beginne...', 'thumbnail': 'https://i.ytimg.com/vi/r59xYe3Vyks/mqdefault.jpg', 'channel_name': 'ProgrammingKnowledge', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_nMWm0WLqhrA2F1FkijY3gfzCcxGIy6i-O_uydd=s88-c-k-c0x00ffffff-no-rj', 'duration': '70.0H1.0M'}, {'playlist_id': 'PL0b6OzIxLPbx-BZTaWu_AF7hsKo_Fvsnf', 'title': '🏆 JavaScript Tutorial for...', 'thumbnail': 'https://i.ytimg.com/vi/Lgxgm-T9cgA/mqdefault.jpg', 'channel_name': 'Yahoo Baba', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_lqWM4aCcSildu1MHHwJrFgZiz10M0RQ89HKijp0A=s88-c-k-c0x00ffffff-no-rj', 'duration': '14.0H28.0M'}, {'playlist_id': 'PLBZBJbE_rGRV8D7XZ08LK6z-4zPoWzu5H', 'title': 'Data Structures and Algor...', 'thumbnail': 'https://i.ytimg.com/vi/bum_19loj9A/mqdefault.jpg', 'channel_name': 'CS Dojo', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_mHrx1EUAmidqrqL2epGhd8UqnFtBpvTJqbcV-H=s88-c-k-c0x00ffffff-no-rj', 'duration': '3.0H57.0M'}, {'playlist_id': 'PLeo1K3hjS3uu_n_a__MI_KktGTLYopZ12', 'title': 'Data Structures And Algor...', 'thumbnail': 'https://i.ytimg.com/vi/_t2GVaQasRY/mqdefault.jpg', 'channel_name': 'codebasics', 'channel_thumbnail': 'https://yt3.ggpht.com/DZidE7P_ESU8Y_dZ5_PrTAItOkSuayCfE2tYkKCnjtFYes7nA2sE-UF1fi3tZLjozlg0h1aK=s88-c-k-c0x00ffffff-no-rj', 'duration': '6.0H11.0M'}, {'playlist_id': 'PLoROMvodv4rPLKxIpqhjhPgdQy7imNkDn', 'title': 'Stanford CS224W: Machine ...', 'thumbnail': 'https://i.ytimg.com/vi/JAB_plj2rbA/mqdefault.jpg', 'channel_name': 'Stanford Online', 'channel_thumbnail': 'https://yt3.ggpht.com/j8Gqr1z_an8WEyAIXRdkPKdaYbnxCSLwPEZb9tF-YHk6sNyvWDCWAzNxM_NAbbOmpF8_99ytWQ=s88-c-k-c0x00ffffff-no-rj', 'duration': '22.0H23.0M'}, {'playlist_id': 'PLD63A284B7615313A', 'title': 'Machine Learning Course -...', 'thumbnail': 'https://i.ytimg.com/vi/mbyG85GZ0PI/mqdefault.jpg', 'channel_name': 'caltech', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_mYkenz8rKQq30FgLsfnrnhRX7KqMrL8XUhyAX2ig=s88-c-k-c0x00ffffff-no-rj', 'duration': '23.0H36.0M'}, {'playlist_id': 'PL-b5Zp9H7qBgrtYJ3YEO0wFI3Ua243-nA', 'title': 'Structure Machine 1', 'thumbnail': 'https://i.ytimg.com/vi/eH9w-olOBI0/mqdefault.jpg', 'channel_name': 'cours informatique Mahseur', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_ni79Yu4BJErKAS7A3GlGT8ugS3P8t9z4o2bZ1c=s88-c-k-c0x00ffffff-no-rj', 'duration': '6.0H11.0M'}, {'playlist_id': 'PLBlnK6fEyqRgWh1emltdMOz8O2m5X3YYn', 'title': 'Stacks | Chapter-6 | Data...', 'thumbnail': 'https://i.ytimg.com/vi/I37kGX-nZEI/mqdefault.jpg', 'channel_name': 'Neso Academy', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_l8suTYCkHO_NBVXwg8-hYAQj_G2KsYprx-qH8S=s88-c-k-c0x00ffffff-no-rj', 'duration': '7.0H54.0M'}, {'playlist_id': 'PL23C220A2C5EC0FDE', 'title': 'ALL REACT EPISODES EVER M...', 'thumbnail': 'https://i.ytimg.com/vi/YOlzwYz0wMw/mqdefault.jpg', 'channel_name': 'REACT', 'channel_thumbnail': 'https://yt3.ggpht.com/3qmO1ZC01p1b9FEeGX9kfr9ZoWIcIvGa98-0KsQBwepeysw92A1yLk2N8FA-qW06gIx4CrUpdTg=s88-c-k-c0x00ffffff-no-rj', 'duration': '419.0H14.0M'}, {'playlist_id': 'PLu0W_9lII9agiCUZYRsvtGTXdxkzPyItg', 'title': 'Web Development Tutorials...', 'thumbnail': 'https://i.ytimg.com/vi/6mbwJ2xhgzM/mqdefault.jpg', 'channel_name': 'CodeWithHarry', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_krnyU9zev1u94JYs4opG8p1sYE3HQ9oButitIb7A=s88-c-k-c0x00ffffff-no-rj', 'duration': '34.0H43.0M'}, {'playlist_id': 'PLcpBBg8UA1Oxz7973OVcCzyBR-caH7hCQ', 'title': 'Quentin Tarantino&#39;s D...', 'thumbnail': 'https://i.ytimg.com/vi/OhlVBpEnjig/mqdefault.jpg', 'channel_name': 'Django Unchained OST', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_mO3hB9I8ZlK9zyIXSOaMFRrEgr0NRkK88Tx9kd=s88-c-k-c0x00ffffff-no-rj', 'duration': '46.0 mins'}, {'playlist_id': 'PLC3y8-rFHvwgg3vaYJgHGnModB54rxOk3', 'title': 'ReactJS Tutorial for Begi...', 'thumbnail': 'https://i.ytimg.com/vi/QFaFIcGhPoM/mqdefault.jpg', 'channel_name': 'Codevolution', 'channel_thumbnail': 'https://yt3.ggpht.com/os7Yw6RimtysXXpc8NrXraci87TjXgZSUQyAezi0D3RrNL3YP5riIwi1-0al4Wz0XwzH6oBu6g=s88-c-k-c0x00ffffff-no-rj', 'duration': '14.0H34.0M'}, {'playlist_id': 'PLu0W_9lII9ahR1blWXxgSlL4y9iQBnLpR', 'title': 'JavaScript Tutorials for ...', 'thumbnail': 'https://i.ytimg.com/vi/ER9SspLe4Hg/mqdefault.jpg', 'channel_name': 'CodeWithHarry', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_krnyU9zev1u94JYs4opG8p1sYE3HQ9oButitIb7A=s88-c-k-c0x00ffffff-no-rj', 'duration': '21.0H36.0M'}, {'playlist_id': 'PL0b6OzIxLPbx-BZTaWu_AF7hsKo_Fvsnf', 'title': '🏆 JavaScript Tutorial for...', 'thumbnail': 'https://i.ytimg.com/vi/Lgxgm-T9cgA/mqdefault.jpg', 'channel_name': 'Yahoo Baba', 'channel_thumbnail': 'https://yt3.ggpht.com/ytc/AIdro_lqWM4aCcSildu1MHHwJrFgZiz10M0RQ89HKijp0A=s88-c-k-c0x00ffffff-no-rj', 'duration': '14.0H28.0M'}]
def home(request):
    topics1 = ['computer science', 'algorithms', 'web development', 'python']
    topics2 = ['compilers', 'java', 'javascript', 'numpy', 'sklearn']
    topics3 = ['Machine Learning', 'Large Lenguage Models', 'Data Structures'] 
    topics4 = ['React', 'Django Web development', 'CSS', 'Javascript']
    # home_playlists = get_all_playlists(topics1, topics2, topics3, topics4)
    # print('playlists')
    # print()
    # print(home_playlists)
    context = {'items': home_playlists}
    return render(request, 'socialnetwork/home.html', context)

def login(request):
    return render(request, 'socialnetwork/login.html')


def get_query(keywords: list):
    query = ""
    for topic in keywords[:-2]:
        query += topic + " | "
    query += keywords[-1]
    return query

def get_playlists_items(topics):
    query = get_query(topics)
    request = youtube.search().list(
        part="snippet",
        maxResults=6,
        order="viewCount",
        q=query,
        type="playlist"
    )
    return request.execute()['items']

def get_playlist(items):
    playlists = []
    for item in items:
        playlist = {}
        playlist['playlist_id'] = item['id']['playlistId']
        playlist['title'] = item['snippet']['title'][:25]+ "..." if len(item['snippet']['title']) > 26 else item['snippet']['title']
        playlist['thumbnail'] = item['snippet']['thumbnails']['medium']['url']
        channel_id = item['snippet']['channelId']
        playlist['channel_name'], playlist['channel_thumbnail'] = get_channel_info(channel_id)
        playlist['duration'] = get_playlist_duration(playlist['playlist_id'])
        playlists.append(playlist)
    
    return playlists

def get_channel_info(channel_id: str):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    items = request.execute()['items']
    channel_name = items[0]['snippet']['title']
    channel_pic = items[0]['snippet']['thumbnails']['default']['url']
    return channel_name, channel_pic

def get_all_playlists(*args):
    items = []
    for keywords in args:
        ans = get_playlists_items(keywords)
        playlist = get_playlist(ans)
        items.extend(playlist)
    return items

def get_playlist_duration(playlist_id: str):
    next_page_token = None
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')
    total_seconds = 0
    while True: 
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()
        vid_ids = [item['contentDetails']['videoId'] for item in pl_response['items']]

        vid_request = youtube.videos().list(
            part="contentDetails",
            id=",".join(vid_ids)
        )
        vid_response = vid_request.execute()

        for item in vid_response['items']:
            duration = item['contentDetails']['duration']

            hours = hours_pattern.search(duration)
            minutes = minutes_pattern.search(duration)
            seconds = seconds_pattern.search(duration)

            hours = int(hours.group(1)) if hours else 0
            minutes = int(minutes.group(1)) if minutes else 0
            seconds = int(seconds.group(1) if seconds else 0)

            video_seconds = timedelta(
                hours = hours,
                minutes = minutes,
                seconds = seconds
            ).total_seconds()

            total_seconds += video_seconds

        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}H{minutes}M" if hours > 0 else f"{minutes} mins"




        
    