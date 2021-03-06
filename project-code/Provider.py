from boxsdk import JWTAuth
from boxsdk import Client
from cloudmesh.management.configuration.config import Config
import os


class Provider(object):

    def __init__(self):
        self.config = Config()
        credentials = self.config.credentials("storage", "box")
        self.sdk = JWTAuth.from_settings_file(credentials['config_path'])
        self.client = Client(self.sdk)

    def put(self, filename, folder):
        folders = self.client.search().query(folder, type='folder')
        if len(folders) > 0:
            folder_id = folders[0].id
            items = self.client.folder(folder_id).get_items()
            if not any(item.name == filename for item in items):
                file = self.client.folder(folder_id).upload_file(filename)
            else:
                file_ind = next((index for (index, item) in enumerate(items) if item.name == filename), None)
                file_id = folders[file_ind].id
                file = self.client.file(file_id).update_contents(filename)
            return file.__dict__
        else:
            print("Folder not found.")

    def get(self, filename, destination):
        items = self.client.search().query(filename, type='file')
        if len(items) > 0 & items[0].name == filename:
            file_id = items[0].id
            file = self.client.file(file_id).get()
            with open(destination+"/"+filename, 'wb') as f:
                self.client.file(file_id).download_to(f)
            return file.__dict__
        else:
            print("File not found.")

    def delete(self, filename):
        items = self.client.search().query(filename, type='file')
        if len(items) > 0 & items[0].name == filename:
            file_id = items[0].id
            self.client.file(file_id).delete()
        else:
            print("File not found.")

    def size(self, filename):
        items = self.client.search().query(filename, type='file', fields=['size'])
        if len(items) > 0:
            return items[0].__dict__
        else:
            print("File not found.")

    def info(self, filename):
        items = self.client.search().query(filename, type='file')
        if len(items) > 0:
            file_id = items[0].id
            file = self.client.file(file_id).get()
            return file.__dict__
        else:
            print("File not found.")

    def sync(self, source, dest):
        files = []
        for file in os.listdir(source):
            self.put(file, dest)
            files.append(file)
        return files

    def search(self, filename):
        items = self.client.search().query(filename, type='file')
        files = []
        for item in items:
            files.append(item.__dict__)
        return files

    def add(self, folder, parent):
        folders = self.client.search.query(parent, type='folder')
        if len(folders) > 0:
            parent = folders[0].id
            folder = self.client.folder(parent).create_subfolder(folder)
            return folder.__dict__
        else:
            print("Parent directory not found.")

