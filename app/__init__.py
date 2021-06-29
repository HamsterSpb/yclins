#coding=utf-8


from flask import Flask, session, request
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

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

    @expose("/")
    def index(self):
        return self.render('admin/index.html')

    @expose("/checkin")
    def checkin(self):
    	return self.render('admin/checkin.html')


admin = Admin(app, name=u'Админка волонтеров', template_mode='bootstrap3', index_view=HomeView(name=u"Пульт управления"))



class ImageBlob(fields.StringField):
    pass


class VolView(ModelView):
    column_list = ('name', 'surname', 'callsign', 'email', 'phone')
    column_searchable_list = ('name', 'surname', 'callsign', 'email', 'phone')

    column_extra_row_actions = [
        EndpointLinkRowAction("glyphicon glyphicon-qrcode", ".link_qr"),
    ]

    @expose("/link_qr", methods=("GET",))
    def link_qr(self):
        if request.args.has_key("id"):
            vol_id = request.args.get("id")
            return self.render('admin/link_qr.html', vol_id=vol_id)
        else:
            return self.render('admin')

    #form_columns = ('blob')


admin.add_view(VolView(model=Volunteer, session=db.session, name=u'Волонтеры'))
admin.add_view(ModelView(Volunteer_type, db.session, name=u"Типы волонтеров"))
admin.add_view(ModelView(Presence, db.session, name=u"Присутствие на полигоне", category=u'Присутствие'))
admin.add_view(ModelView(Transport_type, db.session, name=u"Типы транспорта", category=u'Присутствие'))
admin.add_view(ModelView(Department, db.session, name=u"Направления"))
admin.add_view(ModelView(QR_Codes, db.session, name=u"QR коды"))
admin.add_view(ModelView(Feed_type, db.session, name=u"Виды питания", category=u'Питание'))
admin.add_view(ModelView(Feed_transaction, db.session, name=u"История транзакций питания", category=u'Питание'))
admin.add_view(ModelView(Feed_balance, db.session, name=u"Баланс питания", category=u'Питание'))


from app import routes










