"""tools/clt_pj.py: a conta CLT × PJ com as tabelas de 2026, conferida à mão."""

import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import clt_pj  # noqa: E402


class Tables(unittest.TestCase):
    def test_inss_is_progressive_and_capped(self):
        self.assertEqual(clt_pj.inss(1621.00), 121.58)
        self.assertEqual(clt_pj.inss(8475.55), 988.09)  # a contribuição máxima de 2026
        self.assertEqual(clt_pj.inss(20000), 988.09)

    def test_irrf_with_the_lei_15270_reduction(self):
        self.assertEqual(clt_pj.irrf(5000, clt_pj.inss(5000)), 0.0)        # isento até R$ 5 mil
        self.assertEqual(clt_pj.irrf(6000, clt_pj.inss(6000)), 385.10)     # 564,85 - (978,62 - 0,133145 × 6000)
        self.assertEqual(clt_pj.irrf(8000, clt_pj.inss(8000)), 1037.85)    # acima de R$ 7.350, sem redução
        self.assertEqual(clt_pj.irrf(13500, clt_pj.inss(13500)), 2532.05)

    def test_simplified_discount_wins_when_inss_is_small(self):
        # INSS de 11% sobre R$ 5.133,34 é R$ 564,67, menos que o desconto simplificado de R$ 607,20.
        self.assertEqual(clt_pj.irrf(5133.34, 564.67), 47.75)
        self.assertLess(clt_pj.irrf(8000, 921.51, dependents=2), clt_pj.irrf(8000, 921.51))

    def test_plr_has_its_own_table(self):
        self.assertEqual(clt_pj.plr_tax(8214.40), 0.0)
        self.assertEqual(clt_pj.plr_tax(10000), 139.75)

    def test_simples_effective_rate(self):
        self.assertAlmostEqual(clt_pj.simples_rate(180000, "III"), 0.06)
        self.assertAlmostEqual(clt_pj.simples_rate(220000, "III"), 15280 / 220000)
        self.assertAlmostEqual(clt_pj.simples_rate(180000, "V"), 0.155)
        with self.assertRaises(ValueError):
            clt_pj.simples_rate(5_000_000, "III")


class Sides(unittest.TestCase):
    def test_clt_year(self):
        c = clt_pj.clt(13500, vr=900, health=600)
        self.assertEqual(c["liquido_mensal"], 9979.86)
        self.assertEqual(c["fgts_anual"], 14400.00)          # 8% de 13,33 salários
        self.assertEqual(c["beneficios_anuais"], 18000.00)
        self.assertEqual(c["total_anual"], round(c["dinheiro_anual"] + 14400 + 18000, 2))

    def test_pj_keeps_the_fator_r_by_default(self):
        p = clt_pj.pj(20000)
        self.assertEqual((p["anexo"], p["faturamento_anual"], p["das_anual"]), ("III", 220000.00, 15280.00))
        self.assertGreaterEqual(p["fator_r"], 0.28)
        low = clt_pj.pj(20000, pro_labore=2000)
        self.assertEqual(low["anexo"], "V")
        self.assertGreater(low["das_anual"], p["das_anual"])

    def test_pj_alerts(self):
        self.assertTrue(clt_pj.pj(1000, accountant=900)["alertas"])
        self.assertIn("retenção de 10%", clt_pj.pj(100000, months=12)["alertas"][0])
        self.assertEqual(clt_pj.pj(20000)["alertas"], [])


class Compare(unittest.TestCase):
    def test_equivalents_meet_in_the_middle(self):
        r = clt_pj.compare(13500, None, {"vr": 900, "health": 600}, {"months": 11})
        pj = clt_pj.pj(r["pj_equivalente"], months=11)
        self.assertAlmostEqual(pj["total_anual"], r["clt"]["total_anual"], delta=15)
        back = clt_pj.compare(None, r["pj_equivalente"], {"vr": 900, "health": 600}, {"months": 11})
        self.assertAlmostEqual(back["clt_equivalente"], 13500, delta=2)

    def test_pj_terms_shape_the_equivalent(self):
        eleven = clt_pj.compare(13500, None, {}, {"months": 11})["pj_equivalente"]
        twelve = clt_pj.compare(13500, None, {}, {"months": 12})["pj_equivalente"]
        self.assertGreater(eleven, twelve)

    def test_both_sides_give_the_gap(self):
        r = clt_pj.compare(13500, 20000)
        self.assertEqual(r["diferenca_anual"], round(r["pj"]["total_anual"] - r["clt"]["total_anual"], 2))
        with self.assertRaises(ValueError):
            clt_pj.compare()


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = clt_pj.main(list(args))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_report_in_portuguese(self):
        code, out, _ = self.run_cli("--clt", "13500", "--pj", "20000")
        self.assertEqual(code, 0)
        self.assertIn("R$ 13.500,00", out)
        self.assertIn("alíquota efetiva 6,95%", out)
        self.assertIn("Confirme com um contador", out)

    def test_json_and_bad_values(self):
        code, out, _ = self.run_cli("--pj", "20000", "--json")
        self.assertEqual((code, json.loads(out)["pj"]["anexo"]), (0, "III"))
        self.assertEqual(self.run_cli("--clt", "-1")[0], 2)
        self.assertEqual(self.run_cli("--pj", "20000", "--meses", "14")[0], 2)
        self.assertEqual(self.run_cli("--pj", "500000")[0], 2)  # acima do limite do Simples


if __name__ == "__main__":
    unittest.main()
