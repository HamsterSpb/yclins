#coding=utf-8

from app.models import QR_Codes
from app import db

with open('./to_activate_qr.txt', 'r') as f:
	lines = f.readlines()
	for l in lines:
		q = QR_Codes.query.filter(QR_Codes.code == l.strip()).all()
		if len(q) > 0:
			print "ok"
			q.is_active = 1
		else:
			print "error: {}".format(l.strip())
	db.session.commit()