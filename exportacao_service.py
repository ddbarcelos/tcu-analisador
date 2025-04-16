import os
import pandas as pd
import json
import tempfile
from datetime import datetime

class ExportacaoService:
    """
    Serviço para exportação de acórdãos em diferentes formatos
    """
    def __init__(self):
        # Classe para exportação específica por formato
        self.exportador = ExportadorAcordaos()
        
        # Diretório para arquivos temporários
        self.diretorio_exportacao = tempfile.gettempdir()
    
    def exportar(self, acordaos, formato, caminho_arquivo=None):
        """
        Exporta acórdãos no formato especificado
        
        Args:
            acordaos (list): Lista de acórdãos para exportar
            formato (str): Formato de exportação ('csv', 'json', 'pdf')
            caminho_arquivo (str, optional): Caminho para salvar o arquivo
            
        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário
        """
        if not acordaos:
            return False
        
        # Define caminho do arquivo se não fornecido
        if not caminho_arquivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"acordaos_exportados_{timestamp}"
            
            # Define extensão baseada no formato
            extensoes = {
                'csv': '.csv',
                'json': '.json',
                'pdf': '.pdf'
            }
            
            extensao = extensoes.get(formato, '.txt')
            caminho_arquivo = os.path.join(self.diretorio_exportacao, nome_arquivo + extensao)
        
        # Exporta no formato especificado
        if formato.lower() == 'csv':
            return self.exportador.exportar_csv(acordaos, caminho_arquivo)
        elif formato.lower() == 'json':
            return self.exportador.exportar_json(acordaos, caminho_arquivo)
        elif formato.lower() == 'pdf':
            return self.exportador.exportar_pdf(acordaos, caminho_arquivo)
        else:
            return False
    
    def exportar_multiplos_formatos(self, acordaos, formatos, nome_base):
        """
        Exporta acórdãos em múltiplos formatos
        
        Args:
            acordaos (list): Lista de acórdãos para exportar
            formatos (list): Lista de formatos para exportação
            nome_base (str): Nome base para os arquivos
            
        Returns:
            dict: Dicionário com resultados da exportação para cada formato
        """
        resultados = {}
        
        for formato in formatos:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Define extensão baseada no formato
            extensoes = {
                'csv': '.csv',
                'json': '.json',
                'pdf': '.pdf'
            }
            
            extensao = extensoes.get(formato, '.txt')
            caminho_arquivo = os.path.join(self.diretorio_exportacao, f"{nome_base}_{formato}_{timestamp}{extensao}")
            
            # Exporta no formato
            resultado = self.exportar(acordaos, formato, caminho_arquivo)
            
            resultados[formato] = {
                'sucesso': resultado,
                'caminho': caminho_arquivo if resultado else None
            }
        
        return resultados


class ExportadorAcordaos:
    """
    Classe para exportação de acórdãos em diferentes formatos
    """
    def exportar_csv(self, acordaos, caminho_arquivo):
        """
        Exporta acórdãos para CSV
        
        Args:
            acordaos (list): Lista de acórdãos para exportar
            caminho_arquivo (str): Caminho para salvar o arquivo CSV
            
        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário
        """
        try:
            # Converte a lista de acórdãos para DataFrame
            df = pd.DataFrame(acordaos)
            
            # Seleciona colunas relevantes
            colunas = [
                'numeroAcordao', 'anoAcordao', 'colegiado', 'relator', 
                'dataSessao', 'titulo', 'sumario', 'urlAcordao'
            ]
            
            # Adiciona colunas de classificação se existirem
            for col in ['relevancia', 'impacto', 'inovacao', 'temas', 'subtemas']:
                if col in df.columns:
                    colunas.append(col)
            
            # Filtra apenas as colunas existentes
            colunas_existentes = [col for col in colunas if col in df.columns]
            
            # Exporta para CSV
            df[colunas_existentes].to_csv(caminho_arquivo, index=False, encoding='utf-8-sig')
            
            return True
        except Exception as e:
            print(f"Erro ao exportar para CSV: {e}")
            return False
    
    def exportar_json(self, acordaos, caminho_arquivo):
        """
        Exporta acórdãos para JSON
        
        Args:
            acordaos (list): Lista de acórdãos para exportar
            caminho_arquivo (str): Caminho para salvar o arquivo JSON
            
        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário
        """
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(acordaos, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Erro ao exportar para JSON: {e}")
            return False
    
    def exportar_pdf(self, acordaos, caminho_arquivo):
        """
        Exporta acórdãos para PDF
        
        Args:
            acordaos (list): Lista de acórdãos para exportar
            caminho_arquivo (str): Caminho para salvar o arquivo PDF
            
        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário
        """
        try:
            # Gera o HTML para o PDF
            html_content = self.gerar_html_para_pdf(acordaos)
            
            # Salva o HTML temporariamente
            html_temp = os.path.join(tempfile.gettempdir(), 'temp.html')
            with open(html_temp, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            try:
                # Tenta usar pdfkit se disponível
                import pdfkit
                pdfkit.from_file(html_temp, caminho_arquivo)
            except ImportError:
                # Fallback para reportlab se pdfkit não estiver disponível
                self.exportar_pdf_reportlab(acordaos, caminho_arquivo)
            
            # Remove o arquivo HTML temporário
            if os.path.exists(html_temp):
                os.remove(html_temp)
            
            return True
        except Exception as e:
            print(f"Erro ao exportar para PDF: {e}")
            return False
    
    def exportar_pdf_reportlab(self, acordaos, caminho_arquivo):
        """
        Exporta acórdãos para PDF usando reportlab (fallback)
        
        Args:
            acordaos (list): Lista de acórdãos para exportar
            caminho_arquivo (str): Caminho para salvar o arquivo PDF
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            # Cria o documento
            doc = SimpleDocTemplate(caminho_arquivo, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Cria estilos personalizados
            styles.add(ParagraphStyle(
                name='Heading1',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=12
            ))
            
            styles.add(ParagraphStyle(
                name='Heading2',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=6
            ))
            
            styles.add(ParagraphStyle(
                name='Normal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=10
            ))
            
            # Conteúdo do documento
            conteudo = []
            
            # Título do documento
            conteudo.append(Paragraph("Acórdãos do TCU - Relatório", styles['Title']))
            conteudo.append(Spacer(1, 12))
            
            # Adiciona cada acórdão
            for acordao in acordaos:
                # Título do acórdão
                titulo = f"ACÓRDÃO Nº {acordao.get('numeroAcordao', 'N/A')}/{acordao.get('anoAcordao', 'N/A')} - {acordao.get('colegiado', 'N/A')}"
                conteudo.append(Paragraph(titulo, styles['Heading1']))
                
                # Metadados
                metadados = f"Relator: {acordao.get('relator', 'N/A')} | Data: {acordao.get('dataSessao', 'N/A')}"
                conteudo.append(Paragraph(metadados, styles['Normal']))
                
                # Temas e subtemas
                if 'temas' in acordao and acordao['temas']:
                    temas = f"Temas: {', '.join(acordao['temas'])}"
                    conteudo.append(Paragraph(temas, styles['Normal']))
                
                if 'subtemas' in acordao and acordao['subtemas']:
                    subtemas = f"Subtemas: {', '.join(acordao['subtemas'])}"
                    conteudo.append(Paragraph(subtemas, styles['Normal']))
                
                # Classificações
                if all(key in acordao for key in ['relevancia', 'impacto', 'inovacao']):
                    classificacoes = f"Relevância: {acordao['relevancia']} | Impacto: {acordao['impacto']} | Inovação: {acordao['inovacao']}"
                    conteudo.append(Paragraph(classificacoes, styles['Normal']))
                
                # Sumário
                conteudo.append(Paragraph("Sumário:", styles['Heading2']))
                conteudo.append(Paragraph(acordao.get('sumario', 'Sumário não disponível'), styles['Normal']))
                
                # URL
                if 'urlAcordao' in acordao:
                    url = f"URL: {acordao['urlAcordao']}"
                    conteudo.append(Paragraph(url, styles['Normal']))
                
                # Separador
                conteudo.append(Spacer(1, 20))
            
            # Constrói o documento
            doc.build(conteudo)
            
        except Exception as e:
            print(f"Erro ao exportar para PDF com reportlab: {e}")
            raise
    
    def gerar_html_para_pdf(self, acordaos):
        """
        Gera HTML formatado para conversão em PDF
        
        Args:
            acordaos (list): Lista de acórdãos
            
        Returns:
            str: Conteúdo HTML formatado
        """
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Acórdãos do TCU</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .acordao { margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }
                .header { font-weight: bold; font-size: 16px; margin-bottom: 10px; }
                .metadata { margin-bottom: 10px; font-size: 14px; color: #555; }
                .sumario { margin-bottom: 15px; }
                .tags { font-size: 12px; color: #0066cc; }
                h1 { text-align: center; margin-bottom: 30px; }
                .page-break { page-break-after: always; }
            </style>
        </head>
        <body>
            <h1>Acórdãos do TCU - Relatório</h1>
        """
        
        for i, acordao in enumerate(acordaos):
            html += f"""
            <div class="acordao">
                <div class="header">ACÓRDÃO Nº {acordao.get('numeroAcordao', 'N/A')}/{acordao.get('anoAcordao', 'N/A')} - {acordao.get('colegiado', 'N/A')}</div>
                <div class="metadata">
                    <strong>Relator:</strong> {acordao.get('relator', 'N/A')} | 
                    <strong>Data:</strong> {acordao.get('dataSessao', 'N/A')}
                </div>
            """
            
            # Adiciona temas e subtemas se existirem
            if 'temas' in acordao and acordao['temas']:
                html += f"""
                <div class="metadata">
                    <strong>Temas:</strong> {', '.join(acordao['temas'])}
                </div>
                """
            
            if 'subtemas' in acordao and acordao['subtemas']:
                html += f"""
                <div class="metadata">
                    <strong>Subtemas:</strong> {', '.join(acordao['subtemas'])}
                </div>
                """
            
            # Adiciona classificações se existirem
            if all(key in acordao for key in ['relevancia', 'impacto', 'inovacao']):
                html += f"""
                <div class="metadata">
                    <strong>Relevância:</strong> {acordao['relevancia']} | 
                    <strong>Impacto:</strong> {acordao['impacto']} | 
                    <strong>Inovação:</strong> {acordao['inovacao']}
                </div>
                """
            
            html += f"""
                <div class="sumario">
                    <strong>Sumário:</strong><br>
                    {acordao.get('sumario', 'Sumário não disponível')}
                </div>
                <div class="tags">
                    <strong>URL:</strong> <a href="{acordao.get('urlAcordao', '#')}">{acordao.get('urlAcordao', 'Link não disponível')}</a>
                </div>
            </div>
            """
            
            # Adiciona quebra de página a cada 3 acórdãos
            if (i + 1) % 3 == 0 and i < len(acordaos) - 1:
                html += '<div class="page-break"></div>'
        
        html += """
        </body>
        </html>
        """
        
        return html
