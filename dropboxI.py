import os

import dropbox
from dropbox.exceptions import AuthError


class MyDropbox:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.oauth2_access_token = None
        self.dbx = None
        self.authorize()

    def authorize(self):
        flow = dropbox.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        authorize_url = flow.start()
        print("1. Go to:", authorize_url)
        print("2. Click 'Allow' (you might have to log in first)")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        try:
            oauth_result = flow.finish(auth_code)
            self.oauth2_access_token = oauth_result.access_token
            print("Authorization successful!")
        except AuthError as e:
            print('Error: %s' % (e,))
            return

        self.dbx = dropbox.Dropbox(self.oauth2_access_token)

    def create_remote_folder(self, folder_name):
        try:
            response = self.dbx.files_create_folder_v2(folder_name)
            print(f"Folder '{folder_name}' created successfully")
            return response.metadata.id
        except dropbox.exceptions.ApiError as err:
            print(f"Error creating folder '{folder_name}': {err}")
            return None

    def upload_file(self, local_file_path, dropbox_destination):
        try:
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            self.dbx.files_upload(file_content, dropbox_destination)
            print(f"File uploaded successfully to {dropbox_destination}")
        except dropbox.exceptions.ApiError as err:
            print(f"Error uploading file to '{dropbox_destination}': {err}")

    def upload_directory(self, local_directory, dropbox_destination):
        for item in os.listdir(local_directory):
            item_path = os.path.join(local_directory, item)
            if os.path.isfile(item_path):
                dropbox_file_path = os.path.join(dropbox_destination, item)
                dropbox_file_path = dropbox_file_path.replace('\\', '/')
                self.upload_file(item_path, dropbox_file_path)
                print(f"Uploaded file '{item}' to Dropbox at '{dropbox_file_path}'")
            elif os.path.isdir(item_path):
                folder_name = os.path.basename(item_path)
                folder_id = self.create_remote_folder(f"{dropbox_destination}/{folder_name}")
                if folder_id:
                    self.upload_directory(item_path, f"{dropbox_destination}/{folder_name}")
