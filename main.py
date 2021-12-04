import os
import praw
import shutil
import random
from redvid import Downloader
from os.path import isfile, join
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip

# getting videos

user_agent, secret, client_id = 'get-reddit-999', 'JxoY2mXY7HZkpjXoJSeenuXcvIFmFQ', 'x1HB7m84pex5YLNJlLxXbw'
reddit = praw.Reddit(client_id=client_id, client_secret=secret, user_agent=user_agent)  
subreddit = reddit.subreddit("oddlysatisfying")

for submission in subreddit.top(time_filter='day',limit=20): 
    try:
        redit = Downloader(max_q=True, path = "oddlysatisfying")
        # reddit.path = "E:/BLOGandYT/youtube/automated-yt-redditVideos/oddlysatisfying"
        redit.url = submission.url
        redit.download()
        print(f"Downloaded -> {submission.title}\n")
    except:
        pass 

# compiling videos

path = 'VidBg'
files = os.listdir(path)
bg_img = f"{path}/{random.choice(files)}"

path = 'oddlysatisfying'
allVideos = []
for fileName in os.listdir(path):
    filePath = join(path, fileName)
    if isfile(filePath) and fileName.endswith(".mp4"):
        video_clip = VideoFileClip(filePath)
        # Video_clip = video_clip.resize(width=720)
        video_clip = video_clip.resize(height=1080)
        bg_image_clip = ImageClip(bg_img, transparent=True, duration=video_clip.duration)
        ft_image_clip = ImageClip("front.png", transparent=True, duration=video_clip.duration)
        composed_clip = CompositeVideoClip([bg_image_clip,video_clip.set_pos('center'), ft_image_clip])
        allVideos.append(composed_clip)

allVideos.append(VideoFileClip('outro.mp4'))
print("\nGetting video ready....\n")
finalclip = concatenate_videoclips(allVideos, method="compose")
finalclip.write_videofile('satisfying.mp4', threads=8, temp_audiofile="tempaudio.mp3", remove_temp=True)

# uploading videos

TOKEN_NAME = "token.json" # Don't change
SCOPES = ['https://www.googleapis.com/auth/drive']
client_secrets_file = 'googleAPI.json'

print("Handling GoogleAPI")
creds = None

if os.path.exists(TOKEN_NAME):
    creds = Credentials.from_authorized_user_file(TOKEN_NAME, SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
        creds = flow.run_console()
    # Save the credentials for the next run
    with open(TOKEN_NAME, 'w') as token:
        token.write(creds.to_json())

googleAPI = build('drive', 'v3', credentials=creds)

try:
    # delete folder from drive
    folder = open('folder_id.txt', 'r+')
    id = folder.read()
    googleAPI.files().delete(fileId=id).execute()


    # erase all data from file
    folder.seek(0)
    folder.truncate()
    folder.close()
except:
    pass


# create folder in drive
name = "Satisfying YT"
file_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder'
}
file = googleAPI.files().create(body=file_metadata, fields='id').execute()
folder_id = file.get('id')


# inserting files in folder
file_metadata = {
    'name': 'satisfying.mp4',
    'parents': [folder_id]
}
file_path = "satisfying.mp4"
media = MediaFileUpload(file_path, resumable=True)
file = googleAPI.files().create(body=file_metadata, media_body=media, fields='id').execute()


# write folder id in file
folder = open('folder_id.txt', 'w')
folder.write(folder_id)
folder.close()

print("Uploaded to your Drive!")

# deleting video file

location = 'oddlysatisfying/'
for folder in os.listdir(location):
    print(f"Folder: {folder}")
    path = os.path.join(location, folder)
    shutil.rmtree(path, ignore_errors=True, onerror=None)