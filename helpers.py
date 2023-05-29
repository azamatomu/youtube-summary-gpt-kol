import os
import pickle

import pandas as pd

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from summarizer import summarize_with_gpt

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def pickle_file_name(
        api_name = 'youtube',
        api_version = 'v3'):
    return f'token_{api_name}_{api_version}.pickle'

def load_credentials(
        api_name = 'youtube',
        api_version = 'v3'):
    pickle_file = pickle_file_name(
        api_name, api_version)

    if not os.path.exists(pickle_file):
        return None

    with open(pickle_file, 'rb') as token:
        return pickle.load(token)

def save_credentials(
        cred, api_name = 'youtube',
        api_version = 'v3'):
    pickle_file = pickle_file_name(
        api_name, api_version)

    with open(pickle_file, 'wb') as token:
        pickle.dump(cred, token)

def create_service(
        client_secret_file, scopes,
        api_name = 'youtube',
        api_version = 'v3'):
    print(client_secret_file, scopes,
        api_name, api_version,
        sep = ', ')

    cred = load_credentials(api_name, api_version)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, scopes)
            cred = flow.run_console()

    save_credentials(cred, api_name, api_version)

    try:
        service = build(api_name, api_version, credentials = cred)
        print(api_name, 'service created successfully')
        return service
    except Exception as e:
        print(api_name, 'service creation failed:', e)
        return None

def get_video_transcript(videoId):

    # retrieve the available transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)
    tmp_text = None

    # iterate over all available transcripts
    for transcript in transcript_list:
        # the Transcript object provides metadata properties
        print(
            transcript.video_id,
            transcript.language,
            transcript.language_code,
            # whether it has been manually created or generated by YouTube
            transcript.is_generated,
            # whether this transcript can be translated or not
            transcript.is_translatable,
            # a list of languages the transcript can be translated to
            # transcript.translation_languages,
        )

        # # fetch the actual transcript data
        if transcript.language_code == 'en':
            print('in1')
            if not transcript.is_generated:
                print('in2')
                text = ' '.join([t['text'].replace('\n', ' ') for t in transcript.fetch()])
                return text
            else:
                tmp_text = transcript.fetch()
                text = ' '.join([t['text'].replace('\n', ' ') for t in tmp_text])
                continue

    if tmp_text is not None:
        return text

def load_data(api_name):
    if not os.path.exists(api_name):
        return None

    with open(api_name, 'r') as file:
        return pd.read_csv(file)


def save_data(videoId, comment, transcript, app_version):    
    file_name = 'db.csv'
    db = load_data(file_name)
        
    row = pd.DataFrame([{'videoId': videoId, 'transcript': transcript, 'summary': comment, 'summary_version': app_version}])
    if not db:
        pd.concat([db, row]).to_csv(file_name, index=False)
    else:
        row.to_csv(file_name, index=False)
    return

def insert_comment(videoId, youtube):
    transcript = get_video_transcript(videoId)
    print(transcript)
    comment = summarize_with_gpt(transcript)
    print(comment)

    yt_request = youtube.commentThreads().insert(
        part="snippet",
        body={
          "snippet": {
            "videoId": videoId,
            "topLevelComment": {
              "snippet": {
                "textOriginal": comment
              }
            }
          }
        }
    )

    return yt_request, comment, transcript