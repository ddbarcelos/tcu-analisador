# README - Aplicação de Jurisprudência do TCU

## Visão Geral

Esta aplicação web permite a pesquisa, análise e exportação de acórdãos do Tribunal de Contas da União (TCU), com foco em licitações e contratos administrativos. Desenvolvida para advogados públicos e consultores jurídicos, a plataforma oferece recursos avançados de filtragem, classificação automática e geração de insights.

## Estrutura do Projeto

```
tcu_app/
├── api_info.md              # Documentação da API do TCU
├── arquitetura.md           # Documentação da arquitetura da aplicação
├── interface_design.md      # Especificações de design da interface
├── prototipo.html           # Protótipo funcional da interface
├── database_model.sql       # Modelo de banco de dados
├── jurisprudencia_api.py    # Implementação da API de jurisprudência
├── exportacao_service.py    # Serviço de exportação de acórdãos
├── alerta_service.py        # Serviço de alertas para novos acórdãos
├── tests.py                 # Testes unitários
└── todo.md                  # Lista de tarefas do projeto
```

## Funcionalidades Principais

### 1. Pesquisa e Filtragem
- Filtros avançados por órgão colegiado, relator, tema, subtema, tipo de decisão, relevância e inovação
- Exclusão automática de acórdãos com termos específicos (aposentadoria, pessoal, pensão, admissão)
- Exclusão de acórdãos de relação
- Busca por texto livre

### 2. Análise e Classificação
- Classificação automática de acórdãos por impacto, inovação e relevância
- Detecção automática de temas e subtemas usando técnicas de processamento de linguagem natural
- Recomendação de acórdãos similares

### 3. Visualização
- Interface com filtros laterais
- Visualização em cards com destaque
- Timeline interativa
- Clusterização por temas

### 4. Exportação
- Exportação em CSV para análise em planilhas
- Exportação em PDF para documentação
- Exportação em JSON para integração com outros sistemas

### 5. Insights e Alertas
- Geração automática de insights para compartilhamento no LinkedIn
- Sistema de alertas para notificação sobre novos acórdãos relevantes

## Requisitos Técnicos

### Backend
- Python 3.8+
- Bibliotecas: requests, pandas, nltk, scikit-learn, pdfkit
- Servidor SMTP para envio de alertas

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap 5
- Compatível com navegadores modernos

### Banco de Dados
- PostgreSQL (recomendado)
- Esquema definido em database_model.sql

## Instalação e Configuração

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/tcu-jurisprudencia.git
cd tcu-jurisprudencia
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure o banco de dados:
```
psql -U seu_usuario -d seu_banco -f database_model.sql
```

4. Configure as credenciais SMTP para o serviço de alertas no arquivo de configuração.

5. Execute os testes:
```
python tests.py
```

6. Inicie a aplicação:
```
python app.py
```

## Uso da API

### Busca de Acórdãos
```python
from jurisprudencia_api import TCUJurisprudenciaAPI

api = TCUJurisprudenciaAPI()
acordaos = api.buscar_acordaos(0, 50)

# Aplicar filtros
filtros = {
    'colegiado': 'Plenário',
    'excluir_termos': ['aposentadoria', 'pessoal', 'pensão', 'admissão'],
    'excluir_relacao': True
}
acordaos_filtrados = api.filtrar_acordaos(acordaos, filtros)
```

### Classificação e Análise
```python
from jurisprudencia_api import AnalisadorAcordaos

analisador = AnalisadorAcordaos()
acordaos_classificados = analisador.classificar_acordaos(acordaos_filtrados)

# Encontrar acórdãos similares
similares = analisador.encontrar_acordaos_similares(acordaos, acordaos[0], 5)
```

### Geração de Insights
```python
from jurisprudencia_api import GeradorInsights

gerador = GeradorInsights()
insight = gerador.gerar_insight(acordao, 'post_padrao')
print(insight)
```

### Exportação
```python
from exportacao_service import ExportacaoService

servico = ExportacaoService()
resultado = servico.exportar(acordaos, 'csv', 'acordaos_exportados.csv')
```

### Alertas
```python
from alerta_service import AlertaService

servico = AlertaService()
servico.adicionar_alerta(
    usuario_id=1,
    email="usuario@exemplo.com",
    temas=["Licitações e Contratos"],
    palavras_chave=["pregão eletrônico"]
)
servico.iniciar_monitoramento()
```

## Próximos Passos

- Implementação de autenticação e gerenciamento de usuários
- Integração com outras bases de jurisprudência
- Desenvolvimento de aplicativo móvel
- Aprimoramento dos algoritmos de IA para classificação e recomendação

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para mais informações, entre em contato com a equipe de desenvolvimento.
