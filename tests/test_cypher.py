import unittest
from services.validation_service import validar_lote, extrair_massa_referencia_g
from services.catalog_service import buscar_produto_local
from services.analysis_service import estimar_analise, PERFIS, validar_percentuais
from services.economic_service import calcular_valor_economico, calcular_valor_material
from services.export_service import gerar_csv_analise
from services.tales_service import gerar_resumo_tales
from services.batch_service import analisar_linha
from services.tales_chat_service import responder_tales
from services.wikidata_service import modelo_compativel, selecionar_resultado
from services.analysis_service import validar_percentuais


class TestCypher(unittest.TestCase):
    def test_tales_orienta_logistica_reversa(self):
        for pergunta in ("Como posso iniciar a logística reversa?", "Quais os primeiros passos?", "Como descartar eletrônicos?"):
            resposta, fonte = responder_tales(pergunta, ["Resumo genérico."], usar_ia=False)
            self.assertIn("Inventarie", resposta)
            self.assertIn("operador de logística reversa", resposta)
            self.assertNotIn("Resumo genérico", resposta)
            self.assertIn("Local", fonte)

    def test_tales_interativo_local(self):
        resposta, origem = responder_tales(
            "Qual foi o valor?", ["O valor bruto teórico é R$ 339,12.", "Recuperação indeterminada."],
            usar_ia=False
        )
        self.assertIn("339,12", resposta)
        self.assertIn("Local", origem)

    def test_wikidata_modelo_exato(self):
        self.assertTrue(modelo_compativel("Samsung Galaxy M55 5G", "Samsung Galaxy M55 5G"))
        self.assertFalse(modelo_compativel("Samsung Galaxy M55 5G", "Samsung Galaxy M55s 5G"))
        self.assertFalse(modelo_compativel("Samsung Galaxy M55 5G", "Xiaomi M55 5G"))

    def test_wikidata_descarta_modelo_parecido(self):
        achado = selecionar_resultado(
            "Samsung Galaxy M55 5G",
            [{"id": "Q123", "label": "Samsung Galaxy M55s 5G"},
             {"id": "Q456", "label": "Samsung Galaxy M55 5G"}],
        )
        self.assertEqual(achado["id"], "Q456")
        self.assertFalse(selecionar_resultado("Samsung Galaxy M55 5G",
            [{"id": "Q123", "label": "Samsung Galaxy M55s 5G"}])["encontrado"])

    def test_tales_resumo_valido(self):
        frases = gerar_resumo_tales(
            equipamento_informado="Samsung M55 5G", modelo_identificado="Galaxy M55 5G",
            quantidade=10, massa_total_g=1800, massa_media_g=180,
            fontes=["Catálogo local", "MobileAPI"], alertas=[],
            materiais=[{"material": "Ouro", "massa_estimada_g": 0.54}],
            valor_bruto=339.12, massa_sem_preco_g=270.9,
            massa_recuperavel_g=None, percentual_recuperavel=None,
        )
        texto = " ".join(frases)
        self.assertIn("Galaxy M55 5G", texto)
        self.assertIn("339,12", texto)
        self.assertIn("não determinados", texto)

    def test_tales_nao_inventa_valor_em_entrada_suspeita(self):
        frases = gerar_resumo_tales(
            equipamento_informado="Equipamento incerto", modelo_identificado=None,
            quantidade=10, massa_total_g=20000, massa_media_g=2000,
            fontes=[], alertas=["Massa incomum"], materiais=[],
            valor_bruto=None, massa_sem_preco_g=None,
            massa_recuperavel_g=None, percentual_recuperavel=None,
        )
        texto = " ".join(frases)
        self.assertIn("Massa incomum", texto)
        self.assertIn("não foi calculado", texto)
        self.assertNotIn("R$ 0", texto)

    def test_importacao_em_lote(self):
        resultado = analisar_linha("Samsung Galaxy M55 5G", 10, 1800)
        self.assertEqual(resultado["quantidade"], 10)
        self.assertAlmostEqual(resultado["massa_media_g"], 180)
        self.assertIsNone(resultado["massa_recuperavel_g"])

    def test_importacao_invalida(self):
        for quantidade, massa in [(0, 100), (2.5, 100), (1, -10)]:
            with self.assertRaises(ValueError):
                analisar_linha("Teste", quantidade, massa)

    def test_lote_valido(self):
        r = validar_lote(10, 1800, "phone", 180)
        self.assertAlmostEqual(r["massa_media_g"], 180)
        self.assertFalse(r["alertas"])

    def test_desvio_alerta(self):
        r = validar_lote(10, 20000, "phone", 180)
        self.assertTrue(r["alertas"])
        self.assertFalse(r["confiavel_para_valoracao"])

    def test_invalido(self):
        for quantidade, massa in [(0, 100), (1, -1), (1, float("nan"))]:
            with self.assertRaises(ValueError):
                validar_lote(quantidade, massa, "phone")

    def test_massa_referencia(self):
        self.assertEqual(extrair_massa_referencia_g("0,18 kg"), 180)
        self.assertIsNone(extrair_massa_referencia_g("desconhecido"))

    def test_perfis_somam_cem(self):
        for perfil in PERFIS.values():
            validar_percentuais(perfil)

    def test_balanco_material(self):
        r = estimar_analise("phone", 180)
        self.assertAlmostEqual(sum(x["massa_estimada_g"] for x in r["materiais"]), 180, places=3)
        self.assertIsNone(r["percentual_recuperavel"])

    def test_m55s_nao_e_m55(self):
        r = buscar_produto_local("Samsung Galaxy M55s 5G")
        self.assertTrue(r is None or "M55s" in r["nome"])

    def test_formula_e_sem_preco(self):
        calculado = calcular_valor_material("Ouro", 0.54)
        self.assertIn("0.540000 g", calculado["formula"])
        self.assertTrue(calculado["possui_preco"])
        self.assertFalse(calcular_valor_material("Material não cadastrado", 2)["possui_preco"])

    def test_csv_com_formula_e_indeterminado(self):
        material = calcular_valor_material("Ouro", 0.54)
        csv = gerar_csv_analise(
            equipamento="Teste", quantidade=1, massa_total_g=180,
            massa_media_g=180, categoria="phone", fonte_principal="Teste",
            fontes_utilizadas=["Teste"], materiais=[{
                "material": "Ouro", "percentual_estimado": 0.3, "massa_estimada_g": 0.54
            }], materiais_economicos=[material], massa_recuperavel_g=None,
            percentual_recuperavel=None, valor_total_estimado=243,
            recomendacoes=[]
        ).decode("utf-8-sig")
        self.assertIn("formula_valor", csv)
        self.assertIn("0.540000 g", csv)
        self.assertIn("Não determinado", csv)

    def test_recuperacao_nao_inventada(self):
        resultado = estimar_analise("phone", 1800)
        self.assertIsNone(resultado["massa_recuperavel_g"])
        self.assertIsNone(resultado["percentual_recuperavel"])

    def test_exportacao_suspensa_sem_zero_falso(self):
        csv = gerar_csv_analise(
            equipamento="Teste", quantidade=10, massa_total_g=1800,
            massa_media_g=180, categoria="phone", fonte_principal="Teste",
            fontes_utilizadas=["Teste"],
            materiais=[{"material": "Ouro", "massa_estimada_g": 0.54,
                        "percentual_estimado": 0.03}],
            materiais_economicos=[], massa_recuperavel_g=None,
            percentual_recuperavel=None, valor_total_estimado=None,
            recomendacoes=[]
        ).decode("utf-8-sig")
        self.assertIn("Não calculado", csv)

    def test_perfil_percentual_negativo(self):
        with self.assertRaises(ValueError):
            validar_percentuais({"percentuais": {"Ouro": -0.1, "Outros": 1.1}})

    def test_economia_nao_promete_liquido(self):
        r = calcular_valor_economico([{"material":"Ouro","massa_estimada_g":1.0}])
        self.assertEqual(r["valor_bruto_estimado"], 450)
        self.assertIsNone(r["retorno_liquido_estimado"])
        self.assertFalse(r["custos_recuperacao_informados"])


if __name__ == "__main__":
    unittest.main()
