from openpyxl import Workbook
from models import db, Contract

# Gera planilha com todos os contratos
# Retorna caminho do arquivo para download

def export_contracts(path='contracts.xlsx'):
    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'Contratante', 'Objeto', 'Assinatura', 'Vencimento', 'Aviso'])
    for c in Contract.query.all():
        ws.append([
            c.id,
            c.contratante,
            c.objeto,
            c.assinatura.isoformat(),
            c.vencimento.isoformat(),
            c.aviso_dias,
        ])
    wb.save(path)
    return path
