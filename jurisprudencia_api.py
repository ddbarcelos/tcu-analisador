import requests
import json
import re
import random
from datetime import datetime

class TCUJurisprudenciaAPI:
    """
    Cliente para API de jurisprudência do TCU
    """
    def __init__(self):
        self.base_url = "https://contas.tcu.gov.br/pesquisaJurisprudencia/api"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def buscar_acordaos(self, pagina=0, limite=20, filtros=None) :
        """
        Busca acórdãos na API do TCU
        
        Args:
            pagina (int): Número da página
            limite (int): Limite de resultados por página
            filtros (dict): Filtros para a busca
            
        Returns:
            list: Lista de acórdãos
        """
        # Implementação simulada para desenvolvimento
        # Em produção, seria substituída pela chamada real à API
        acordaos = self._gerar_acordaos_simulados(limite)
        
        # Aplica filtros se fornecidos
        if filtros:
            acordaos = self.filtrar_acordaos(acordaos, filtros)
        
        return acordaos
    
    def buscar_acordao_por_id(self, acordao_id):
        """
        Busca um acórdão específico por ID
        
        Args:
            acordao_id (str): ID do acórdão
            
        Returns:
            dict: Dados do acórdão
        """
        # Implementação simulada para desenvolvimento
        # Em produção, seria substituída pela chamada real à API
        acordaos = self._gerar_acordaos_simulados(20)
        
        # Simula a busca por ID
        for acordao in acordaos:
            if str(acordao.get('id', '')) == acordao_id:
                return acordao
        
        return None
    
    def filtrar_acordaos(self, acordaos, filtros):
        """
        Filtra acórdãos com base nos critérios fornecidos
        
        Args:
            acordaos (list): Lista de acórdãos
            filtros (dict): Critérios de filtragem
            
        Returns:
            list: Lista de acórdãos filtrados
        """
        resultado = acordaos.copy()
        
        # Filtra por colegiado
        if 'colegiado' in filtros and filtros['colegiado']:
            resultado = [a for a in resultado if a.get('colegiado', '').lower() == filtros['colegiado'].lower()]
        
        # Filtra por relator
        if 'relator' in filtros and filtros['relator']:
            resultado = [a for a in resultado if filtros['relator'].lower() in a.get('relator', '').lower()]
        
        # Filtra por data
        if 'data_inicio' in filtros and 'data_fim' in filtros:
            try:
                data_inicio = datetime.strptime(filtros['data_inicio'], '%Y-%m-%d')
                data_fim = datetime.strptime(filtros['data_fim'], '%Y-%m-%d')
                
                resultado = [a for a in resultado if self._verificar_data_entre(a.get('dataSessao', ''), data_inicio, data_fim)]
            except:
                pass
        
        # Filtra por texto
        if 'texto' in filtros and filtros['texto']:
            texto = filtros['texto'].lower()
            resultado = [a for a in resultado if 
                         texto in a.get('sumario', '').lower() or 
                         texto in a.get('titulo', '').lower()]
        
        # Exclui termos específicos
        if 'excluir_termos' in filtros and filtros['excluir_termos']:
            for termo in filtros['excluir_termos']:
                resultado = [a for a in resultado if termo.lower() not in a.get('sumario', '').lower()]
        
        # Exclui acórdãos de relação
        if 'excluir_relacao' in filtros and filtros['excluir_relacao']:
            resultado = [a for a in resultado if not self._eh_acordao_relacao(a)]
        
        return resultado
    
    def _verificar_data_entre(self, data_str, data_inicio, data_fim):
        """Verifica se uma data está entre duas datas"""
        try:
            # Tenta diferentes formatos de data
            for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
                try:
                    data = datetime.strptime(data_str, fmt)
                    return data_inicio <= data <= data_fim
                except:
                    continue
            return False
        except:
            return False
    
    def _eh_acordao_relacao(self, acordao):
        """Verifica se é um acórdão de relação"""
        titulo = acordao.get('titulo', '').lower()
        sumario = acordao.get('sumario', '').lower()
        
        return 'relação' in titulo or 'relacao' in titulo or 'relação' in sumario or 'relacao' in sumario
    
    def _gerar_acordaos_simulados(self, quantidade):
        """
        Gera acórdãos simulados para desenvolvimento
        
        Args:
            quantidade (int): Quantidade de acórdãos a gerar
            
        Returns:
            list: Lista de acórdãos simulados
        """
        acordaos = []
        
        # Dados para simulação
        colegiados = ['Plenário', 'Primeira Câmara', 'Segunda Câmara']
        relatores = ['Ministro João Silva', 'Ministro Carlos Oliveira', 'Ministra Ana Santos', 'Ministro Pedro Costa']
        temas = [
            ['Licitação', 'Contratação Direta'], 
            ['Contrato Administrativo', 'Fiscalização'], 
            ['Responsabilidade', 'Débito'],
            ['Convênio', 'Transferência de Recursos'],
            ['Obra Pública', 'Sobrepreço']
        ]
        subtemas = [
            ['Pregão Eletrônico', 'Dispensa de Licitação', 'Inexigibilidade'],
            ['Aditivo', 'Fiscalização', 'Pagamento'],
            ['Multa', 'Tomada de Contas Especial', 'Prescrição'],
            ['Prestação de Contas', 'Contrapartida', 'Tomada de Contas Especial'],
            ['Superfaturamento', 'Projeto Básico', 'BDI']
        ]
        
        # Gera acórdãos aleatórios
        for i in range(quantidade):
            # Seleciona tema e subtema
            tema_idx = random.randint(0, len(temas) - 1)
            
            acordao = {
                'id': f'acordao-{i+1000}',
                'numeroAcordao': str(random.randint(1000, 9999)),
                'anoAcordao': str(random.randint(2018, 2023)),
                'colegiado': random.choice(colegiados),
                'relator': random.choice(relatores),
                'dataSessao': f'{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(2018, 2023)}',
                'titulo': f'Acórdão sobre {random.choice(temas[tema_idx])}',
                'sumario': self._gerar_sumario_simulado(temas[tema_idx], subtemas[tema_idx]),
                'urlAcordao': f'https://pesquisa.apps.tcu.gov.br/#/documento/acordao-completo/{random.randint(1000, 9999) }',
                'temas': temas[tema_idx],
                'subtemas': random.sample(subtemas[tema_idx], random.randint(1, len(subtemas[tema_idx])))
            }
            
            acordaos.append(acordao)
        
        return acordaos
    
    def _gerar_sumario_simulado(self, temas, subtemas):
        """Gera um sumário simulado para desenvolvimento"""
        tema = random.choice(temas)
        subtema = random.choice(subtemas)
        
        templates = [
            f"Representação formulada a partir de trabalho realizado pela Secretaria de Controle Externo versando sobre {tema.lower()} com foco em {subtema.lower()}. Análise de oitivas. Procedência parcial. Determinações.",
            f"Tomada de contas especial instaurada em razão de irregularidades em {tema.lower()}. Citação dos responsáveis. {subtema}. Contas irregulares. Débito. Multa.",
            f"Auditoria realizada para avaliar a conformidade de procedimentos relacionados a {tema.lower()}. {subtema}. Falhas identificadas. Determinações e recomendações.",
            f"Monitoramento de determinações expedidas em processo anterior sobre {tema.lower()}. {subtema}. Cumprimento parcial. Novas determinações.",
            f"Consulta acerca da aplicabilidade de normativos relacionados a {tema.lower()}. {subtema}. Conhecimento. Resposta ao consulente."
        ]
        
        return random.choice(templates)


class AnalisadorAcordaos:
    """
    Classe para análise e classificação de acórdãos
    """
    def __init__(self):
        # Inicialização simulada para desenvolvimento
        pass
    
    def classificar_acordaos(self, acordaos):
        """
        Classifica acórdãos por relevância, impacto e inovação
        
        Args:
            acordaos (list): Lista de acórdãos
            
        Returns:
            list: Lista de acórdãos classificados
        """
        resultado = []
        
        for acordao in acordaos:
            resultado.append(self.classificar_acordao(acordao))
        
        return resultado
    
    def classificar_acordao(self, acordao):
        """
        Classifica um acórdão por relevância, impacto e inovação
        
        Args:
            acordao (dict): Acórdão a classificar
            
        Returns:
            dict: Acórdão classificado
        """
        # Cria uma cópia para não modificar o original
        acordao_classificado = acordao.copy()
        
        # Simulação de classificação para desenvolvimento
        # Em produção, seria substituída por algoritmos de ML
        acordao_classificado['relevancia'] = self._calcular_relevancia(acordao)
        acordao_classificado['impacto'] = self._calcular_impacto(acordao)
        acordao_classificado['inovacao'] = self._calcular_inovacao(acordao)
        
        return acordao_classificado
    
    def encontrar_acordaos_similares(self, acordaos, acordao_referencia, limite=5):
        """
        Encontra acórdãos similares a um acórdão de referência
        
        Args:
            acordaos (list): Lista de acórdãos para comparação
            acordao_referencia (dict): Acórdão de referência
            limite (int): Número máximo de resultados
            
        Returns:
            list: Lista de acórdãos similares
        """
        # Implementação simulada para desenvolvimento
        # Em produção, seria substituída por algoritmos de similaridade
        
        # Filtra para não incluir o próprio acórdão
        candidatos = [a for a in acordaos if a.get('id') != acordao_referencia.get('id')]
        
        # Calcula similaridade simulada
        similares = []
        for acordao in candidatos:
            similaridade = self._calcular_similaridade(acordao, acordao_referencia)
            similares.append({
                'acordao': acordao,
                'similaridade': similaridade
            })
        
        # Ordena por similaridade e limita resultados
        similares.sort(key=lambda x: x['similaridade'], reverse=True)
        similares = similares[:limite]
        
        # Formata resultado
        resultado = []
        for item in similares:
            acordao = item['acordao'].copy()
            acordao['score_similaridade'] = round(item['similaridade'], 2)
            resultado.append(acordao)
        
        return resultado
    
    def encontrar_acordaos_similares_por_texto(self, acordaos, texto, limite=5):
        """
        Encontra acórdãos similares a um texto
        
        Args:
            acordaos (list): Lista de acórdãos para comparação
            texto (str): Texto de referência
            limite (int): Número máximo de resultados
            
        Returns:
            list: Lista de acórdãos similares
        """
        # Implementação simulada para desenvolvimento
        # Em produção, seria substituída por algoritmos de similaridade
        
        # Calcula similaridade simulada
        similares = []
        for acordao in acordaos:
            similaridade = self._calcular_similaridade_texto(acordao, texto)
            similares.append({
                'acordao': acordao,
                'similaridade': similaridade
            })
        
        # Ordena por similaridade e limita resultados
        similares.sort(key=lambda x: x['similaridade'], reverse=True)
        similares = similares[:limite]
        
        # Formata resultado
        resultado = []
        for item in similares:
            acordao = item['acordao'].copy()
            acordao['score_similaridade'] = round(item['similaridade'], 2)
            resultado.append(acordao)
        
        return resultado
    
    def _calcular_relevancia(self, acordao):
        """Calcula relevância simulada"""
        # Simulação para desenvolvimento
        return round(random.uniform(0.5, 1.0), 2)
    
    def _calcular_impacto(self, acordao):
        """Calcula impacto simulado"""
        # Simulação para desenvolvimento
        return round(random.uniform(0.5, 1.0), 2)
    
    def _calcular_inovacao(self, acordao):
        """Calcula inovação simulada"""
        # Simulação para desenvolvimento
        return round(random.uniform(0.5, 1.0), 2)
    
    def _calcular_similaridade(self, acordao, acordao_referencia):
        """Calcula similaridade simulada entre acórdãos"""
        # Simulação para desenvolvimento
        # Verifica temas em comum
        temas_ref = set(acordao_referencia.get('temas', []))
        temas = set(acordao.get('temas', []))
        
        # Verifica subtemas em comum
        subtemas_ref = set(acordao_referencia.get('subtemas', []))
        subtemas = set(acordao.get('subtemas', []))
        
        # Calcula similaridade baseada em temas e subtemas comuns
        similaridade_temas = len(temas.intersection(temas_ref)) / max(len(temas_ref), 1)
        similaridade_subtemas = len(subtemas.intersection(subtemas_ref)) / max(len(subtemas_ref), 1)
        
        # Adiciona componente aleatório para simulação
        return (similaridade_temas * 0.4 + similaridade_subtemas * 0.4 + random.uniform(0, 0.2))
    
    def _calcular_similaridade_texto(self, acordao, texto):
        """Calcula similaridade simulada entre acórdão e texto"""
        # Simulação para desenvolvimento
        # Verifica palavras em comum
        palavras_texto = set(re.findall(r'\w+', texto.lower()))
        palavras_sumario = set(re.findall(r'\w+', acordao.get('sumario', '').lower()))
        
        # Calcula similaridade baseada em palavras comuns
        palavras_comuns = len(palavras_texto.intersection(palavras_sumario))
        similaridade = palavras_comuns / max(len(palavras_texto), 1) * 0.8
        
        # Adiciona componente aleatório para simulação
        return similaridade + random.uniform(0, 0.2)


class GeradorInsights:
    """
    Classe para geração de insights a partir de acórdãos
    """
    def __init__(self):
        # Inicialização simulada para desenvolvimento
        pass
    
    def gerar_insight(self, acordao, formato='post_padrao'):
        """
        Gera insights a partir de um acórdão
        
        Args:
            acordao (dict): Acórdão para análise
            formato (str): Formato do insight ('post_padrao', 'resumo', 'destaque')
            
        Returns:
            str: Insight gerado
        """
        # Implementação simulada para desenvolvimento
        if formato == 'post_padrao':
            return self._gerar_post_padrao(acordao)
        elif formato == 'resumo':
            return self._gerar_resumo(acordao)
        elif formato == 'destaque':
            return self._gerar_destaque(acordao)
        else:
            return self._gerar_post_padrao(acordao)
    
    def _gerar_post_padrao(self, acordao):
        """Gera post padrão"""
        numero = acordao.get('numeroAcordao', 'N/A')
        ano = acordao.get('anoAcordao', 'N/A')
        colegiado = acordao.get('colegiado', 'TCU')
        relator = acordao.get('relator', 'N/A')
        sumario = acordao.get('sumario', '')
        
        # Extrai primeira frase do sumário
        primeira_frase = sumario.split('.')[0] + '.' if sumario else 'Sumário não disponível.'
        
        # Gera post
        post = f"""
        📌 JURISPRUDÊNCIA DO TCU | ACÓRDÃO {numero}/{ano}

        O {colegiado} do TCU, sob relatoria do(a) {relator}, decidiu:

        "{primeira_frase}"

        Este acórdão traz importantes orientações sobre {', '.join(acordao.get('temas', ['licitações e contratos']))}.

        #TCU #JurisprudênciaAdministrativa #DireitoAdministrativo
        """
        
        return post.strip()
    
    def _gerar_resumo(self, acordao):
        """Gera resumo"""
        numero = acordao.get('numeroAcordao', 'N/A')
        ano = acordao.get('anoAcordao', 'N/A')
        colegiado = acordao.get('colegiado', 'TCU')
        sumario = acordao.get('sumario', 'Sumário não disponível.')
        
        # Gera resumo
        resumo = f"""
        RESUMO: ACÓRDÃO {numero}/{ano} - {colegiado}

        {sumario}

        Temas: {', '.join(acordao.get('temas', ['N/A']))}
        Subtemas: {', '.join(acordao.get('subtemas', ['N/A']))}
        """
        
        return resumo.strip()
    
    def _gerar_destaque(self, acordao):
        """Gera destaque"""
        numero = acordao.get('numeroAcordao', 'N/A')
        ano = acordao.get('anoAcordao', 'N/A')
        
        # Gera destaque
        destaque = f"""
        🔍 DESTAQUE DA SEMANA: ACÓRDÃO {numero}/{ano}

        Relevância: {acordao.get('relevancia', 'N/A')}
        Impacto: {acordao.get('impacto', 'N/A')}
        Inovação: {acordao.get('inovacao', 'N/A')}

        Este acórdão se destaca por {self._gerar_motivo_destaque(acordao)}.
        """
        
        return destaque.strip()
    
    def _gerar_motivo_destaque(self, acordao):
        """Gera motivo de destaque simulado"""
        motivos = [
            "trazer uma interpretação inovadora sobre o tema",
            "consolidar entendimento divergente em julgados anteriores",
            "estabelecer novos parâmetros para análise de casos similares",
            "revisar posicionamento anterior do Tribunal",
            "apresentar detalhada fundamentação técnica e jurídica"
        ]
        
        return random.choice(motivos)
