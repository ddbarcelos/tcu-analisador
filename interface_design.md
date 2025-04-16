# Proposta Visual da Interface

## 1. Visão Geral da Interface

A interface da aplicação de jurisprudência do TCU será projetada com foco na usabilidade, eficiência e experiência do usuário, especialmente para advogados públicos e consultores jurídicos. O design seguirá uma abordagem moderna e limpa, com ênfase na facilidade de acesso às informações e ferramentas de análise.

## 2. Layout Principal

### Estrutura de Tela
```
+-----------------------------------------------------------------------+
|                           CABEÇALHO/MENU                              |
+---------------+-------------------------------------------------------+
|               |                                                       |
|               |                                                       |
|    FILTROS    |                 ÁREA DE RESULTADOS                    |
|    LATERAIS   |                 (CARDS/TIMELINE)                      |
|               |                                                       |
|               |                                                       |
+---------------+-------------------------------------------------------+
|                              RODAPÉ                                   |
+-----------------------------------------------------------------------+
```

### Componentes Principais

#### Cabeçalho/Menu
- Logo da aplicação
- Barra de pesquisa global (busca por texto livre)
- Menu de navegação principal (Dashboard, Pesquisa, Favoritos, Alertas, Insights)
- Área de usuário (perfil, configurações, notificações)

#### Painel de Filtros Laterais
- Filtros por órgão colegiado (Plenário, 1ª Câmara, 2ª Câmara)
- Filtros por relator (lista dinâmica de relatores)
- Filtros por tema e subtema (estrutura hierárquica)
- Filtros por tipo de decisão
- Filtros por relevância, impacto e inovação (sliders)
- Filtros por período (seletor de datas)
- Opções de exclusão (aposentadoria, pessoal, pensão, admissão)
- Opção para excluir acórdãos de relação
- Botão de aplicar filtros
- Botão de limpar filtros
- Opção para salvar conjunto de filtros

#### Área de Resultados
- Alternância entre visualizações (cards, lista, timeline)
- Ordenação dos resultados (data, relevância, impacto)
- Indicador de total de resultados e paginação
- Botão de exportação (CSV, PDF, JSON)

## 3. Componentes Detalhados

### Cards de Acórdãos
```
+-----------------------------------------------------------------------+
| [ÍCONE TIPO] ACÓRDÃO Nº 123/2023 - PLENÁRIO                [FAVORITO] |
+-----------------------------------------------------------------------+
| Relator: Ministro XXXXX                       Data: 15/03/2023        |
+-----------------------------------------------------------------------+
| Tema: Licitações e Contratos                                          |
| Subtema: Pregão Eletrônico                                            |
+-----------------------------------------------------------------------+
| SUMÁRIO:                                                              |
| Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do       |
| eiusmod tempor incididunt ut labore et dolore magna aliqua...         |
+-----------------------------------------------------------------------+
| TAGS: #PregãoEletrônico #Habilitação #DocumentaçãoTécnica            |
+-----------------------------------------------------------------------+
|                                                                       |
| [Ver Inteiro] [Salvar] [Compartilhar] [Gerar Insight]                 |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Timeline Interativa
- Linha do tempo vertical ou horizontal
- Marcos temporais representando acórdãos
- Agrupamento visual por períodos (meses, anos)
- Indicadores visuais de relevância/impacto
- Zoom para ajustar a visualização temporal
- Filtros rápidos na própria timeline

### Clusterização por Temas
- Visualização em formato de mapa de calor ou gráfico de bolhas
- Tamanho das bolhas representando quantidade de acórdãos
- Cores representando diferentes temas principais
- Interatividade para explorar subtemas
- Opção para filtrar resultados por cluster selecionado

### Visualizador de Acórdão Completo
```
+-----------------------------------------------------------------------+
| < VOLTAR AOS RESULTADOS                                               |
+-----------------------------------------------------------------------+
| ACÓRDÃO Nº 123/2023 - PLENÁRIO                                        |
| Relator: Ministro XXXXX                                               |
| Data da Sessão: 15/03/2023                                            |
+-----------------------------------------------------------------------+
| MENU DO DOCUMENTO | CONTEÚDO COMPLETO DO ACÓRDÃO                      |
| - Ementa          |                                                   |
| - Sumário         | Lorem ipsum dolor sit amet, consectetur           |
| - Relatório       | adipiscing elit. Sed do eiusmod tempor            |
| - Voto            | incididunt ut labore et dolore magna aliqua.      |
| - Acórdão         | Ut enim ad minim veniam, quis nostrud             |
| - Anexos          | exercitation ullamco laboris nisi ut              |
|                   | aliquip ex ea commodo consequat...                |
+-------------------+---------------------------------------------------+
| FERRAMENTAS:                                                          |
| [Destacar] [Anotar] [Exportar] [Compartilhar] [Gerar Insight]         |
+-----------------------------------------------------------------------+
```

### Gerador de Insights
```
+-----------------------------------------------------------------------+
| GERAR INSIGHT PARA LINKEDIN                                           |
+-----------------------------------------------------------------------+
| Acórdão: Nº 123/2023 - PLENÁRIO                                       |
+-----------------------------------------------------------------------+
| Formato:  [X] Post Padrão  [ ] Análise Detalhada  [ ] Dica Rápida     |
+-----------------------------------------------------------------------+
| Título Sugerido:                                                      |
| TCU define novos critérios para habilitação em Pregão Eletrônico      |
+-----------------------------------------------------------------------+
| Conteúdo Gerado:                                                      |
| #Licitações #TCU #NovoEntendimento                                    |
|                                                                       |
| O TCU, por meio do Acórdão 123/2023-Plenário, estabeleceu importante  |
| precedente sobre documentação técnica em Pregão Eletrônico.           |
|                                                                       |
| Principais pontos:                                                    |
| ✅ Exigência de atestados deve ser proporcional ao objeto             |
| ✅ Vedada a restrição geográfica injustificada                        |
| ✅ Qualificação técnica limitada ao mínimo necessário                 |
|                                                                       |
| 📌 Relator: Min. XXXXX                                                |
| 📌 Data: 15/03/2023                                                   |
|                                                                       |
| #DireitoAdministrativo #Licitações #NovaJurisprudência                |
+-----------------------------------------------------------------------+
| [Editar] [Copiar] [Compartilhar Diretamente]                          |
+-----------------------------------------------------------------------+
```

### Sistema de Alertas
```
+-----------------------------------------------------------------------+
| CONFIGURAÇÃO DE ALERTAS                                               |
+-----------------------------------------------------------------------+
| Novo Alerta                                                           |
+-----------------------------------------------------------------------+
| Nome do Alerta: Monitoramento de Licitações                           |
+-----------------------------------------------------------------------+
| Critérios:                                                            |
| [ ] Temas:      [X] Licitações e Contratos                            |
|                 [X] Pregão Eletrônico                                 |
|                 [ ] Concorrência                                      |
|                                                                       |
| [ ] Relatores:  [X] Todos                                             |
|                 [ ] Selecionar específicos                            |
|                                                                       |
| [ ] Palavras-chave: pregão, habilitação, proposta inexequível         |
+-----------------------------------------------------------------------+
| Frequência:     [ ] Imediata  [X] Diária  [ ] Semanal                 |
+-----------------------------------------------------------------------+
| Formato:        [X] Email  [ ] Notificação no sistema                 |
+-----------------------------------------------------------------------+
| [Cancelar]                           [Salvar Alerta]                  |
+-----------------------------------------------------------------------+
```

## 4. Elementos de Design

### Paleta de Cores
- **Cor Principal**: Azul institucional (#1A5276)
- **Cor Secundária**: Verde (#27AE60)
- **Cores de Destaque**: Laranja (#E67E22), Vermelho (#C0392B)
- **Cores Neutras**: Cinza claro (#F2F3F4), Cinza médio (#BDC3C7), Cinza escuro (#34495E)
- **Texto**: Preto (#17202A), Branco (#FFFFFF)

### Tipografia
- **Fonte Principal**: Roboto ou Open Sans
- **Títulos**: Semi-bold, 18-24px
- **Corpo de Texto**: Regular, 14-16px
- **Metadados**: Light, 12-14px

### Iconografia
- Ícones minimalistas e consistentes
- Indicadores visuais de relevância e impacto
- Badges para identificação rápida de tipos de acórdãos
- Marcadores de status (novo, relevante, inovador)

## 5. Responsividade e Adaptação

### Versão Mobile
- Menu hamburger para acesso aos filtros
- Cards em formato de lista simplificada
- Botões de ação flutuantes
- Visualização otimizada para telas menores

### Versão Tablet
- Layout híbrido com filtros recolhíveis
- Visualização adaptada dos cards
- Acesso rápido às funcionalidades principais

### Acessibilidade
- Contraste adequado para leitura
- Suporte a leitores de tela
- Tamanho de fonte ajustável
- Navegação por teclado

## 6. Interações e Microinterações

### Filtros Dinâmicos
- Atualização em tempo real dos resultados ao aplicar filtros
- Indicadores visuais de filtros ativos
- Sugestões de filtros baseados em padrões de uso

### Feedback Visual
- Animações sutis para transições entre estados
- Indicadores de carregamento para operações assíncronas
- Notificações para ações completadas

### Gestos (Mobile)
- Deslizar para navegar entre acórdãos
- Pinçar para zoom na timeline
- Tocar duas vezes para expandir detalhes
