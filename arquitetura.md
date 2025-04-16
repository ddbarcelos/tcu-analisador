# Arquitetura da Aplicação de Jurisprudência do TCU

## 1. Visão Geral

A aplicação será desenvolvida como uma aplicação web moderna, utilizando uma arquitetura de três camadas:

1. **Frontend**: Interface de usuário responsiva e intuitiva
2. **Backend**: API RESTful para processamento de dados e lógica de negócio
3. **Banco de Dados**: Armazenamento estruturado dos acórdãos e metadados

## 2. Estrutura da Base de Dados

### Modelo de Dados Principal

#### Tabela: Acordaos
```
- id (PK): Identificador único interno
- key: Chave do acórdão no banco de dados do TCU
- tipo: Tipo do acórdão
- ano: Ano de expedição
- numero: Número do acórdão
- titulo: Título do acórdão
- colegiado: Órgão colegiado que emitiu o acórdão
- data_sessao: Data da sessão em que foi expedido
- relator: Nome do relator
- situacao: Situação atual do acórdão
- sumario: Texto resumido do conteúdo
- url_arquivo: Link para o arquivo original
- url_arquivo_pdf: Link para o arquivo em PDF
- url_acordao: Link para o acórdão no portal do TCU
- conteudo_completo: Texto completo do acórdão (quando disponível)
- data_importacao: Data em que o acórdão foi importado para o sistema
- ultima_atualizacao: Data da última atualização do registro
```

#### Tabela: Temas
```
- id (PK): Identificador único
- nome: Nome do tema
- descricao: Descrição detalhada do tema
- categoria_principal: Categoria principal à qual o tema pertence
```

#### Tabela: AcordaosTemas (Relacionamento N:N)
```
- id (PK): Identificador único
- acordao_id (FK): Referência ao acórdão
- tema_id (FK): Referência ao tema
- relevancia: Pontuação de relevância do tema para o acórdão (0-100)
- automatico: Flag indicando se a classificação foi automática ou manual
```

#### Tabela: Classificacoes
```
- id (PK): Identificador único
- acordao_id (FK): Referência ao acórdão
- impacto: Pontuação de impacto (0-100)
- inovacao: Pontuação de inovação (0-100)
- relevancia: Pontuação de relevância geral (0-100)
- data_classificacao: Data em que a classificação foi realizada
- metodo: Método utilizado para classificação (IA, manual, híbrido)
```

#### Tabela: Usuarios
```
- id (PK): Identificador único
- nome: Nome completo do usuário
- email: Email do usuário (usado para login)
- senha_hash: Hash da senha
- cargo: Cargo/função do usuário
- data_cadastro: Data de cadastro
- ultimo_acesso: Data do último acesso
```

#### Tabela: Favoritos
```
- id (PK): Identificador único
- usuario_id (FK): Referência ao usuário
- acordao_id (FK): Referência ao acórdão
- data_adicionado: Data em que foi adicionado aos favoritos
- notas: Notas pessoais do usuário sobre o acórdão
```

#### Tabela: Alertas
```
- id (PK): Identificador único
- usuario_id (FK): Referência ao usuário
- tema_id (FK): Referência ao tema (opcional)
- palavras_chave: Palavras-chave para monitoramento
- frequencia: Frequência de notificação (diária, semanal, imediata)
- ativo: Status do alerta
- data_criacao: Data de criação do alerta
```

#### Tabela: Insights
```
- id (PK): Identificador único
- acordao_id (FK): Referência ao acórdão
- titulo: Título do insight
- conteudo: Conteúdo do insight
- formato: Formato do insight (LinkedIn, resumo, análise)
- data_geracao: Data de geração do insight
- gerado_por: Identificador do usuário ou sistema que gerou
```

## 3. Arquitetura de Software

### Backend (API RESTful)

**Tecnologias Sugeridas:**
- Python com FastAPI ou Django REST Framework
- Node.js com Express

**Componentes Principais:**
1. **API Gateway**: Gerenciamento de requisições e autenticação
2. **Serviço de Acórdãos**: Busca, filtragem e manipulação de acórdãos
3. **Serviço de Classificação**: Classificação automática por IA
4. **Serviço de Alertas**: Monitoramento e notificação de novos acórdãos
5. **Serviço de Insights**: Geração automática de insights para redes sociais
6. **Serviço de Exportação**: Exportação em diferentes formatos (CSV, PDF, JSON)

### Frontend (SPA)

**Tecnologias Sugeridas:**
- React.js com Material UI ou Tailwind CSS
- Vue.js com Vuetify

**Componentes Principais:**
1. **Painel de Filtros**: Interface lateral para filtros avançados
2. **Visualização de Resultados**: Cards com destaque e timeline interativa
3. **Visualizador de Acórdãos**: Interface para leitura e análise de acórdãos
4. **Painel de Administração**: Gerenciamento de usuários e configurações
5. **Gerador de Insights**: Interface para criação e edição de insights
6. **Sistema de Alertas**: Configuração e visualização de alertas

### Inteligência Artificial

**Componentes de IA:**
1. **Classificador de Temas**: Utilização de embeddings ou BERTopic para detecção automática de temas
2. **Avaliador de Impacto**: Algoritmo para classificação de impacto dos acórdãos
3. **Detector de Inovação**: Sistema para identificar precedentes inovadores
4. **Recomendador de Acórdãos**: Sistema de recomendação baseado em similaridade
5. **Gerador de Insights**: Processamento de linguagem natural para gerar resumos e insights

## 4. Fluxo de Dados

1. **Importação de Dados**:
   - Consumo periódico da API do TCU para obter novos acórdãos
   - Processamento e armazenamento no banco de dados local
   - Classificação automática por temas, impacto e inovação

2. **Consulta e Filtragem**:
   - Recebimento de parâmetros de filtro do frontend
   - Execução de consultas otimizadas no banco de dados
   - Retorno de resultados paginados e ordenados

3. **Geração de Insights**:
   - Análise do conteúdo dos acórdãos
   - Extração de pontos relevantes
   - Geração de textos formatados para LinkedIn

4. **Sistema de Alertas**:
   - Monitoramento contínuo de novos acórdãos
   - Comparação com critérios de alerta dos usuários
   - Envio de notificações quando houver correspondência

## 5. Considerações de Segurança e Desempenho

1. **Segurança**:
   - Autenticação JWT para acesso à API
   - Criptografia de dados sensíveis
   - Proteção contra ataques comuns (CSRF, XSS, SQL Injection)

2. **Desempenho**:
   - Indexação otimizada do banco de dados
   - Cache de consultas frequentes
   - Paginação e carregamento sob demanda
   - Compressão de respostas HTTP

3. **Escalabilidade**:
   - Arquitetura modular para facilitar escalabilidade horizontal
   - Processamento assíncrono para tarefas intensivas
   - Filas de mensagens para operações em lote
