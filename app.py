from flask import Flask, request, jsonify, render_template, send_file
import os
import json
import tempfile
from datetime import datetime

# Importa os módulos da aplicação
from jurisprudencia_api import TCUJurisprudenciaAPI, AnalisadorAcordaos, GeradorInsights
from exportacao_service import ExportacaoService
from alerta_service import AlertaService

# Inicializa a aplicação Flask
app = Flask(__name__)

# Inicializa os serviços
api_client = TCUJurisprudenciaAPI()
analisador = AnalisadorAcordaos()
gerador_insights = GeradorInsights()
exportacao_service = ExportacaoService()

# Configuração
RESULTADOS_POR_PAGINA = 20
DIRETORIO_TEMP = tempfile.gettempdir()

# Rota principal - página inicial
@app.route('/')
def index():
    return render_template('index.html')

# API para buscar acórdãos
@app.route('/api/acordaos', methods=['GET'])
def buscar_acordaos():
    try:
        # Parâmetros de paginação
        pagina = int(request.args.get('pagina', 0))
        limite = int(request.args.get('limite', RESULTADOS_POR_PAGINA))
        
        # Parâmetros de filtro
        filtros = {}
        
        # Filtros de colegiado
        if 'colegiado' in request.args:
            filtros['colegiado'] = request.args.get('colegiado')
        
        # Filtros de relator
        if 'relator' in request.args:
            filtros['relator'] = request.args.get('relator')
        
        # Filtros de data
        if 'data_inicio' in request.args and 'data_fim' in request.args:
            filtros['data_inicio'] = request.args.get('data_inicio')
            filtros['data_fim'] = request.args.get('data_fim')
        
        # Filtros de texto
        if 'texto' in request.args:
            filtros['texto'] = request.args.get('texto')
        
        # Exclusões
        if 'excluir_termos' in request.args:
            termos = request.args.get('excluir_termos').split(',')
            filtros['excluir_termos'] = [termo.strip() for termo in termos]
        
        if 'excluir_relacao' in request.args:
            filtros['excluir_relacao'] = request.args.get('excluir_relacao').lower() == 'true'
        
        # Busca acórdãos
        acordaos = api_client.buscar_acordaos(pagina, limite)
        
        # Aplica filtros
        if filtros:
            acordaos = api_client.filtrar_acordaos(acordaos, filtros)
        
        # Classifica acórdãos
        if 'classificar' in request.args and request.args.get('classificar').lower() == 'true':
            acordaos = analisador.classificar_acordaos(acordaos)
        
        return jsonify({
            'total': len(acordaos),
            'pagina': pagina,
            'limite': limite,
            'acordaos': acordaos
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para buscar um acórdão específico
@app.route('/api/acordaos/<string:acordao_id>', methods=['GET'])
def buscar_acordao(acordao_id):
    try:
        acordao = api_client.buscar_acordao_por_id(acordao_id)
        
        if not acordao:
            return jsonify({'erro': 'Acórdão não encontrado'}), 404
        
        # Classifica o acórdão
        if 'classificar' in request.args and request.args.get('classificar').lower() == 'true':
            acordao = analisador.classificar_acordao(acordao)
        
        return jsonify(acordao)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para buscar acórdãos similares
@app.route('/api/recomendacao/acordao/<string:acordao_id>', methods=['GET'])
def recomendar_similares(acordao_id):
    try:
        # Parâmetros
        limite = int(request.args.get('limite', 5))
        
        # Busca acórdão de referência
        acordao = api_client.buscar_acordao_por_id(acordao_id)
        
        if not acordao:
            return jsonify({'erro': 'Acórdão não encontrado'}), 404
        
        # Busca acórdãos para comparação
        acordaos_comparacao = api_client.buscar_acordaos(0, 100)
        
        # Encontra similares
        similares = analisador.encontrar_acordaos_similares(
            acordaos_comparacao, 
            acordao, 
            limite
        )
        
        return jsonify(similares)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para buscar acórdãos por texto similar
@app.route('/api/recomendacao/texto', methods=['POST'])
def recomendar_por_texto():
    try:
        # Parâmetros
        dados = request.get_json()
        texto = dados.get('texto', '')
        limite = int(request.args.get('limite', 5))
        
        if not texto:
            return jsonify({'erro': 'Texto não fornecido'}), 400
        
        # Busca acórdãos para comparação
        acordaos_comparacao = api_client.buscar_acordaos(0, 100)
        
        # Encontra similares por texto
        similares = analisador.encontrar_acordaos_similares_por_texto(
            acordaos_comparacao, 
            texto, 
            limite
        )
        
        return jsonify(similares)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para gerar insights
@app.route('/api/insights/acordao/<string:acordao_id>', methods=['GET'])
def gerar_insight(acordao_id):
    try:
        # Parâmetros
        formato = request.args.get('formato', 'post_padrao')
        
        # Busca acórdão
        acordao = api_client.buscar_acordao_por_id(acordao_id)
        
        if not acordao:
            return jsonify({'erro': 'Acórdão não encontrado'}), 404
        
        # Gera insight
        insight = gerador_insights.gerar_insight(acordao, formato)
        
        return jsonify({
            'acordao_id': acordao_id,
            'formato': formato,
            'insight': insight
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para gerar legendas para LinkedIn
@app.route('/api/linkedin/legenda/<string:acordao_id>', methods=['GET'])
def gerar_legenda_linkedin(acordao_id):
    try:
        from gerador_legendas_linkedin import GeradorLegendasLinkedIn
        
        # Inicializa o gerador de legendas
        gerador = GeradorLegendasLinkedIn()
        
        # Busca acórdão
        acordao = api_client.buscar_acordao_por_id(acordao_id)
        
        if not acordao:
            return jsonify({'erro': 'Acórdão não encontrado'}), 404
        
        # Gera legenda
        legenda = gerador.gerar_legenda(acordao)
        
        return jsonify({
            'acordao_id': acordao_id,
            'legenda': legenda
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para exportar acórdãos
@app.route('/api/exportar', methods=['POST'])
def exportar_acordaos():
    try:
        # Parâmetros
        dados = request.get_json()
        formato = dados.get('formato', 'csv')
        acordaos = dados.get('acordaos', [])
        
        if not acordaos:
            return jsonify({'erro': 'Nenhum acórdão fornecido para exportação'}), 400
        
        # Cria nome de arquivo temporário
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"acordaos_exportados_{timestamp}"
        
        # Define extensão baseada no formato
        extensoes = {
            'csv': '.csv',
            'json': '.json',
            'pdf': '.pdf'
        }
        
        extensao = extensoes.get(formato, '.txt')
        caminho_arquivo = os.path.join(DIRETORIO_TEMP, nome_arquivo + extensao)
        
        # Exporta acórdãos
        resultado = exportacao_service.exportar(acordaos, formato, caminho_arquivo)
        
        if not resultado:
            return jsonify({'erro': 'Falha ao exportar acórdãos'}), 500
        
        # Retorna o arquivo para download
        return send_file(
            caminho_arquivo,
            as_attachment=True,
            download_name=nome_arquivo + extensao
        )
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# API para configurar alertas
@app.route('/api/alertas', methods=['POST'])
def configurar_alerta():
    try:
        # Parâmetros
        dados = request.get_json()
        usuario_id = dados.get('usuario_id')
        email = dados.get('email')
        temas = dados.get('temas')
        subtemas = dados.get('subtemas')
        palavras_chave = dados.get('palavras_chave')
        frequencia = dados.get('frequencia', 'diaria')
        
        if not usuario_id or not email:
            return jsonify({'erro': 'Usuário ID e email são obrigatórios'}), 400
        
        # Inicializa serviço de alertas
        alerta_service = AlertaService()
        
        # Adiciona alerta
        alerta_id = alerta_service.adicionar_alerta(
            usuario_id=usuario_id,
            email=email,
            temas=temas,
            subtemas=subtemas,
            palavras_chave=palavras_chave,
            frequencia=frequencia
        )
        
        return jsonify({
            'alerta_id': alerta_id,
            'mensagem': 'Alerta configurado com sucesso'
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Inicializa a aplicação
if __name__ == '__main__':
    # Cria diretório de templates se não existir
    os.makedirs('templates', exist_ok=True)
    
    # Cria um arquivo index.html básico se não existir
    index_path = os.path.join('templates', 'index.html')
    if not os.path.exists(index_path):
        with open(index_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>TCU Jurisprudência</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                    h1 { color: #003366; }
                    .container { max-width: 1200px; margin: 0 auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>API de Jurisprudência do TCU</h1>
                    <p>Bem-vindo à API de Jurisprudência do TCU. Utilize os endpoints disponíveis para acessar os acórdãos.</p>
                    <h2>Endpoints Disponíveis:</h2>
                    <ul>
                        <li><code>/api/acordaos</code> - Buscar acórdãos</li>
                        <li><code>/api/acordaos/{id}</code> - Buscar acórdão específico</li>
                        <li><code>/api/recomendacao/acordao/{id}</code> - Buscar acórdãos similares</li>
                        <li><code>/api/insights/acordao/{id}</code> - Gerar insights</li>
                        <li><code>/api/exportar</code> - Exportar acórdãos</li>
                    </ul>
                </div>
            </body>
            </html>
            """)
    
    # Inicia o servidor
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
