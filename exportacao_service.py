import os
import pdfkit
from jurisprudencia_api import ExportadorAcordaos

class ExportacaoService:
    """
    Serviço para exportação de acórdãos em diferentes formatos
    """
    def __init__(self):
        self.exportador = ExportadorAcordaos()
        self.formatos_suportados = ['csv', 'json', 'pdf']
        self.diretorio_exportacao = os.path.join(os.getcwd(), 'exportacoes')
        
        # Cria o diretório de exportação se não existir
        if not os.path.exists(self.diretorio_exportacao):
            os.makedirs(self.diretorio_exportacao)
    
    def exportar(self, acordaos, formato, nome_arquivo=None):
        """
        Exporta acórdãos no formato especificado
        
        Args:
            acordaos (list): Lista de acórdãos
            formato (str): Formato de exportação (csv, json, pdf)
            nome_arquivo (str, optional): Nome do arquivo de saída
            
        Returns:
            dict: Resultado da exportação com status e caminho do arquivo
        """
        if not acordaos:
            return {
                'sucesso': False,
                'mensagem': 'Nenhum acórdão para exportar',
                'arquivo': None
            }
        
        if formato.lower() not in self.formatos_suportados:
            return {
                'sucesso': False,
                'mensagem': f'Formato não suportado. Formatos disponíveis: {", ".join(self.formatos_suportados)}',
                'arquivo': None
            }
        
        # Define o nome do arquivo se não for fornecido
        if not nome_arquivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f'acordaos_{timestamp}'
        
        # Adiciona a extensão se não estiver presente
        if not nome_arquivo.endswith(f'.{formato.lower()}'):
            nome_arquivo = f'{nome_arquivo}.{formato.lower()}'
        
        # Caminho completo do arquivo
        caminho_arquivo = os.path.join(self.diretorio_exportacao, nome_arquivo)
        
        # Exporta no formato especificado
        sucesso = False
        mensagem = ''
        
        try:
            if formato.lower() == 'csv':
                sucesso = self.exportador.exportar_csv(acordaos, caminho_arquivo)
                mensagem = 'Acórdãos exportados com sucesso para CSV'
            
            elif formato.lower() == 'json':
                sucesso = self.exportador.exportar_json(acordaos, caminho_arquivo)
                mensagem = 'Acórdãos exportados com sucesso para JSON'
            
            elif formato.lower() == 'pdf':
                # Gera o HTML para o PDF
                html_content = self.exportador.gerar_html_para_pdf(acordaos)
                
                # Salva o HTML temporariamente
                html_temp = os.path.join(self.diretorio_exportacao, 'temp.html')
                with open(html_temp, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Converte HTML para PDF
                pdfkit.from_file(html_temp, caminho_arquivo)
                
                # Remove o arquivo HTML temporário
                if os.path.exists(html_temp):
                    os.remove(html_temp)
                
                sucesso = os.path.exists(caminho_arquivo)
                mensagem = 'Acórdãos exportados com sucesso para PDF'
            
            if not sucesso:
                mensagem = f'Falha ao exportar acórdãos para {formato.upper()}'
                
            return {
                'sucesso': sucesso,
                'mensagem': mensagem,
                'arquivo': caminho_arquivo if sucesso else None
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao exportar: {str(e)}',
                'arquivo': None
            }
    
    def exportar_multiplos_formatos(self, acordaos, formatos, nome_base=None):
        """
        Exporta acórdãos em múltiplos formatos
        
        Args:
            acordaos (list): Lista de acórdãos
            formatos (list): Lista de formatos de exportação
            nome_base (str, optional): Nome base para os arquivos
            
        Returns:
            list: Lista de resultados de exportação
        """
        resultados = []
        
        for formato in formatos:
            if formato.lower() in self.formatos_suportados:
                # Define o nome do arquivo para cada formato
                if nome_base:
                    nome_arquivo = f'{nome_base}.{formato.lower()}'
                else:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    nome_arquivo = f'acordaos_{timestamp}.{formato.lower()}'
                
                # Exporta no formato atual
                resultado = self.exportar(acordaos, formato, nome_arquivo)
                resultados.append(resultado)
        
        return resultados


# Exemplo de uso
if __name__ == "__main__":
    from jurisprudencia_api import TCUJurisprudenciaAPI, AnalisadorAcordaos
    from datetime import datetime
    
    # Inicializa a API e busca acórdãos
    api = TCUJurisprudenciaAPI()
    acordaos = api.buscar_acordaos(0, 5)
    
    # Classifica os acórdãos
    analisador = AnalisadorAcordaos()
    acordaos_classificados = analisador.classificar_acordaos(acordaos)
    
    # Exporta os acórdãos
    servico_exportacao = ExportacaoService()
    
    # Exporta em CSV
    resultado_csv = servico_exportacao.exportar(acordaos_classificados, 'csv')
    print(f"Exportação CSV: {resultado_csv['mensagem']}")
    
    # Exporta em JSON
    resultado_json = servico_exportacao.exportar(acordaos_classificados, 'json')
    print(f"Exportação JSON: {resultado_json['mensagem']}")
    
    # Exporta em PDF
    resultado_pdf = servico_exportacao.exportar(acordaos_classificados, 'pdf')
    print(f"Exportação PDF: {resultado_pdf['mensagem']}")
    
    # Exporta em múltiplos formatos
    resultados = servico_exportacao.exportar_multiplos_formatos(
        acordaos_classificados, 
        ['csv', 'json', 'pdf'], 
        'acordaos_completo'
    )
    
    for resultado in resultados:
        print(f"Exportação múltipla: {resultado['mensagem']}")
