#coding=utf-8

from app import app, db, gsheet
from flask import render_template, url_for, redirect, session, request, flash, send_from_directory
from app.models import Volunteer, Volunteer_type, Feed_type, Feed_transaction, Feed_balance, QR_Codes, Department, Presence, User
from sqlalchemy import and_

import datetime
import json
import math
import random

import hashlib
import uuid
import bcrypt


def alyonka_deco(func):
	def wrapper(*args, **kwargs):
		try:
			func(*args, **kwargs)
		except:
			print("[deco] Trying to flush connections and retry func...")
			Volunteer.query.session.close()
			Volunteer_type.query.session.close()
			Feed_type.query.session.close()
			Feed_transaction.query.session.close()
			Feed_balance.query.session.close()
			QR_Codes.query.session.close()
			Department.query.session.close()
			func(*args, **kwargs)

	return wrapper


@app.route('/')
def index():
	if 'login' not in session:
		return redirect('/login')
	else:
		return redirect('/admin')


@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == "POST":
		login = request.form["user"]
		password = request.form["pwd"]
		_v = User.query.filter(and_(
			User.login == login
		)).first()
		if _v is not None:
			if bcrypt.checkpw(password.encode('utf-8'), _v.password_hash.encode('utf-8')):
				session['login'] = login
				session["userid"] = _v.id
				return redirect('/')
	return render_template("login.html")


@app.route('/qr/<path:path>')
def send_qr(path):
	return send_from_directory('../qrs', path)


@app.route('/import')
def import_sheet():

	to_import = gsheet.do_import()

	depts = dict.fromkeys(map(lambda x: x["department"], to_import))
	depts_db = Department.query.all()

	_qrs = list(dict.fromkeys(map(lambda x: x["qr"], to_import)))
	qrs = dict.fromkeys(map(lambda x: x.code, QR_Codes.query.filter(QR_Codes.code.in_(_qrs))))

	for d in depts_db:
		if d.name in depts:
			depts[d.name] = d

	for d in depts.keys():
		if depts[d] == None:
			d_db = Department()
			d_db.name = d
			db.session.add(d_db)
			depts[d] = d_db

	ft_free = Feed_type.query.filter(Feed_type.code == "FT1").all()[0]
	ft_other = Feed_type.query.filter(Feed_type.code == "FT2").all()[0]
	ft_child = Feed_type.query.filter(Feed_type.code == "FT3").all()[0]

	vt_ord = Volunteer_type.query.filter(Volunteer_type.code == "VT1").all()[0]
	vt_org = Volunteer_type.query.filter(Volunteer_type.code == "VT2").all()[0]


	for o in to_import:
		if o["qr"] in qrs:
			continue
		print(o["qr"])
		_vol = Volunteer()
		_vol.name = o["name"]
		_vol.surname = o["surname"]
		_vol.callsign = o["callsign"]
		_vol.photo = o["photo"]
		_vol.department.append(depts[o["department"]])

		if o["feed_type"] == "free":
			_vol.feed_type = ft_free
		elif o["feed_type"] == u"Ребенок":
			_vol.feed_type = ft_child
		else:
			_vol.feed_type = ft_other

		if o["department"] == u"Организатор":
			_vol.volunteer_type = vt_org
		else:
			_vol.volunteer_type = vt_ord


		db.session.add(_vol)

		_q = QR_Codes()
		_q.code = o["qr"]
		_q.is_valid = 1
		_q.volunteer = _vol
		db.session.add(_q)

	db.session.commit()


	return "All ok"


@app.route('/qrgen/<int:qrcou>')
def qrgen(qrcou):
	res = []
	for i in range(0, qrcou):
		_uuid = uuid.uuid1()
		_hash = hashlib.sha1(str(_uuid)).hexdigest()[:8]
		res.append(_hash)
	return "<br>".join(res)


@alyonka_deco
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


@alyonka_deco
@app.route('/get_vol_list')
def get_vol_list():
	qry = db.session.query(Volunteer, Feed_balance, QR_Codes).outerjoin(Feed_balance)\
		.outerjoin(QR_Codes).all()
	res = []
	for o in qry:
		vol = o[0]
		fb = o[1]
		qr = o[2]
		if qr is None:
			continue
		res.append({
			u"id": vol.id,
			u"name": vol.name,
			u"surname": vol.surname,
			u"callsign": vol.callsign,
			u"qr": qr.code,
			u"balance": 0 if fb is None else fb.balance,
			u"is_active": qr.is_active,
			u"is_valid": qr.is_valid,
			u"feed_type": vol.feed_type.code
			});

	return (json.dumps(res, ensure_ascii=False)).encode('utf-8')


@alyonka_deco
@app.route('/activate_vol', methods=['POST'])
def activate_vol():
	dta = json.loads(request.data)
	qr = dta["qr"]

	_qv = QR_Codes.query.filter(QR_Codes.code == qr).all()
	if len(_qv) > 0:
		_qv[0].is_active = 1
		db.session.commit()
		return u'{{"res": "ok", "name": "{}"}}'.format(_qv[0].volunteer.name)
	
	return u'{"res": "error"}'


@app.route('/open_by_qr/<string:qr>')
def open_by_qr(qr):
	q = QR_Codes.query.filter(QR_Codes.code == qr).all()
	if len(q) > 0:
		return redirect('/admin/volunteer/edit/?url=%2Fadmin%2Fvolunteer%2F&id={}'.format(q[0].volunteer.id))
	else:
		return redirect('admin/volunteer/')


@app.route('/open_qr/<string:qr>')
def open_qr(qr):
	q = QR_Codes.query.filter(QR_Codes.code == qr).all()
	if len(q) > 0:
		return redirect('/admin/qr_codes/edit/?url=%2Fadmin%2Fqr_codes%2F&id={}'.format(q[0].id))
	else:
		return redirect('admin/qr_codes/')


@alyonka_deco
@app.route('/link_vol_to_badge', methods=['POST'])
def link_to_badge():
	dta = json.loads(request.data)
	vol_id = dta["vol_id"]
	qr = dta["qr"]

	print("qr: {}, vol_id: {}".format(qr, vol_id))

	_v = Volunteer.query.get(vol_id)

	_qv = QR_Codes.query.filter(QR_Codes.volunteer_id == vol_id).all()
	for o in _qv:
		o.is_valid = 0
		o.is_active = 0

	_q = QR_Codes.query.filter(QR_Codes.code == qr).all()

	if len(_q) > 0:
		_q[0].is_valid = 1
		_q[0].is_active = 1
		_q[0].volunteer = _v
	else:
		_q = QR_Codes()
		_q.is_valid = 1
		_q.is_active = 1
		_q.code = qr
		_q.volunteer = _v
		db.session.add(_q)
	db.session.commit()

	return '{"res": "ok"}'


@alyonka_deco
@app.route("/load_transactions", methods=['POST'])
def load_transactions():

	hashes = list(dict.fromkeys(map(lambda x: x.trhash, Feed_transaction.query.all())))

	dta = json.loads(request.data)
	to_upd_bal = {}
	for entry in dta:
		if entry["trhash"] in hashes:
			continue
		ft = Feed_transaction()
		ft.volunteer_id = entry["vol_id"]
		ft.amount = (-1)*abs(entry["amount"])
		ft.hwo = "sync"
		ft.dtime = datetime.datetime.fromtimestamp(entry["timestamp"] / 1e3)
		ft.trhash = entry["trhash"]
		db.session.add(ft)
		if entry["vol_id"] not in to_upd_bal:
			to_upd_bal[str(entry["vol_id"])] = ft.amount
		else:
			to_upd_bal[str(entry["vol_id"])] -= ft.amount


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

	return "{'res': 'success'}"


@app.route('/scaff')
def scaffold():
	vols_types = [
		{
			"code": "VT1",
			"name": "Ordinar volunteer"
		},
		{
			"code": "VT2",
			"name": "ORG"
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















