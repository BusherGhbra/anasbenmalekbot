import io
import gspread
import constants
import pandas as pd
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

service = Create_Service(constants.CLIENT_SECRET_FILE, constants.API_NAME, constants.API_VERSION, constants.SCOPE)

query = f"parents = '{constants.DRIVE_FOLDER}'"
result = service.files().list(q=query).execute()
files = result.get('files')
nextPageToken = result.get('nextPageToken')

while nextPageToken:
    result = service.files().list(q=query).execute()
    files.extend(result.get(files))
    nextPageToken = result.get('nextPageToken')


pdfs = pd.DataFrame(files)
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', constants.SCOPE)
client = gspread.authorize(creds)

points = client.open('points').sheet1
students = client.open('students').sheet1


def validate_user(username, password):
    for row in range(2, students.row_count + 1):
        if students.cell(row, 1).value == username and students.cell(row, 2).value == password:
            return True
    return False


def logged_in(context, username):
    return context.user_data.get(username, False)


def get_points(username):
    for row in range(2, points.row_count + 1):
        if points.cell(row, 1).value == username:
            return int(points.cell(row, 2).value)
    return 0


def get_pages(username):
    fh = io.BytesIO()
    for file_name, file_id in zip(pdfs['name'], pdfs['id']):
        if file_name == f'{username}_P.pdf':
            request = service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(fd=fh, request=request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            fh.seek(0)
            fh.name = file_name
            break

    return fh


def get_sections(username):
    fh = io.BytesIO()
    for file_name, file_id in zip(pdfs['name'], pdfs['id']):
        if file_name == f'{username}_S.pdf':
            request = service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(fd=fh, request=request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            fh.seek(0)
            fh.name = file_name
            break

    return fh


