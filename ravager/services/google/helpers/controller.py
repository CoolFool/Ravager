import google.oauth2.credentials as google_credential
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from ravager.config import OAUTH_URL, CLIENT_CONFIG


class GoogleController:
    def __init__(self):
        self.redirect_uri = OAUTH_URL + "/oauth_handler"
        self.authorization_url = None
        self.state = None
        self.refresh_token = None
        self.CLIENT_CONFIG = CLIENT_CONFIG
        self.scopes = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.metadata']

    def get_oauth_url(self, state=None):
        self.state = state
        flow = Flow.from_client_config(
            client_config=self.CLIENT_CONFIG,
            scopes=self.scopes)
        flow.redirect_uri = self.redirect_uri
        self.authorization_url, self.state = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true',
            state=self.state)
        return self.authorization_url

    def credentials_handler(self, refresh_token=None):
        self.refresh_token = refresh_token
        google_creds = google_credential.Credentials(
            token=None,
            refresh_token=self.refresh_token,
            client_id=self.CLIENT_CONFIG["web"]["client_id"],
            client_secret=self.CLIENT_CONFIG["web"]["client_secret"],
            token_uri=self.CLIENT_CONFIG["web"]["token_uri"])
        return google_creds

    @staticmethod
    def get_shared_drive_list(google_auth_creds=None, next_page_token=None):
        drive = build(serviceName="drive", version="v3", credentials=google_auth_creds, cache_discovery=False)
        shared_drives = drive.drives().list(pageSize=5, pageToken=next_page_token).execute()
        shared_drives_list = []
        if "nextPageToken" in shared_drives:
            next_page_token = shared_drives["nextPageToken"]
        for i in shared_drives["drives"]:
            shared_drives_list.append(i)
        return shared_drives_list, next_page_token
