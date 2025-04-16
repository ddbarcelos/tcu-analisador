import requests
import json
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
import re

# Baixar recursos necessários do NLTK
nltk.download('punkt')
nltk.download('stopwords')

class TCUJurisprudenciaAPI:
    """
    Classe para interagir com a API de Acórdãos do TCU
    """
    def __init__(self):
        self.base_url = "https://dados-abertos.apps.tcu.gov.br/api/acordao/recupera-acordaos"
        self.stop_words = set(stopwords.words('portuguese'))
    
    def buscar_acordaos(self, inicio=0, quantidade=50):
        """
        Busca acórdãos na API do TCU
        
        Args:
            inicio (int): Índice inicial para busca
            quantidade (int): Quantidade de acórdãos a serem retornados
            
        Returns:
            list: Lista de acórdãos
        """
        url = f"{self.base_url}?inicio={inicio}&quantidade={quantidade}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar acórdãos: {e}")
            return []
    
    def filtrar_acordaos(self, acordaos, filtros=None):
        """
        Filtra acórdãos com base nos critérios especificados
        
        Args:
            acordaos (list): Lista de acórdãos
            filtros (dict): Dicionário com filtros a serem aplicados
            
        Returns:
            list: Lista de acórdãos filtrados
        """
        if not filtros:
            return acordaos
        
        resultado = acordaos.copy()
        
        # Filtrar por órgão colegiado
        if 'colegiado' in filtros and filtros['colegiado']:
            resultado = [a for a in resultado if a.get('colegiado') == filtros['colegiado']]
        
        # Filtrar por relator
        if 'relator' in filtros and filtros['relator']:
            resultado = [a for a in resultado if a.get('relator') == filtros['relator']]
        
        # Filtrar por ano
        if 'ano' in filtros and filtros['ano']:
            resultado = [a for a in resultado if a.get('anoAcordao') == str(filtros['ano'])]
        
        # Filtrar por período
        if 'data_inicio' in filtros and 'data_fim' in filtros and filtros['data_inicio'] and filtros['data_fim']:
            data_inicio = datetime.strptime(filtros['data_inicio'], '%Y-%m-%d')
            data_fim = datetime.strptime(filtros['data_fim'], '%Y-%m-%d')
            
            resultado = [a for a in resultado if self._esta_no_periodo(a.get('dataSessao'), data_inicio, data_fim)]
        
        # Excluir acórdãos com termos específicos no sumário
        if 'excluir_termos' in filtros and filtros['excluir_termos']:
            for termo in filtros['excluir_termos']:
                resultado = [a for a in resultado if not self._contem_termo_no_sumario(a, termo)]
        
        # Excluir acórdãos de relação
        if 'excluir_relacao' in filtros and filtros['excluir_relacao']:
            resultado = [a for a in resultado if not self._eh_acordao_relacao(a)]
        
        return resultado
    
    def _esta_no_periodo(self, data_str, data_inicio, data_fim):
        """Verifica se uma data está dentro de um período específico"""
        if not data_str:
            return False
        
        try:
            data = datetime.strptime(data_str, '%d/%m/%Y')
            return data_inicio <= data <= data_fim
        except ValueError:
            return False
    
    def _contem_termo_no_sumario(self, acordao, termo):
        """Verifica se um termo está presente no sumário do acórdão"""
        sumario = acordao.get('sumario', '').lower()
        return termo.lower() in sumario
    
    def _eh_acordao_relacao(self, acordao):
        """Verifica se é um acórdão de relação"""
        titulo = acordao.get('titulo', '').lower()
        return 'relação' in titulo or 'relacao' in titulo
    
    def buscar_por_texto(self, acordaos, texto):
        """
        Busca acórdãos que contenham o texto especificado
        
        Args:
            acordaos (list): Lista de acórdãos
            texto (str): Texto a ser buscado
            
        Returns:
            list: Lista de acórdãos que contêm o texto
        """
        if not texto:
            return acordaos
        
        texto = texto.lower()
        resultado = []
        
        for acordao in acordaos:
            # Busca em vários campos do acórdão
            campos_busca = [
                acordao.get('titulo', '').lower(),
                acordao.get('sumario', '').lower(),
                acordao.get('relator', '').lower(),
                acordao.get('colegiado', '').lower()
            ]
            
            # Se algum campo contiver o texto, inclui o acórdão no resultado
            if any(texto in campo for campo in campos_busca):
                resultado.append(acordao)
        
        return resultado


class AnalisadorAcordaos:
    """
    Classe para análise e classificação de acórdãos
    """
    def __init__(self):
        self.stop_words = set(stopwords.words('portuguese'))
        self.vectorizer = TfidfVectorizer(stop_words=self.stop_words)
        
        # Palavras-chave que indicam relevância, impacto e inovação
        self.palavras_relevancia = [
            'importante', 'relevante', 'significativo', 'essencial', 'fundamental',
            'precedente', 'jurisprudência', 'consolidado', 'reiterado'
        ]
        
        self.palavras_impacto = [
            'impacto', 'efeito', 'consequência', 'resultado', 'repercussão',
            'alcance', 'abrangência', 'influência', 'determinação', 'multa'
        ]
        
        self.palavras_inovacao = [
            'novo', 'inovador', 'inédito', 'pioneiro', 'original',
            'mudança', 'alteração', 'revisão', 'atualização', 'evolução'
        ]
        
        # Dicionário de temas e subtemas com palavras-chave associadas
        self.temas = {
            'Licitações e Contratos': {
                'palavras': ['licitação', 'contrato', 'edital', 'pregão', 'concorrência', 'tomada de preços'],
                'subtemas': {
                    'Pregão Eletrônico': ['pregão eletrônico', 'pregoeiro', 'lance', 'proposta'],
                    'Dispensa de Licitação': ['dispensa', 'dispensada', 'dispensável', 'emergência'],
                    'Inexigibilidade': ['inexigibilidade', 'inviável', 'competição', 'exclusividade', 'notória especialização'],
                    'Aditivos Contratuais': ['aditivo', 'alteração contratual', 'acréscimo', 'supressão'],
                    'Sanções': ['sanção', 'penalidade', 'multa', 'impedimento', 'inidoneidade']
                }
            },
            'Responsabilidade': {
                'palavras': ['responsabilidade', 'responsável', 'culpa', 'dolo', 'erro'],
                'subtemas': {
                    'Culpa': ['culpa', 'negligência', 'imprudência', 'imperícia'],
                    'Dolo': ['dolo', 'má-fé', 'intenção', 'fraude'],
                    'Solidária': ['solidária', 'solidariedade', 'conjunto']
                }
            },
            'Convênio': {
                'palavras': ['convênio', 'acordo', 'parceria', 'cooperação', 'repasse'],
                'subtemas': {
                    'Prestação de Contas': ['prestação de contas', 'comprovação', 'documentação'],
                    'Tomada de Contas Especial': ['tomada de contas especial', 'TCE', 'dano ao erário']
                }
            }
        }
    
    def classificar_acordaos(self, acordaos):
        """
        Classifica acórdãos por relevância, impacto e inovação
        
        Args:
            acordaos (list): Lista de acórdãos
            
        Returns:
            list: Lista de acórdãos com classificações adicionadas
        """
        resultado = []
        
        for acordao in acordaos:
            # Cria uma cópia do acórdão para não modificar o original
            acordao_classificado = acordao.copy()
            
            # Obtém o texto para análise (sumário + título)
            texto = f"{acordao.get('sumario', '')} {acordao.get('titulo', '')}"
            
            # Classifica o acórdão
            relevancia = self._calcular_relevancia(texto)
            impacto = self._calcular_impacto(texto)
            inovacao = self._calcular_inovacao(texto)
            
            # Adiciona as classificações ao acórdão
            acordao_classificado['relevancia'] = relevancia
            acordao_classificado['impacto'] = impacto
            acordao_classificado['inovacao'] = inovacao
            
            # Identifica temas e subtemas
            temas, subtemas = self._identificar_temas(texto)
            acordao_classificado['temas'] = temas
            acordao_classificado['subtemas'] = subtemas
            
            resultado.append(acordao_classificado)
        
        return resultado
    
    def _calcular_relevancia(self, texto):
        """Calcula a pontuação de relevância com base no texto"""
        texto = texto.lower()
        pontuacao = 0
        
        # Verifica a presença de palavras-chave de relevância
        for palavra in self.palavras_relevancia:
            if palavra in texto:
                pontuacao += 10
        
        # Fatores adicionais de relevância
        if 'precedente' in texto or 'jurisprudência' in texto:
            pontuacao += 20
        
        if 'súmula' in texto:
            pontuacao += 30
        
        return min(pontuacao, 100)  # Limita a pontuação a 100
    
    def _calcular_impacto(self, texto):
        """Calcula a pontuação de impacto com base no texto"""
        texto = texto.lower()
        pontuacao = 0
        
        # Verifica a presença de palavras-chave de impacto
        for palavra in self.palavras_impacto:
            if palavra in texto:
                pontuacao += 10
        
        # Fatores adicionais de impacto
        if 'determinação' in texto:
            pontuacao += 15
        
        if 'multa' in texto:
            pontuacao += 20
        
        if 'dano ao erário' in texto:
            pontuacao += 25
        
        return min(pontuacao, 100)  # Limita a pontuação a 100
    
    def _calcular_inovacao(self, texto):
        """Calcula a pontuação de inovação com base no texto"""
        texto = texto.lower()
        pontuacao = 0
        
        # Verifica a presença de palavras-chave de inovação
        for palavra in self.palavras_inovacao:
            if palavra in texto:
                pontuacao += 10
        
        # Fatores adicionais de inovação
        if 'primeira vez' in texto or 'inédito' in texto:
            pontuacao += 25
        
        if 'revisão' in texto or 'mudança de entendimento' in texto:
            pontuacao += 30
        
        return min(pontuacao, 100)  # Limita a pontuação a 100
    
    def _identificar_temas(self, texto):
        """Identifica temas e subtemas com base no texto"""
        texto = texto.lower()
        temas_identificados = []
        subtemas_identificados = []
        
        # Verifica cada tema e seus subtemas
        for tema, info in self.temas.items():
            # Verifica se alguma palavra-chave do tema está presente no texto
            if any(palavra in texto for palavra in info['palavras']):
                temas_identificados.append(tema)
                
                # Verifica subtemas
                for subtema, palavras_subtema in info['subtemas'].items():
                    if any(palavra in texto for palavra in palavras_subtema):
                        subtemas_identificados.append(subtema)
        
        return temas_identificados, subtemas_identificados
    
    def encontrar_acordaos_similares(self, acordaos, acordao_referencia, n=5):
        """
        Encontra acórdãos similares ao acórdão de referência
        
        Args:
            acordaos (list): Lista de acórdãos
            acordao_referencia (dict): Acórdão de referência
            n (int): Número de acórdãos similares a retornar
            
        Returns:
            list: Lista de acórdãos similares
        """
        # Extrai o texto de todos os acórdãos
        textos = []
        for acordao in acordaos:
            texto = f"{acordao.get('sumario', '')} {acordao.get('titulo', '')}"
            textos.append(texto)
        
        # Adiciona o texto do acórdão de referência
        texto_referencia = f"{acordao_referencia.get('sumario', '')} {acordao_referencia.get('titulo', '')}"
        textos.append(texto_referencia)
        
        # Vetoriza os textos
        tfidf_matrix = self.vectorizer.fit_transform(textos)
        
        # Calcula a similaridade de cosseno
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
        
        # Obtém os índices dos acórdãos mais similares
        indices_similares = cosine_similarities.argsort()[::-1][:n]
        
        # Retorna os acórdãos similares
        return [acordaos[i] for i in indices_similares]


class GeradorInsights:
    """
    Classe para geração de insights a partir de acórdãos
    """
    def __init__(self):
        self.templates = {
            'post_padrao': """
#Licitações #TCU #NovoEntendimento

O TCU, por meio do Acórdão {numero}/{ano}-{colegiado}, estabeleceu importante precedente sobre {tema}.

Principais pontos:
✅ {ponto1}
✅ {ponto2}
✅ {ponto3}

📌 Relator: {relator}
📌 Data: {data}

#{hashtag1} #{hashtag2} #{hashtag3}
            """,
            
            'analise_detalhada': """
#AnáliseJurídica #TCU #Jurisprudência

📑 ANÁLISE DE JURISPRUDÊNCIA DO TCU 📑

Acórdão {numero}/{ano}-{colegiado}
Relator: {relator}
Data: {data}

📋 RESUMO:
{resumo}

🔍 ANÁLISE DETALHADA:
{analise}

💡 IMPACTO PRÁTICO:
{impacto}

⚖️ CONCLUSÃO:
{conclusao}

#{hashtag1} #{hashtag2} #{hashtag3}
            """,
            
            'dica_rapida': """
#DicaRápida #TCU #Licitações

💡 VOCÊ SABIA? 💡

Segundo o Acórdão {numero}/{ano}-{colegiado} do TCU:

"{citacao}"

Isso significa que {explicacao}

📌 Fonte: TCU, Acórdão {numero}/{ano}, Relator: {relator}

#{hashtag1} #{hashtag2}
            """
        }
    
    def extrair_pontos_principais(self, acordao):
        """
        Extrai pontos principais do acórdão para uso nos insights
        
        Args:
            acordao (dict): Acórdão
            
        Returns:
            list: Lista de pontos principais
        """
        sumario = acordao.get('sumario', '')
        
        # Divide o sumário em sentenças
        sentencas = re.split(r'[.;]', sumario)
        sentencas = [s.strip() for s in sentencas if len(s.strip()) > 20]
        
        # Seleciona até 3 sentenças mais relevantes
        pontos = sentencas[:3] if len(sentencas) >= 3 else sentencas
        
        # Se não houver pontos suficientes, adiciona pontos genéricos
        while len(pontos) < 3:
            pontos.append("Ponto a ser analisado pelo especialista")
        
        return pontos
    
    def gerar_hashtags(self, acordao):
        """
        Gera hashtags relevantes com base no acórdão
        
        Args:
            acordao (dict): Acórdão
            
        Returns:
            list: Lista de hashtags
        """
        hashtags = []
        
        # Adiciona hashtags com base nos temas
        if 'temas' in acordao and acordao['temas']:
            for tema in acordao['temas']:
                hashtag = tema.replace(' e ', '').replace(' ', '')
                hashtags.append(hashtag)
        
        # Adiciona hashtags com base nos subtemas
        if 'subtemas' in acordao and acordao['subtemas']:
            for subtema in acordao['subtemas']:
                hashtag = subtema.replace(' ', '')
                
(Content truncated due to size limit. Use line ranges to read in chunks)