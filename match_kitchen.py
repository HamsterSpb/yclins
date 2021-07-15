#coding=utf-8

import requests
import csv
import json
import re

from app.models import QR_Codes

#https://yclins.hamsterspb.xyz/get_vol_list

r = requests.get('https://yclins.hamsterspb.xyz/get_vol_list')
vols = json.loads(r.text.encode("utf-8"))

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield [unicode(cell, 'utf-8') for cell in row]

volsd = {}
volsd_r = {}
for vol in vols:
	#if vol["surname"] != u"Ефимцев":
	#	continue
	#_key = u"{}{}".format(vol["name"].strip(), vol["surname"].strip())
	_key = u"{}".format(vol["surname"].strip())
	if _key in volsd:
		volsd_r[_key] = 2 if _key not in volsd_r else volsd_r[_key] + 1
	volsd[_key] = {
		"qr": vol["qr"],
		"id": vol["id"]
	}

#print json.dumps(volsd, ensure_ascii=False)
#print json.dumps(volsd_r, ensure_ascii=False)

to_print = {}
to_print_d = {}

with open('./names_to_match.csv', 'r') as f:
	c = unicode_csv_reader(f, delimiter=";")
	#cou = 1
	for r in c:
		_name = r[0].encode("utf-8").decode('utf-8').strip()
		_surname = r[1].encode("utf-8").decode('utf-8').strip()
		#if _surname != u"Ефимцев":
		#	continue
		#cou += 1
		#print u"{} {}".format(_name, _surname)
		#_key = u"{}{}".format(_name, _surname)
		_key = u"{}".format(r[1].strip())
		#print u'"{}"'.format(_name)
		if _key in volsd_r:
			continue
		if _key in to_print:
			to_print_d[_key] = True
		if _key in volsd:
			to_print[_key] = {
				"txt": u"{};{}".format(r[2], volsd[_key]["qr"]),
				"qr": volsd[_key]["qr"]
			}

for _key in to_print:
	if _key not in to_print_d:
		#q = QR_Codes.query.filter(QR_Codes.code == to_print[_key]["qr"]).all()
		#if len(q) > 0:
		#	print u"{} {}".format(q[0].volunteer.name, q[0].volunteer.surname)
		print to_print[_key]["txt"]