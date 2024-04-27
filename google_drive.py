import os
import pickle

from PyQt5.QtWidgets import (
    QFileDialog
)
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class MyDrive:
    def __init__(self):
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        scopes = ['https://www.googleapis.com/auth/drive']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)

    def create_remote_folder(self, folder_name):
        body = {
            'name': folder_name,
            'mimeType': "application/vnd.google-apps.folder"
        }
        root_folder = self.service.files().create(body=body).execute()
        print(f'Folder named:{folder_name} created with id {root_folder['id']}\n')
        return root_folder['id']

    def get_folder_id(self, folder_name):
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        response = self.service.files().list(q=query, fields="files(id)").execute()
        files = response.get('files', [])
        if files:
            return files[0]['id']
        else:
            return None

    def upload_file(self, filename, parent_id):
        media = MediaFileUpload(filename)
        file_metadata = {
            'name': os.path.basename(filename),
            'parents': [parent_id]
        }
        file = self.service.files().create(
            body=file_metadata, media_body=media, fields='id').execute()
        print(f"A new file was created {file.get('id')}")

    def upload_directory(self, directory, parent_id):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if not item.startswith('.'):
                if os.path.isfile(item_path):
                    self.upload_file(item_path, parent_id)
                elif os.path.isdir(item_path):
                    folder_id = self.get_folder_id(item)
                    if folder_id is None:
                        folder_id = self.create_remote_folder(item)
                    self.upload_directory(item_path, folder_id)
                    self.move_file_to_parent(folder_id, parent_id)

    def move_file_to_parent(self, file_id, parent_id):
        file = self.service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        file = self.service.files().update(fileId=file_id,
                                           addParents=parent_id,
                                           removeParents=previous_parents,
                                           fields='id, parents').execute()

    def select_directory(self, folder_name):
        directory = QFileDialog.getExistingDirectory(None, "Select Directory to Backup")
        if directory:
            folder_id = self.get_folder_id(folder_name)
            if folder_id is None:
                folder_id = self.create_remote_folder(folder_name)
            self.upload_directory(directory, folder_id)

    def select_file(self, folder_name):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File to Backup", "", "All Files (*.*);;")
        if file_path:
            folder_id = self.get_folder_id(folder_name)
            if folder_id is None:
                folder_id = self.create_remote_folder(folder_name)
            self.upload_file(file_path, folder_id)
