#coding=utf-8


from flask import Flask, session, request
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

import random
import string

from OpenSSL import SSL


#context = SSL.Context(SSL.PROTOCOL_TLS_SERVER)
#context.use_privatekey_file('key.pem')
#context.use_certificate_file('cert.pem')   

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db)

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))

from app.models import Volunteer, Volunteer_type, Feed_type, Feed_transaction, Feed_balance, QR_Codes, Department


class HomeView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html')

    @expose("/checkin")
    def checkin(self):
    	return self.render('admin/checkin.html')


admin = Admin(app, name=u'Админка волонтеров', template_mode='bootstrap3', index_view=HomeView(name=u"Пульт управления"))


admin.add_view(ModelView(Volunteer, db.session, name=u"Волонтеры"))
admin.add_view(ModelView(Volunteer_type, db.session, name=u"Типы волонтеров"))
admin.add_view(ModelView(Department, db.session, name=u"Направления"))
admin.add_view(ModelView(QR_Codes, db.session, name=u"QR коды"))
admin.add_view(ModelView(Feed_type, db.session, name=u"Виды питания", category=u'Питание'))
admin.add_view(ModelView(Feed_transaction, db.session, name=u"История транзакций питания", category=u'Питание'))
admin.add_view(ModelView(Feed_balance, db.session, name=u"Баланс питания", category=u'Питание'))


from app import routes



#if __name__ == '__main__':
#	context = ('key.pem', 'cert.pem')
#	app.run_server(host='0.0.0.0', port="5000", debug=True, ssl_context=context)








