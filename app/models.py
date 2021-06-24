from app import db
import datetime
import random


def gen_short_uuid():
	return "-".join("".join(random.choice('0123456789abcdefghjklmnopqrstuvwxyz') for _ in range(4)) for _ in range(3))


vol_dept_link = db.Table('vol_dept_link', 
    db.Column('volunteer_id', db.Integer, db.ForeignKey('volunteer.id')),
    db.Column('department_id', db.Integer, db.ForeignKey('department.id'))
)

vol_pres_link = db.Table('vol_pres_link', 
    db.Column('volunteer_id', db.Integer, db.ForeignKey('volunteer.id')),
    db.Column('presence_id', db.Integer, db.ForeignKey('presence.id'))
)

class Volunteer(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	name					= db.Column(db.String(256))
	surname					= db.Column(db.String(256))
	callsign				= db.Column(db.String(256))
	phone					= db.Column(db.String(256))
	email					= db.Column(db.String(256))
	photo					= db.Column(db.BLOB)
	short_uuid 				= db.Column(db.String(256), default=gen_short_uuid())
	volunteer_type_id		= db.Column(db.Integer, db.ForeignKey('volunteer_type.id'), nullable=False)
	feed_type_id			= db.Column(db.Integer, db.ForeignKey('feed_type.id'), nullable=False)
	ref_to_id				= db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=True)
	has_signed_approval		= db.Column(db.Integer)

	department				= db.relationship('Department', secondary=vol_dept_link)
	presence				= db.relationship('Presence', secondary=vol_pres_link)
	volunteer_type			= db.relationship('Volunteer_type', backref='volunteers')
	feed_type				= db.relationship('Feed_type', backref='volunteers')
	ref_to					= db.relationship('Volunteer')


	def __repr__(self):
		return u"{} {} ({})".format(self.name, self.surname, self.callsign)


class Volunteer_type(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	code					= db.Column(db.String(3))
	name					= db.Column(db.String(256))

	def __repr__(self):
		return self.name


class Presence(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	arrival					= db.Column(db.DateTime)
	departure				= db.Column(db.DateTime)
	transport_type_id		= db.Column(db.Integer, db.ForeignKey('transport_type.id'), nullable=False)
	needToMeet				= db.Column(db.Integer, default=0)

	transport_type			= db.relationship('Transport_type')

	def __repr__(self):
		return "{} - {}".format(self.departure, self.departure)


class Transport_type(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	name					= db.Column(db.String(256))

	def __repr__(self):
		return self.name


class QR_Codes(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	volunteer_id			= db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
	code					= db.Column(db.String(256))
	is_active 				= db.Column(db.Integer, default=0)
	is_valid				= db.Column(db.Integer, default=0)

	volunteer				= db.relationship('Volunteer')


class Department(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	name					= db.Column(db.String(256))
	is_federal				= db.Column(db.Integer, default=0)
	lead_id 				= db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)

	lead					= db.relationship('Volunteer')


	def __repr__(self):
		return self.name


class Feed_type(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	code					= db.Column(db.String(3))
	name					= db.Column(db.String(256))
	daily_amount			= db.Column(db.Integer)
	clear_before_add		= db.Column(db.Integer)

	def __repr__(self):
		return self.name


class Feed_balance(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	volunteer_id			= db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
	balance 				= db.Column(db.Integer)

	volunteer				= db.relationship('Volunteer')


class Feed_transaction(db.Model):
	id						= db.Column(db.Integer, primary_key=True)
	volunteer_id			= db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
	trhash					= db.Column(db.String(256))
	amount 					= db.Column(db.Integer)
	hwo 					= db.Column(db.String(256))
	dtime					= db.Column(db.DateTime, default=datetime.datetime.utcnow)


	volunteer				= db.relationship('Volunteer')















