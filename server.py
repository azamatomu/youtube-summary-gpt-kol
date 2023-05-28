import os
import json
from dotenv import load_dotenv

from flask import Flask, request

import google.oauth2.credentials
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

load_dotenv()

from helpers import save_data, insert_comment


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
YOUR_API_KEY = os.getenv('API_KEY')
APP_VERSION = 0.1

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret_desktopapp.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
# credentials = flow.run_console()
credentials = flow.run_local_server(port=0)

YOUTUBE = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

app = Flask(__name__)

@app.route('/summarize', methods=['GET'])
def summarize():
    # Code to retrieve comment based on videoId
    videoId = request.args.get('videoId')
    print(videoId)

    yt_request, comment, transcript = insert_comment(videoId, YOUTUBE)
    save_data(videoId, comment, transcript, APP_VERSION)

    response = yt_request.execute()

    return json.dumps({'success': True, 'videoId': videoId, 'comment': comment})

@app.route('/test', methods=['GET'])
def test():
    summary = 'hello'
    print(summary)
    return json.dumps({'success': True, 'summary': summary})



if __name__ == '__main__':
    
    app.run(debug=True)