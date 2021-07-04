import qrcode

from app.models import QR_Codes


qrs = QR_Codes.query.all()

for q in qrs:
	i = qrcode.make(q.code)
	i.save('./qrs/{}.png'.format(q.code))