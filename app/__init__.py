#coding=utf-8


from flask import Flask, session, request, redirect, url_for
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action

from wtforms import fields
from wtforms.widgets import FileInput

import random
import string


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db)

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))

from app.models import Volunteer, Volunteer_type, Feed_type, Feed_transaction, Feed_balance, QR_Codes, Department, Presence, Transport_type


from flask_admin.model.template import EndpointLinkRowAction

class HomeView(AdminIndexView):

    def is_accessible(self):
        if 'login' in session:
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    @expose("/")
    def index(self):
        return self.render('admin/index.html')

    @expose("/checkin")
    def checkin(self):
    	return self.render('admin/checkin.html')


admin = Admin(app, name=u'Админка волонтеров', template_mode='bootstrap3', index_view=HomeView(name=u"Пульт управления"))


class QRView(ModelView):
    column_searchable_list = (Volunteer.name, Volunteer.surname, Volunteer.callsign, 'code')
    page_size = 500
    @action('activate', 'Activate', u'Активировать коды')
    def batch_activate(self, ids):
        qrs = QR_Codes.query.filter(QR_Codes.id.in_(ids)).all()
        for q in qrs:
            q.is_active = True
        db.session.commit()



class FBView(ModelView):
    column_searchable_list = (Volunteer.name, Volunteer.surname, Volunteer.callsign)


class FTView(ModelView):
    column_searchable_list = (Volunteer.name, Volunteer.surname, Volunteer.callsign)


class VolView(ModelView):
    column_list = ('name', 'surname', 'callsign', 'email', 'phone')
    column_searchable_list = ('name', 'surname', 'callsign', 'email', 'phone')
    page_size = 500

    column_extra_row_actions = [
        EndpointLinkRowAction("glyphicon glyphicon-qrcode", ".link_qr"),
    ]

    def is_accessible(self):
        if 'login' in session:
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    @expose("/link_qr", methods=("GET",))
    def link_qr(self):
        if request.args.has_key("id"):
            vol_id = request.args.get("id")
            return self.render('admin/link_qr.html', vol_id=vol_id)
        else:
            return self.render('admin')


class AssessModelView(ModelView):
    def is_accessible(self):
        if 'login' in session:
            return True
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


admin.add_view(VolView(model=Volunteer, session=db.session, name=u'Волонтеры'))
admin.add_view(AssessModelView(Volunteer_type, db.session, name=u"Типы волонтеров"))
admin.add_view(AssessModelView(Presence, db.session, name=u"Присутствие на полигоне", category=u'Присутствие'))
admin.add_view(AssessModelView(Transport_type, db.session, name=u"Типы транспорта", category=u'Присутствие'))
admin.add_view(AssessModelView(Department, db.session, name=u"Направления"))
admin.add_view(QRView(QR_Codes, db.session, name=u"QR коды"))
admin.add_view(AssessModelView(Feed_type, db.session, name=u"Виды питания", category=u'Питание'))
admin.add_view(FTView(Feed_transaction, db.session, name=u"История транзакций питания", category=u'Питание'))
admin.add_view(FBView(Feed_balance, db.session, name=u"Баланс питания", category=u'Питание'))


from app import routes










