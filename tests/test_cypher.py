import unittest
from services.validation_service import validar_lote, extrair_massa_referencia_g
from services.catalog_service import buscar_produto_local
from services.analysis_service import estimar_analise, PERFIS, validar_percentuais
from services.economic_service import calcular_valor_economico, calcular_valor_material
from services.export_service import gerar_csv_analise


class TestCypher(unittest.TestCase):
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

    def test_economia_nao_promete_liquido(self):
        r = calcular_valor_economico([{"material":"Ouro","massa_estimada_g":1.0}])
        self.assertEqual(r["valor_bruto_estimado"], 450)
        self.assertIsNone(r["retorno_liquido_estimado"])
        self.assertFalse(r["custos_recuperacao_informados"])


if __name__ == "__main__":
    unittest.main()
