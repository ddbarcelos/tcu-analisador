import os
import sys
import time
import schedule
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

sys.path.append('/home/ubuntu/tcu_app')
from jurisprudencia_api import TCUJurisprudenciaAPI, AnalisadorAcordaos

class AlertaService:
    """
    Serviço para monitoramento e alerta de novos acórdãos do TCU
    """
    def __init__(self, config_file=None):
        self.api = TCUJurisprudenciaAPI()
        self.analisador = AnalisadorAcordaos()
        self.config = self._carregar_config(config_file)
        self.ultimo_check = datetime.now() - timedelta(days=1)  # Inicializa com 1 dia atrás
        self.diretorio_cache = os.path.join(os.getcwd(), 'cache')
        
        # Cria o diretório de cache se não existir
        if not os.path.exists(self.diretorio_cache):
            os.makedirs(self.diretorio_cache)
        
        # Arquivo de cache para armazenar os últimos acórdãos verificados
        self.arquivo_cache = os.path.join(self.diretorio_cache, 'ultimos_acordaos.json')
        
        # Carrega o cache se existir
        self.acordaos_conhecidos = self._carregar_cache()
    
    def _carregar_config(self, config_file):
        """Carrega a configuração do serviço de alertas"""
        config_padrao = {
            'intervalo_verificacao': 24,  # horas
            'quantidade_acordaos': 50,
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_user': 'user@example.com',
            'smtp_password': 'password',
            'email_from': 'alertas@tcujurisprudencia.com',
            'alertas': []
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Mescla com a configuração padrão
                    for key, value in config_padrao.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
        
        return config_padrao
    
    def _carregar_cache(self):
        """Carrega o cache de acórdãos conhecidos"""
        if os.path.exists(self.arquivo_cache):
            try:
                with open(self.arquivo_cache, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")
        
        return []
    
    def _salvar_cache(self, acordaos):
        """Salva o cache de acórdãos conhecidos"""
        try:
            # Extrai apenas as chaves dos acórdãos para economizar espaço
            chaves = [acordao.get('key') for acordao in acordaos if 'key' in acordao]
            
            with open(self.arquivo_cache, 'w', encoding='utf-8') as f:
                json.dump(chaves, f, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def adicionar_alerta(self, usuario_id, email, temas=None, subtemas=None, palavras_chave=None, frequencia='diaria'):
        """
        Adiciona um novo alerta ao sistema
        
        Args:
            usuario_id (int): ID do usuário
            email (str): Email para envio de alertas
            temas (list, optional): Lista de temas para monitorar
            subtemas (list, optional): Lista de subtemas para monitorar
            palavras_chave (list, optional): Lista de palavras-chave para monitorar
            frequencia (str, optional): Frequência de notificação (diaria, semanal, imediata)
        
        Returns:
            int: ID do alerta criado
        """
        alerta = {
            'id': len(self.config['alertas']) + 1,
            'usuario_id': usuario_id,
            'email': email,
            'temas': temas or [],
            'subtemas': subtemas or [],
            'palavras_chave': palavras_chave or [],
            'frequencia': frequencia,
            'ativo': True,
            'data_criacao': datetime.now().isoformat()
        }
        
        self.config['alertas'].append(alerta)
        return alerta['id']
    
    def remover_alerta(self, alerta_id):
        """Remove um alerta do sistema"""
        for i, alerta in enumerate(self.config['alertas']):
            if alerta['id'] == alerta_id:
                del self.config['alertas'][i]
                return True
        return False
    
    def verificar_novos_acordaos(self):
        """
        Verifica se há novos acórdãos e processa alertas
        
        Returns:
            list: Lista de novos acórdãos encontrados
        """
        print(f"Verificando novos acórdãos em {datetime.now().isoformat()}")
        
        # Busca os acórdãos mais recentes
        acordaos = self.api.buscar_acordaos(0, self.config['quantidade_acordaos'])
        
        if not acordaos:
            print("Nenhum acórdão encontrado")
            return []
        
        # Filtra apenas os acórdãos que não estão no cache
        novos_acordaos = []
        for acordao in acordaos:
            if 'key' in acordao and acordao['key'] not in self.acordaos_conhecidos:
                novos_acordaos.append(acordao)
        
        if not novos_acordaos:
            print("Nenhum novo acórdão encontrado")
            return []
        
        print(f"Encontrados {len(novos_acordaos)} novos acórdãos")
        
        # Classifica os novos acórdãos
        acordaos_classificados = self.analisador.classificar_acordaos(novos_acordaos)
        
        # Processa alertas para os novos acórdãos
        self._processar_alertas(acordaos_classificados)
        
        # Atualiza o cache com os novos acórdãos
        self._atualizar_cache(acordaos)
        
        return novos_acordaos
    
    def _atualizar_cache(self, acordaos):
        """Atualiza o cache com os novos acórdãos"""
        # Extrai as chaves dos acórdãos
        chaves = [acordao.get('key') for acordao in acordaos if 'key' in acordao]
        
        # Atualiza a lista de acórdãos conhecidos
        self.acordaos_conhecidos = chaves
        
        # Salva o cache atualizado
        self._salvar_cache(acordaos)
    
    def _processar_alertas(self, acordaos):
        """
        Processa alertas para os acórdãos fornecidos
        
        Args:
            acordaos (list): Lista de acórdãos classificados
        """
        if not acordaos or not self.config['alertas']:
            return
        
        # Agrupa acórdãos por alerta
        alertas_para_enviar = {}
        
        for alerta in self.config['alertas']:
            if not alerta['ativo']:
                continue
            
            # Filtra acórdãos relevantes para este alerta
            acordaos_relevantes = self._filtrar_acordaos_para_alerta(acordaos, alerta)
            
            if acordaos_relevantes:
                # Adiciona à lista de alertas para enviar
                if alerta['email'] not in alertas_para_enviar:
                    alertas_para_enviar[alerta['email']] = {
                        'usuario_id': alerta['usuario_id'],
                        'acordaos': []
                    }
                
                alertas_para_enviar[alerta['email']]['acordaos'].extend(acordaos_relevantes)
        
        # Envia os alertas
        for email, dados in alertas_para_enviar.items():
            self._enviar_alerta_email(email, dados['usuario_id'], dados['acordaos'])
    
    def _filtrar_acordaos_para_alerta(self, acordaos, alerta):
        """
        Filtra acórdãos relevantes para um alerta específico
        
        Args:
            acordaos (list): Lista de acórdãos classificados
            alerta (dict): Configuração do alerta
            
        Returns:
            list: Lista de acórdãos relevantes para o alerta
        """
        acordaos_relevantes = []
        
        for acordao in acordaos:
            relevante = False
            
            # Verifica temas
            if alerta['temas'] and 'temas' in acordao:
                if any(tema in acordao['temas'] for tema in alerta['temas']):
                    relevante = True
            
            # Verifica subtemas
            if not relevante and alerta['subtemas'] and 'subtemas' in acordao:
                if any(subtema in acordao['subtemas'] for subtema in alerta['subtemas']):
                    relevante = True
            
            # Verifica palavras-chave
            if not relevante and alerta['palavras_chave']:
                sumario = acordao.get('sumario', '').lower()
                titulo = acordao.get('titulo', '').lower()
                texto_completo = f"{sumario} {titulo}"
                
                if any(palavra.lower() in texto_completo for palavra in alerta['palavras_chave']):
                    relevante = True
            
            if relevante:
                acordaos_relevantes.append(acordao)
        
        return acordaos_relevantes
    
    def _enviar_alerta_email(self, email, usuario_id, acordaos):
        """
        Envia alerta por email
        
        Args:
            email (str): Email do destinatário
            usuario_id (int): ID do usuário
            acordaos (list): Lista de acórdãos para incluir no alerta
        """
        try:
            # Cria a mensagem
            msg = MIMEMultipart()
            msg['From'] = self.config['email_from']
            msg['To'] = email
            msg['Subject'] = f"Alerta de Novos Acórdãos do TCU - {datetime.now().strftime('%d/%m/%Y')}"
            
            # Corpo do email
            corpo = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .acordao {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    .header {{ font-weight: bold; margin-bottom: 5px; }}
                    .metadata {{ color: #666; margin-bottom: 5px; }}
                    .sumario {{ margin-top: 10px; }}
                    .link {{ margin-top: 10px; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #999; }}
                </style>
            </head>
            <body>
                <h2>Novos Acórdãos do TCU</h2>
                <p>Olá,</p>
                <p>Encontramos {len(acordaos)} novo(s) acórdão(s) que correspondem aos seus critérios de alerta:</p>
            """
            
            # Adiciona os acórdãos
            for acordao in acordaos:
                corpo += f"""
                <div class="acordao">
                    <div class="header">ACÓRDÃO Nº {acordao.get('numeroAcordao', 'N/A')}/{acordao.get('anoAcordao', 'N/A')} - {acordao.get('colegiado', 'N/A')}</div>
                    <div class="metadata">Relator: {acordao.get('relator', 'N/A')} | Data: {acordao.get('dataSessao', 'N/A')}</div>
                """
                
                # Adiciona temas e subtemas se existirem
                if 'temas' in acordao and acordao['temas']:
                    corpo += f'<div class="metadata">Temas: {", ".join(acordao["temas"])}</div>'
                
                if 'subtemas' in acordao and acordao['subtemas']:
                    corpo += f'<div class="metadata">Subtemas: {", ".join(acordao["subtemas"])}</div>'
                
                corpo += f"""
                    <div class="sumario">{acordao.get('sumario', 'Sumário não disponível')}</div>
                    <div class="link"><a href="{acordao.get('urlAcordao', '#')}">Ver acórdão completo</a></div>
                </div>
                """
            
            corpo += """
                <p>Acesse a plataforma para mais detalhes e funcionalidades.</p>
                <div class="footer">
                    <p>Este é um email automático. Por favor, não responda.</p>
                    <p>Para cancelar ou modificar seus alertas, acesse a plataforma.</p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(corpo, 'html'))
            
            # Configura o servidor SMTP
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['smtp_user'], self.config['smtp_password'])
            
            # Envia o email
            server.send_message(msg)
            server.quit()
            
            print(f"Alerta enviado para {email} com {len(acordaos)} acórdãos")
            
        except Exception as e:
            print(f"Erro ao enviar alerta por email: {e}")
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento periódico de novos acórdãos"""
        # Verifica imediatamente na primeira execução
        self.verificar_novos_acordaos()
        
        # Agenda verificações periódicas
        intervalo = self.config['intervalo_verificacao']
        
        if intervalo == 24:  # Diário
            schedule.every().day.at("08:00").do(self.verificar_novos_acordaos)
        elif intervalo == 168:  # Semanal (7 dias)
            schedule.every().monday.at("08:00").do(self.verificar_novos_acordaos)
        else:  # Intervalo personalizado em horas
            schedule.every(intervalo).hours.do(self.verificar_novos_acordaos)
        
        print(f"Monitoramento iniciado. Próxima verificação em {intervalo} horas.")
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto se há tarefas pendentes
        except KeyboardInterrupt:
            print("Monitoramento interrompido pelo usuário")


# Exemplo de uso
if __name__ == "__main__":
    # Cria o serviço de alertas
    servico = AlertaService()
    
    # Adiciona alguns alertas de exemplo
    servico.adicionar_alerta(
        usuario_id=1,
        email="usuario1@exemplo.com",
        temas=["Licitações e Contratos"],
        palavras_chave=["pregão eletrônico", "dispensa"],
        frequencia="diaria"
    )
    
    servico.adicionar_alerta(
        usuario_id=2,
        email="usuario2@exemplo.com",
        subtemas=["Tomada de Contas Especial"],
        frequencia="semanal"
    )
    
    # Inicia o monitoramento
    servico.iniciar_monitoramento()
