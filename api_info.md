# API de Acórdãos do TCU

## Endpoint Principal
```
GET https://dados-abertos.apps.tcu.gov.br/api/acordao/recupera-acordaos?{inicio}&{quantidade}
```

## Parâmetros
- **inicio**: Índice de referência para buscar os Acórdãos. Considerando a lista de Acórdãos disponíveis, o web service retornará {quantidade} acórdãos a partir de {inicio}.
- **quantidade**: Quantidade de Acórdãos retornados pelo web-service.

## Estrutura de Dados Retornada
```json
{
  "key": "string",
  "tipo": "string",
  "anoAcordao": "string",
  "titulo": "string",
  "numeroAcordao": "string",
  "colegiado": "string",
  "dataSessao": "string",
  "relator": "string",
  "situacao": "string",
  "sumario": "string",
  "urlArquivo": "string",
  "urlArquivoPDF": "string",
  "urlAcordao": "string"
}
```

## Descrição dos Campos
- **key**: Chave do Acórdão no banco de dados
- **tipo**: Tipo do Acórdão
- **anoAcordao**: Ano de expedição
- **titulo**: Título do Acórdão
- **numeroAcordao**: Número do Acórdão
- **colegiado**: Colegiado
- **dataSessao**: Data da sessão em que foi expedido o Acórdão (formato DD/MM/AAAAA)
- **relator**: Relator
- **situacao**: Situação
- **sumario**: Sumário
- **urlArquivo**: URL do arquivo do acórdão
- **urlArquivoPDF**: URL do arquivo PDF do acórdão
- **urlAcordao**: URL do acórdão no portal do TCU
