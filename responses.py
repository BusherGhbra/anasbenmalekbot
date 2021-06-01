from http import server
import io
from pickle import load
import gspread
import constants
import pandas as pd
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials


global points, students, service, pdfs


def load_data():
    global points, students, service, pdfs

    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', constants.SCOPES)
    client = gspread.authorize(creds)

    points = client.open('points').sheet1
    students = client.open('students').sheet1

    service = Create_Service(
        constants.CLIENT_SECRET_FILE,
        constants.API_NAME, 
        constants.API_VERSION, 
        constants.SCOPES
    )

    query = f"parents = '{constants.DRIVE_FOLDER}'"
    result = service.files().list(q=query).execute()
    loaded_files = result.get('files')
    nextPageToken = result.get('nextPageToken')

    while nextPageToken:
        result = service.files().list(q=query).execute()
        loaded_files.extend(result.get('files'))
        nextPageToken = result.get('nextPageToken')

    pdfs = pd.DataFrame(loaded_files)


def validate_user(username, password):
    try:
        row = 2 if username.lower() in constants.ADMIN else int(username[1:]) + constants.SHEET_OFFSET
        if row > students.row_count:
            raise Exception
    except Exception:
        return ''

    data = students.row_values(row)
    if data[0].lower() == username.lower() and data[1].lower() == password.lower():
        return data[2]
    return ''


def logged_in(context, username):
    return username.lower() in context.user_data.get('users', set())


def get_keyboard(context):
    users = context.user_data.get('users', set())
    reply_keyboard = []
    for username in users:
        fullname = context.user_data.get(username, '')
        reply_keyboard.append([f'\u2985 {fullname} \u2986'])
        
    reply_keyboard.append(['تسجيل الدخول'])
    return reply_keyboard


def get_points(username):
    try:
        row = 2 if username.lower() in constants.ADMIN else int(username[1:]) + constants.SHEET_OFFSET
    except Exception:
        return 0

    data = points.row_values(row)
    if data[0].lower() == username.lower():
        return int(data[1])
    return 0


def get_file(username, file_type):
    fh = io.BytesIO()
    for file_name, file_id in zip(pdfs['name'], pdfs['id']):
        if str(file_name).lower() == f'{username}_{file_type}.pdf'.lower():
            request = service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(fd=fh, request=request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            fh.seek(0)
            fh.name = file_name
            return True, fh

    return False, fh
