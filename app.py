from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from dotenv import load_dotenv
import os
from models import db, Contract
from export_excel import export_contracts

# Carrega variaveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///contracts.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')

db.init_app(app)

@app.template_filter('days_left')
def days_left(vencimento):
    delta = (vencimento - date.today()).days
    return delta

@app.route('/')
def index():
    contracts = Contract.query.all()
    return render_template('contracts.html', contracts=contracts)

@app.route('/add', methods=['POST'])
def add_contract():
    data = request.json or request.form
    contract = Contract(
        contratante=data['contratante'],
        objeto=data['objeto'],
        assinatura=datetime.strptime(data['assinatura'], '%Y-%m-%d').date(),
        vencimento=datetime.strptime(data['vencimento'], '%Y-%m-%d').date(),
        aviso_dias=int(data.get('aviso_dias', 60)),
    )
    db.session.add(contract)
    db.session.commit()
    flash('Contrato adicionado')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_contract(id):
    c = Contract.query.get_or_404(id)
    data = request.json or request.form
    c.contratante = data.get('contratante', c.contratante)
    c.objeto = data.get('objeto', c.objeto)
    if 'assinatura' in data:
        c.assinatura = datetime.strptime(data['assinatura'], '%Y-%m-%d').date()
    if 'vencimento' in data:
        c.vencimento = datetime.strptime(data['vencimento'], '%Y-%m-%d').date()
    if 'aviso_dias' in data:
        c.aviso_dias = int(data['aviso_dias'])
    db.session.commit()
    flash('Contrato atualizado')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_contract(id):
    c = Contract.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Contrato removido')
    return redirect(url_for('index'))

@app.route('/export')
def export():
    path = export_contracts()
    return {'file': path}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
