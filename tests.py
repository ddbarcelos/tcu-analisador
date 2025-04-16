import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
sys.path.append('/home/ubuntu/tcu_app')

from jurisprudencia_api import TCUJurisprudenciaAPI, AnalisadorAcordaos, GeradorInsights, ExportadorAcordaos

class TestTCUJurisprudenciaAPI(unittest.TestCase):
    """Testes para a classe TCUJurisprudenciaAPI"""
    
    @patch('jurisprudencia_api.requests.get')
    def test_buscar_acordaos(self, mock_get):
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.json.return_value = [{"key": "123", "titulo": "Teste"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Executar o método
        api = TCUJurisprudenciaAPI()
        resultado = api.buscar_acordaos(0, 10)
        
        # Verificar resultados
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["key"], "123")
        mock_get.assert_called_once()
    
    def test_filtrar_acordaos(self):
        # Dados de teste
        acordaos = [
            {"colegiado": "Plenário", "relator": "Ministro A", "anoAcordao": "2023", "sumario": "Teste de licitação"},
            {"colegiado": "Primeira Câmara", "relator": "Ministro B", "anoAcordao": "2022", "sumario": "Teste de aposentadoria"},
            {"colegiado": "Plenário", "relator": "Ministro A", "anoAcordao": "2023", "sumario": "Teste de relação", "titulo": "Acórdão de relação"}
        ]
        
        # Filtrar por colegiado
        api = TCUJurisprudenciaAPI()
        filtros = {"colegiado": "Plenário"}
        resultado = api.filtrar_acordaos(acordaos, filtros)
        self.assertEqual(len(resultado), 2)
        
        # Filtrar por relator
        filtros = {"relator": "Ministro B"}
        resultado = api.filtrar_acordaos(acordaos, filtros)
        self.assertEqual(len(resultado), 1)
        
        # Excluir termos específicos
        filtros = {"excluir_termos": ["aposentadoria"]}
        resultado = api.filtrar_acordaos(acordaos, filtros)
        self.assertEqual(len(resultado), 2)
        
        # Excluir acórdãos de relação
        filtros = {"excluir_relacao": True}
        resultado = api.filtrar_acordaos(acordaos, filtros)
        self.assertEqual(len(resultado), 2)
        
        # Combinação de filtros
        filtros = {
            "colegiado": "Plenário",
            "excluir_relacao": True
        }
        resultado = api.filtrar_acordaos(acordaos, filtros)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["sumario"], "Teste de licitação")


class TestAnalisadorAcordaos(unittest.TestCase):
    """Testes para a classe AnalisadorAcordaos"""
    
    def test_classificar_acordaos(self):
        # Dados de teste
        acordaos = [
            {
                "sumario": "Importante precedente sobre licitação. Determinação de multa com grande impacto.",
                "titulo": "Acórdão sobre licitação"
            },
            {
                "sumario": "Novo entendimento sobre convênios. Revisão da jurisprudência anterior.",
                "titulo": "Acórdão inovador sobre convênios"
            }
        ]
        
        # Classificar acórdãos
        analisador = AnalisadorAcordaos()
        resultado = analisador.classificar_acordaos(acordaos)
        
        # Verificar resultados
        self.assertEqual(len(resultado), 2)
        
        # Verificar classificações do primeiro acórdão
        self.assertIn('relevancia', resultado[0])
        self.assertIn('impacto', resultado[0])
        self.assertIn('inovacao', resultado[0])
        self.assertIn('temas', resultado[0])
        
        # Verificar temas identificados
        self.assertIn('Licitações e Contratos', resultado[0]['temas'])
        self.assertIn('Convênio', resultado[1]['temas'])
    
    def test_encontrar_acordaos_similares(self):
        # Dados de teste
        acordaos = [
            {
                "sumario": "Licitação para contratação de serviços de TI",
                "titulo": "Acórdão sobre licitação de TI"
            },
            {
                "sumario": "Licitação para aquisição de equipamentos de informática",
                "titulo": "Acórdão sobre compra de equipamentos"
            },
            {
                "sumario": "Convênio para construção de escola",
                "titulo": "Acórdão sobre convênio"
            }
        ]
        
        acordao_referencia = {
            "sumario": "Pregão eletrônico para contratação de serviços de TI",
            "titulo": "Acórdão sobre contratação de TI"
        }
        
        # Encontrar acórdãos similares
        analisador = AnalisadorAcordaos()
        resultado = analisador.encontrar_acordaos_similares(acordaos, acordao_referencia, 2)
        
        # Verificar resultados
        self.assertEqual(len(resultado), 2)
        # O primeiro resultado deve ser o mais similar (sobre TI)
        self.assertIn("TI", resultado[0]["titulo"])


class TestGeradorInsights(unittest.TestCase):
    """Testes para a classe GeradorInsights"""
    
    def test_gerar_insight(self):
        # Dados de teste
        acordao = {
            "numeroAcordao": "1234",
            "anoAcordao": "2023",
            "colegiado": "Plenário",
            "relator": "Ministro Teste",
            "dataSessao": "15/03/2023",
            "sumario": "Representação formulada a partir de trabalho realizado pela Secretaria de Controle Externo versando sobre pregão eletrônico. Análise de oitivas. Procedência parcial. Determinações.",
            "temas": ["Licitações e Contratos"],
            "subtemas": ["Pregão Eletrônico"]
        }
        
        # Gerar insights em diferentes formatos
        gerador = GeradorInsights()
        
        # Formato padrão
        insight_padrao = gerador.gerar_insight(acordao, 'post_padrao')
        self.assertIn("#Licitações", insight_padrao)
        self.assertIn("Acórdão 1234/2023", insight_padrao)
        self.assertIn("Ministro Teste", insight_padrao)
        
        # Formato análise detalhada
        insight_analise = gerador.gerar_insight(acordao, 'analise_detalhada')
        self.assertIn("#AnáliseJurídica", insight_analise)
        self.assertIn("ANÁLISE DE JURISPRUDÊNCIA DO TCU", insight_analise)
        
        # Formato dica rápida
        insight_dica = gerador.gerar_insight(acordao, 'dica_rapida')
        self.assertIn("#DicaRápida", insight_dica)
        self.assertIn("VOCÊ SABIA?", insight_dica)


class TestExportadorAcordaos(unittest.TestCase):
    """Testes para a classe ExportadorAcordaos"""
    
    def setUp(self):
        # Criar diretório temporário para testes
        self.temp_dir = "/tmp/tcu_test"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def tearDown(self):
        # Limpar arquivos de teste
        for arquivo in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, arquivo))
        os.rmdir(self.temp_dir)
    
    def test_exportar_csv(self):
        # Dados de teste
        acordaos = [
            {
                "numeroAcordao": "1234",
                "anoAcordao": "2023",
                "colegiado": "Plenário",
                "relator": "Ministro Teste",
                "dataSessao": "15/03/2023",
                "titulo": "Título de teste",
                "sumario": "Sumário de teste",
                "urlAcordao": "https://exemplo.com/acordao"
            }
        ]
        
        # Exportar para CSV
        exportador = ExportadorAcordaos()
        caminho_arquivo = os.path.join(self.temp_dir, "teste.csv")
        resultado = exportador.exportar_csv(acordaos, caminho_arquivo)
        
        # Verificar resultados
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(caminho_arquivo))
    
    def test_exportar_json(self):
        # Dados de teste
        acordaos = [
            {
                "numeroAcordao": "1234",
                "anoAcordao": "2023",
                "colegiado": "Plenário",
                "relator": "Ministro Teste"
            }
        ]
        
        # Exportar para JSON
        exportador = ExportadorAcordaos()
        caminho_arquivo = os.path.join(self.temp_dir, "teste.json")
        resultado = exportador.exportar_json(acordaos, caminho_arquivo)
        
        # Verificar resultados
        self.assertTrue(resultado)
        self.assertTrue(os.path.exists(caminho_arquivo))
        
        # Verificar conteúdo do JSON
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            self.assertEqual(len(dados), 1)
            self.assertEqual(dados[0]["numeroAcordao"], "1234")
    
    def test_gerar_html_para_pdf(self):
        # Dados de teste
        acordaos = [
            {
                "numeroAcordao": "1234",
                "anoAcordao": "2023",
                "colegiado": "Plenário",
                "relator": "Ministro Teste",
                "dataSessao": "15/03/2023",
                "sumario": "Sumário de teste",
                "urlAcordao": "https://exemplo.com/acordao"
            }
        ]
        
        # Gerar HTML para PDF
        exportador = ExportadorAcordaos()
        html = exportador.gerar_html_para_pdf(acordaos)
        
        # Verificar resultados
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("ACÓRDÃO Nº 1234/2023", html)
        self.assertIn("Ministro Teste", html)


if __name__ == '__main__':
    unittest.main()
