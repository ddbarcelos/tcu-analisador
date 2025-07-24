from flask_sqlalchemy import SQLAlchemy

# Instancia global do banco
# Usada em app.py e export_excel.py

db = SQLAlchemy()

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contratante = db.Column(db.String(120), nullable=False)
    objeto = db.Column(db.String(150), nullable=False)
    assinatura = db.Column(db.Date, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    aviso_dias = db.Column(db.Integer, default=60)
