import requests
import re
from rfc6266 import parse_headers
import csv

def download_file_from_google_drive(id, destination):
	URL = "https://docs.google.com/uc?export=download"

	session = requests.Session()

	response = session.get(URL, params = { 'id' : id }, stream = True)
	token = get_confirm_token(response)

	if token:
		params = { 'id' : id, 'confirm' : token }
		response = session.get(URL, params = params, stream = True)

	save_response_content(response, destination)    

def get_confirm_token(response):
	for key, value in response.cookies.items():
		if key.startswith('download_warning'):
			return value

	return None

def save_response_content(response, destination):
	CHUNK_SIZE = 32768

	with open(destination, "wb") as f:
		for chunk in response.iter_content(CHUNK_SIZE):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)


with open('./photos.csv', 'r') as f:
	c = csv.reader(f, delimiter=";")
	fl = True
	for r in c:
		if fl:
			fl = False
			continue
		print r
		fname = r[0]
		qr = r[1]
		res = re.split("\/d\/(.*)\/view", r[0])
		if len(res) <= 1:
			print(l)
		else:
			download_file_from_google_drive(res[1], "./phs/{}.png".format(qr))


