# Modelo de Banco de Dados para Aplicação de Jurisprudência do TCU

Este arquivo contém os scripts SQL para criação do esquema de banco de dados da aplicação de jurisprudência do TCU, conforme a arquitetura definida.

## Tabelas Principais

```sql
-- Tabela de Acórdãos
CREATE TABLE acordaos (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE,
    tipo VARCHAR(100),
    ano INTEGER,
    numero VARCHAR(50),
    titulo TEXT,
    colegiado VARCHAR(100),
    data_sessao DATE,
    relator VARCHAR(100),
    situacao VARCHAR(50),
    sumario TEXT,
    url_arquivo VARCHAR(255),
    url_arquivo_pdf VARCHAR(255),
    url_acordao VARCHAR(255),
    conteudo_completo TEXT,
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Temas
CREATE TABLE temas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    categoria_principal VARCHAR(100)
);

-- Tabela de relacionamento entre Acórdãos e Temas
CREATE TABLE acordaos_temas (
    id SERIAL PRIMARY KEY,
    acordao_id INTEGER REFERENCES acordaos(id),
    tema_id INTEGER REFERENCES temas(id),
    relevancia INTEGER CHECK (relevancia BETWEEN 0 AND 100),
    automatico BOOLEAN DEFAULT TRUE,
    UNIQUE (acordao_id, tema_id)
);

-- Tabela de Classificações
CREATE TABLE classificacoes (
    id SERIAL PRIMARY KEY,
    acordao_id INTEGER REFERENCES acordaos(id),
    impacto INTEGER CHECK (impacto BETWEEN 0 AND 100),
    inovacao INTEGER CHECK (inovacao BETWEEN 0 AND 100),
    relevancia INTEGER CHECK (relevancia BETWEEN 0 AND 100),
    data_classificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo VARCHAR(50) DEFAULT 'IA',
    UNIQUE (acordao_id)
);

-- Tabela de Usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP
);

-- Tabela de Favoritos
CREATE TABLE favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    acordao_id INTEGER REFERENCES acordaos(id),
    data_adicionado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT,
    UNIQUE (usuario_id, acordao_id)
);

-- Tabela de Alertas
CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    tema_id INTEGER REFERENCES temas(id),
    palavras_chave TEXT,
    frequencia VARCHAR(20) CHECK (frequencia IN ('diaria', 'semanal', 'imediata')),
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Insights
CREATE TABLE insights (
    id SERIAL PRIMARY KEY,
    acordao_id INTEGER REFERENCES acordaos(id),
    titulo VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,
    formato VARCHAR(50) CHECK (formato IN ('LinkedIn', 'resumo', 'análise')),
    data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gerado_por VARCHAR(100)
);
```

## Índices para Otimização

```sql
-- Índices para melhorar a performance de consultas
CREATE INDEX idx_acordaos_ano ON acordaos(ano);
CREATE INDEX idx_acordaos_relator ON acordaos(relator);
CREATE INDEX idx_acordaos_colegiado ON acordaos(colegiado);
CREATE INDEX idx_acordaos_data_sessao ON acordaos(data_sessao);
CREATE INDEX idx_acordaos_tipo ON acordaos(tipo);
CREATE INDEX idx_classificacoes_relevancia ON classificacoes(relevancia);
CREATE INDEX idx_classificacoes_impacto ON classificacoes(impacto);
CREATE INDEX idx_classificacoes_inovacao ON classificacoes(inovacao);
CREATE INDEX idx_acordaos_temas_tema_id ON acordaos_temas(tema_id);
CREATE INDEX idx_acordaos_temas_acordao_id ON acordaos_temas(acordao_id);
CREATE INDEX idx_favoritos_usuario_id ON favoritos(usuario_id);
CREATE INDEX idx_alertas_usuario_id ON alertas(usuario_id);
CREATE INDEX idx_alertas_tema_id ON alertas(tema_id);
```

## Funções e Triggers

```sql
-- Função para atualizar o timestamp de última atualização
CREATE OR REPLACE FUNCTION update_ultima_atualizacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ultima_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o timestamp quando um acórdão for modificado
CREATE TRIGGER trigger_update_acordao_timestamp
BEFORE UPDATE ON acordaos
FOR EACH ROW
EXECUTE FUNCTION update_ultima_atualizacao();

-- Função para verificar alertas quando novos acórdãos forem adicionados
CREATE OR REPLACE FUNCTION verificar_alertas()
RETURNS TRIGGER AS $$
BEGIN
    -- Lógica para verificar alertas e notificar usuários
    -- (Implementação depende da estrutura de notificações)
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para verificar alertas quando um novo acórdão for adicionado
CREATE TRIGGER trigger_verificar_alertas
AFTER INSERT ON acordaos
FOR EACH ROW
EXECUTE FUNCTION verificar_alertas();
```

## Dados Iniciais

```sql
-- Inserção de temas iniciais
INSERT INTO temas (nome, descricao, categoria_principal) VALUES
('Licitações e Contratos', 'Temas relacionados a processos licitatórios e contratos administrativos', 'Direito Administrativo'),
('Pregão Eletrônico', 'Modalidade de licitação para aquisição de bens e serviços comuns', 'Licitações e Contratos'),
('Dispensa de Licitação', 'Casos em que a licitação é dispensável', 'Licitações e Contratos'),
('Inexigibilidade', 'Casos em que a licitação é inexigível', 'Licitações e Contratos'),
('Responsabilidade', 'Temas relacionados à responsabilização de agentes', 'Direito Administrativo'),
('Convênio', 'Acordos firmados entre entidades públicas', 'Direito Administrativo'),
('Tomada de Contas Especial', 'Processo para apurar responsabilidade por dano ao erário', 'Direito Administrativo');

-- Inserção de usuário administrador para testes
INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES
('Administrador', 'admin@exemplo.com', '$2a$12$1234567890abcdefghijkl', 'Administrador do Sistema');
```
