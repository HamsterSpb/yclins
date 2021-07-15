#coding=utf-8

import csv

with open('./names.csv', 'r') as f:
	c = csv.reader(f, delimiter=";")
	fl = True
	for r in c:
		if len(r) < 2:
			continue
		_id = r[1]
		_fio = r[0].strip()
		_nparts = _fio.split(" ")
		if len(_nparts) < 2:
			continue
		print "{};{};{}".format(_nparts[0], _nparts[1], _id)