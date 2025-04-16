import json
import os
import uuid
from datetime import datetime

class AlertaService:
    """
    Serviço para gerenciamento de alertas de novos acórdãos
    """
    def __init__(self):
        # Diretório para armazenar alertas
        self.diretorio_alertas = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.diretorio_alertas, exist_ok=True)
        
        # Arquivo de alertas
        self.arquivo_alertas = os.path.join(self.diretorio_alertas, 'alertas.json')
        
        # Carrega alertas existentes
        self.alertas = self._carregar_alertas()
    
    def adicionar_alerta(self, usuario_id, email, temas=None, subtemas=None, palavras_chave=None, frequencia='diaria'):
        """
        Adiciona um novo alerta
        
        Args:
            usuario_id (str): ID do usuário
            email (str): Email para envio de alertas
            temas (list): Lista de temas para monitorar
            subtemas (list): Lista de subtemas para monitorar
            palavras_chave (list): Lista de palavras-chave para monitorar
            frequencia (str): Frequência de envio ('diaria', 'semanal')
            
        Returns:
            str: ID do alerta criado
        """
        # Gera ID único para o alerta
        alerta_id = str(uuid.uuid4())
        
        # Cria alerta
        alerta = {
            'id': alerta_id,
            'usuario_id': usuario_id,
            'email': email,
            'temas': temas or [],
            'subtemas': subtemas or [],
            'palavras_chave': palavras_chave or [],
            'frequencia': frequencia,
            'criado_em': datetime.now().isoformat(),
            'ultima_execucao': None,
            'ativo': True
        }
        
        # Adiciona à lista de alertas
        self.alertas.append(alerta)
        
        # Salva alertas
        self._salvar_alertas()
        
        return alerta_id
    
    def remover_alerta(self, alerta_id):
        """
        Remove um alerta
        
        Args:
            alerta_id (str): ID do alerta
            
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        # Busca alerta
        for i, alerta in enumerate(self.alertas):
            if alerta['id'] == alerta_id:
                # Remove alerta
                self.alertas.pop(i)
                
                # Salva alertas
                self._salvar_alertas()
                
                return True
        
        return False
    
    def atualizar_alerta(self, alerta_id, dados):
        """
        Atualiza um alerta
        
        Args:
            alerta_id (str): ID do alerta
            dados (dict): Dados para atualização
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        # Busca alerta
        for i, alerta in enumerate(self.alertas):
            if alerta['id'] == alerta_id:
                # Atualiza campos permitidos
                campos_permitidos = ['email', 'temas', 'subtemas', 'palavras_chave', 'frequencia', 'ativo']
                
                for campo in campos_permitidos:
                    if campo in dados:
                        alerta[campo] = dados[campo]
                
                # Salva alertas
                self._salvar_alertas()
                
                return True
        
        return False
    
    def buscar_alerta(self, alerta_id):
        """
        Busca um alerta pelo ID
        
        Args:
            alerta_id (str): ID do alerta
            
        Returns:
            dict: Dados do alerta ou None se não encontrado
        """
        # Busca alerta
        for alerta in self.alertas:
            if alerta['id'] == alerta_id:
                return alerta.copy()
        
        return None
    
    def buscar_alertas_por_usuario(self, usuario_id):
        """
        Busca alertas de um usuário
        
        Args:
            usuario_id (str): ID do usuário
            
        Returns:
            list: Lista de alertas do usuário
        """
        return [alerta.copy() for alerta in self.alertas if alerta['usuario_id'] == usuario_id]
    
    def processar_alertas(self):
        """
        Processa alertas pendentes
        
        Returns:
            dict: Estatísticas de processamento
        """
        # Implementação simulada para desenvolvimento
        # Em produção, seria integrada com sistema de envio de emails
        
        # Estatísticas
        estatisticas = {
            'total': len(self.alertas),
            'processados': 0,
            'enviados': 0,
            'erros': 0
        }
        
        # Processa cada alerta
        for alerta in self.alertas:
            if not alerta['ativo']:
                continue
            
            try:
                # Simula processamento
                estatisticas['processados'] += 1
                
                # Atualiza última execução
                alerta['ultima_execucao'] = datetime.now().isoformat()
                
                # Simula envio
                # Em produção, aqui seria feita a busca de novos acórdãos e envio de email
                estatisticas['enviados'] += 1
                
            except Exception as e:
                estatisticas['erros'] += 1
                print(f"Erro ao processar alerta {alerta['id']}: {e}")
        
        # Salva alertas
        self._salvar_alertas()
        
        return estatisticas
    
    def _carregar_alertas(self):
        """Carrega alertas do arquivo"""
        if os.path.exists(self.arquivo_alertas):
            try:
                with open(self.arquivo_alertas, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        
        return []
    
    def _salvar_alertas(self):
        """Salva alertas no arquivo"""
        with open(self.arquivo_alertas, 'w', encoding='utf-8') as f:
            json.dump(self.alertas, f, ensure_ascii=False, indent=4)
