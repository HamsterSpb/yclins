#coding=utf-8

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1EpcPXa36PGsxdHxGAVDEdxe5jBep5g3WjErDy64Cc2k'
SAMPLE_RANGE_NAME = u"'ForImport_values'!A2:O400"

def do_import():
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=50797)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

	service = build('sheets', 'v4', credentials=creds)

	dims = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, fields='sheets(data/rowData/values/userEnteredValue,properties(index,sheetId,title))').execute()
	sheetIndex = 0
	sheetName = dims['sheets'][sheetIndex]['properties']['title']
	lastRow = len(dims['sheets'][sheetIndex]['data'][0]['rowData'])

	# Call the Sheets API
	sheet = service.spreadsheets()
	result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
								range=SAMPLE_RANGE_NAME).execute()
	values = result.get('values', [])

	ranges = [
		{
			"arrive": "20210620",
			"dept": "20210626"
		},
		{
			"arrive": "20210627",
			"dept": "20210703"
		},
		{
			"arrive": "20210704",
			"dept": "20210710"
		},
		{
			"arrive": "20210711",
			"dept": "20210714"
		},
		{
			"arrive": "20210715",
			"dept": "20210719"
		},
		{
			"arrive": "20210720",
			"dept": "20210725"
		},
		{
			"arrive": "20210726",
			"dept": "20210730"
		},
			{
			"arrive": "20210731",
			"dept": "20210801"
		}
	]

	res = []

	if not values:
		print('No data found.')
	else:
		for row in values:
			if row[0] == '-':
				continue
			if row[0] == "#END#":
				break

			presences = []
			_cur_cont = []
			_prev_r = -1
			print(row[0])
			for i in range(7, 15):
				if row[i] == "1":
					_cur_range = ranges[(i-7)]
					if _prev_r == -1:
						_prev_r = i
					if i - _prev_r <= 1:
						_cur_cont.append(_cur_range)
					else:
						presences.append({
							"arrive": _cur_cont[0]["arrive"],
							"dept": _cur_cont[-1]["dept"]
							})
						_cur_cont = []
						_cur_cont.append(_cur_range)
					_prev_r = i
			if len(_cur_cont) > 0:
				presences.append({
					"arrive": _cur_cont[0]["arrive"],
					"dept": _cur_cont[-1]["dept"]
					})
				
			cur_vol = {
				"name": row[1],
				"surname": row[2],
				"callsign": row[3],
				"feed_type": row[4],
				"photo": row[5],
				"dept": row[6],
				"presences": presences
			}

			res.append(cur_vol)

	return res


if __name__ == '__main__':
	do_import()






