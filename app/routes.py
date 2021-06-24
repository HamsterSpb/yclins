#coding=utf-8

from app import app, db, gsheet
from flask import render_template, url_for, redirect, session, request,  flash
from app.models import Volunteer, Volunteer_type, Feed_type, Feed_transaction, Feed_balance, QR_Codes

import datetime
import json
import math
import random


@app.route('/')
def index():
	return "Hello world"


@app.route('/import')
def import_sheet():

	to_import = gsheet.do_import()

	depts = list(dict.fromkeys(map(lambda x: x["dept"], to_import)))

	for o in to_import:

	return "All ok"


@app.route('/update_balance')
def update_balance():

	qry = db.session.query(Volunteer, Feed_balance).outerjoin(Feed_balance).all()

	for o in qry:
		vol = o[0]

		if o[1] is None:
			fb = Feed_balance()
			fb.volunteer = vol
			fb.balance = 0
			db.session.add(fb)
		else:
			fb = o[1]

		balance = fb.balance
		ft = vol.feed_type

		if ft.clear_before_add == 1:
			if balance != 0:
				ftt = Feed_transaction()
				ftt.volunteer = vol
				ftt.amount = balance*(-1)
				ftt.hwo = "auto"
				ftt.dtime = datetime.datetime.now()
				db.session.add(ftt)
			fb.balance = 0
		fb.balance = fb.balance + ft.daily_amount
		if ft.daily_amount > 0:
			ftt = Feed_transaction()
			ftt.volunteer = vol
			ftt.hwo = "auto"
			ftt.amount = ft.daily_amount
			ftt.dtime = datetime.datetime.now()
			db.session.add(ftt)

	db.session.commit()
	
	return "Update success"


@app.route('/get_vol_list')
def get_vol_list():
	qry = db.session.query(Volunteer, Feed_balance, QR_Codes).outerjoin(Feed_balance)\
		.outerjoin(QR_Codes)\
		.filter(QR_Codes.is_active == 1)\
		.filter(QR_Codes.is_valid == 1).all()
	res = []
	for o in qry:
		vol = o[0]
		fb = o[1]
		qr = o[2]
		res.append({
			u"id": vol.id,
			u"name": vol.name,
			u"surname": vol.surname,
			u"callsign": vol.callsign,
			u"qr": qr.code,
			u"balance": 0 if fb is None else fb.balance
			})

	return (json.dumps(res, ensure_ascii=False)).encode('utf-8')


@app.route("/load_transactions", methods=['POST'])
def load_transactions():
	dta = json.loads(request.data)
	to_upd_bal = {}
	for entry in dta:
		ft = Feed_transaction()
		ft.volunteer_id = entry["vol_id"]
		ft.amount = (-1)*abs(entry["amount"])
		ft.hwo = "sync"
		ft.dtime = datetime.datetime.fromtimestamp(entry["timestamp"] / 1e3)
		db.session.add(ft)
		if entry["vol_id"] not in to_upd_bal:
			to_upd_bal[entry["vol_id"]] = ft.amount
		else:
			to_upd_bal[entry["vol_id"]] -= ft.amount


	fbs = Feed_balance.query.filter(Feed_balance.volunteer_id.in_(to_upd_bal)).all()
	for fb in fbs:
		fb.balance += to_upd_bal[str(fb.volunteer_id)]
		del to_upd_bal[str(fb.volunteer_id)]
	for k in to_upd_bal:
		fb = Feed_balance()
		fb.volunteer_id = int(k)
		fb.balance = to_upd_bal[k]
		db.session.add(fb)

	
	db.session.commit()



@app.route('/scaff')
def scaffold():
	vols_types = [
		{
			"code": "VT1",
			"name": "Ordinar volunteer"
		}
	]

	Volunteer_type.query.delete()
	for o in vols_types:
		vt = Volunteer_type()
		vt.name = o["name"]
		vt.code = o["code"]
		db.session.add(vt)


	feed_types = [
		{
			"code": "FT1",
			"name": "Eat while work",
			"daily_amount": 4,
			"clear_before_add": 1
		},
		{
			"code": "FT2",
			"name": "Fixed balance",
			"daily_amount": 0,
			"clear_before_add": 0
		}
	]

	Feed_type.query.delete()
	for o in feed_types:
		ft = Feed_type()
		ft.name = o["name"]
		ft.code = o["code"]
		ft.daily_amount = o["daily_amount"]
		ft.clear_before_add = o["clear_before_add"]

		db.session.add(ft)

	db.session.commit()

	vols = [
		{
			u"name": u"Мария",
			u"surname": u"Манькова",
			u"callsign": u"Маняша",
			u"phone": u"+79032128506",
			u"email": u"ya@maffka.ru",
			u"_vol_type": u"VT1",
			u"_feed_type": u"FT1"
		},
		{
			u"name": u"Станислав",
			u"surname": u"Раташнюк",
			u"callsign": u"Ладога",
			u"phone": u"+78122325465",
			u"email": u"i@ladoga.ru",
			u"_vol_type": u"VT1",
			u"_feed_type": u"FT1"
		},
		{
			u"name": u"Евгений",
			u"surname": u"Шульц",
			u"callsign": u"Хомяк",
			u"phone": u"+79112238276",
			u"email": u"homa@yandex.ru",
			u"_vol_type": u"VT1",
			u"_feed_type": u"FT2"
		}
	]

	Volunteer.query.delete()
	for o in vols:
		vo = Volunteer()
		vo.name = o["name"]
		vo.surname = o["surname"]
		vo.callsign= o["callsign"]
		vo.phone= o["phone"]
		vo.email= o["email"]
		vo.volunteer_type = Volunteer_type.query.filter(Volunteer_type.code == o["_vol_type"]).first()
		vo.feed_type = Feed_type.query.filter(Feed_type.code == o["_feed_type"]).first()

		db.session.add(vo)

	db.session.commit()

	return "All ok"















