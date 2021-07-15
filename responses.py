import io
import gspread
import constants
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials


sheets = {}
global service


def load_data():
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', constants.SCOPES)
    client = gspread.authorize(creds)

    sheets['points'] = client.open('points').sheet1
    sheets['students'] = client.open('students').sheet1
    sheets['P'] = client.open('pages').sheet1
    sheets['S'] = client.open('sections').sheet1

    global service
    service = Create_Service(
        constants.CLIENT_SECRET_FILE,
        constants.API_NAME, 
        constants.API_VERSION, 
        constants.SCOPES
    )


def get_row(username):
    try:
        row = int(username[1:])
        if row > sheets['students'].row_count:
            raise Exception
    except Exception:
        return 0
    return row


def validate_user(username, password):
    if (username, password) in constants.ADMIN:
        return username

    row = get_row(username)
    if row:
        data = sheets['students'].row_values(row)
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
    row = get_row(username)
    if row:
        data = sheets['points'].row_values(row)
        if data[0].lower() == username.lower():
            return int(data[1])
    return 0


def get_file(username, file_type):
    fh = io.BytesIO()
    row = get_row(username)
    sheet = sheets.get(file_type, None)

    if not row or not sheet:
        return False, fh

    data = sheet.row_values(row)
    if username.lower() == data[0].lower():
        request = service.files().get_media(fileId=data[1])
        downloader = MediaIoBaseDownload(fd=fh, request=request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        fh.seek(0)
        fh.name = f'{username.upper()}_{file_type}.pdf'
        return True, fh

    return False, fh
