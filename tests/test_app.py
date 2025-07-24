import json
from datetime import date
import pytest
from app import app, db, days_left
from models import Contract

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def sample_data():
    return {
        "contratante": "Acme",
        "objeto": "Manutencao",
        "assinatura": "2025-01-15",
        "vencimento": "2026-01-14",
        "aviso_dias": 60,
    }

def test_create_contract(client):
    res = client.post('/add', json=sample_data())
    assert res.status_code == 302
    with app.app_context():
        assert Contract.query.count() == 1


def test_edit_contract(client):
    with app.app_context():
        c = Contract(
            contratante='A',
            objeto='B',
            assinatura=date(2025,1,1),
            vencimento=date(2025,12,31),
        )
        db.session.add(c)
        db.session.commit()
        cid = c.id
    res = client.post(f'/edit/{cid}', json={"objeto":"Novo"})
    assert res.status_code == 302
    with app.app_context():
        assert Contract.query.get(cid).objeto == 'Novo'


def test_delete_contract(client):
    with app.app_context():
        c = Contract(
            contratante='X',
            objeto='Y',
            assinatura=date(2025,1,1),
            vencimento=date(2025,12,31),
        )
        db.session.add(c)
        db.session.commit()
        cid = c.id
    res = client.post(f'/delete/{cid}')
    assert res.status_code == 302
    with app.app_context():
        assert Contract.query.get(cid) is None


def test_days_left():
    future = date.today().replace(year=date.today().year + 1)
    assert days_left(future) > 360
