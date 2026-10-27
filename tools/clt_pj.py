#!/usr/bin/env python3
"""CLT x PJ: the same monthly number is very different money.

04-job-evaluation.md explains the rules in prose; this tool does the
arithmetic, so every comparison uses the same tables and prints its
assumptions instead of a mental estimate.

CLT (one year of employment):
  * 11 regular months and 1 vacation month paid with the 1/3 bonus, each
    net of INSS and IRRF;
  * the 13th salary, taxed on its own (exclusive withholding);
  * FGTS: 8% of salary, 13th and vacation pay with the 1/3;
  * PLR, taxed on its own annual table;
  * benefits the employer pays (meal card, health plan, others), at face value.
PJ (the person's own company in the Simples Nacional):
  * the invoice for each month worked - 11 by default: the month of rest a
    CLT vacation pays is unpaid here;
  * DAS at the effective rate for the annual revenue: Anexo III when the
    pró-labore is at least 28% of revenue (Fator R), Anexo V below. The
    employer's INSS on the pró-labore is inside the DAS in both;
  * on the pró-labore, paid all 12 months: INSS 11% up to the ceiling, and IRRF;
  * accountant and other fixed costs; benefits the contract pays.
  The rest is distributed as profit, tax-free up to R$ 50,000 a month per
  company; above it there is a 10% withholding since 2026, flagged, not modeled.

Each side ends in one annual figure: net cash plus FGTS and benefits.
`equivalent_pj` / `equivalent_clt` search the other side's monthly value
that matches it.

Tables for 2026, checked on 2026-10-27:
  * IRRF monthly table, simplified discount, dependent deduction, the Lei
    15.270/2025 reduction and the PLR table - Receita Federal:
    https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/2026
    (the reduction also applies to the 13th salary, per secondary sources;
    it only matters for salaries up to R$ 7,350);
  * INSS employee table - Portaria Interministerial MPS/MF 13/2026,
    ceiling R$ 8,475.55;
  * Simples Nacional Anexos III and V and the Fator R - LC 123/2006 as
    amended by LC 155/2016.
Update the constants below when a table changes, and TABLES_YEAR with them.
Not legal or tax advice: every result says to confirm with an accountant.

Usage:
  python3 tools/clt_pj.py --clt 13500 [--vr 900] [--saude 600] [--outros 0] [--plr 0]
  python3 tools/clt_pj.py --pj 20000 [--meses 11] [--contador 300] [--custos 0]
                                     [--beneficios-pj 0] [--pro-labore N]
  python3 tools/clt_pj.py --clt 13500 --pj 20000 ... [--dependentes 0] [--json]
With one side only, the other side's equivalent is computed.

Exit codes: 0 done; 2 usage error or a value outside the tables.
"""

import argparse
import json
import math
import sys
from decimal import ROUND_HALF_UP, Decimal

TABLES_YEAR = 2026
MIN_WAGE = 1621.00

# INSS, employee: progressive, each rate on its own slice, capped at the ceiling.
INSS_BANDS = [(1621.00, 0.075), (2902.84, 0.09), (4354.27, 0.12), (8475.55, 0.14)]
INSS_CEILING = 8475.55
PRO_LABORE_INSS = 0.11  # contribuinte individual on a pró-labore, up to the ceiling

# IRRF, monthly: (upper bound, rate, deduction).
IRRF_BANDS = [(2428.80, 0.0, 0.0), (2826.65, 0.075, 182.16), (3751.05, 0.15, 394.16),
              (4664.68, 0.225, 675.49), (math.inf, 0.275, 908.73)]
SIMPLIFIED_DISCOUNT = 607.20
DEPENDENT_DEDUCTION = 189.59
# Lei 15.270/2025: no tax up to R$ 5,000; a reduction that fades out at R$ 7,350.
REDUCTION_FREE_UP_TO = 5000.00
REDUCTION_UP_TO = 7350.00
REDUCTION_BASE, REDUCTION_SLOPE = 978.62, 0.133145

# PLR, annual and exclusive: (upper bound, rate, deduction).
PLR_BANDS = [(8214.40, 0.0, 0.0), (9922.28, 0.075, 616.08), (13167.00, 0.15, 1360.25),
             (16380.38, 0.225, 2347.78), (math.inf, 0.275, 3166.80)]

FGTS = 0.08

# Simples Nacional: (annual revenue upper bound, nominal rate, deduction).
ANEXO_III = [(180000, 0.06, 0), (360000, 0.112, 9360), (720000, 0.135, 17640),
             (1800000, 0.16, 35640), (3600000, 0.21, 125640), (4800000, 0.33, 648000)]
ANEXO_V = [(180000, 0.155, 0), (360000, 0.18, 4500), (720000, 0.195, 9900),
           (1800000, 0.205, 17100), (3600000, 0.23, 62100), (4800000, 0.305, 540000)]
FATOR_R = 0.28
DIVIDEND_MONTHLY_LIMIT = 50000.00


def _round(value: float) -> float:
    """Cents, half up, as payroll rounds (R$ 121,575 is R$ 121,58), not the float's binary half-even."""
    return float(Decimal(repr(round(value, 6))).quantize(Decimal("0.01"), ROUND_HALF_UP))


def inss(gross: float) -> float:
    """Employee INSS for one month's pay."""
    total, floor = 0.0, 0.0
    for top, rate in INSS_BANDS:
        if gross <= floor:
            break
        total += (min(gross, top) - floor) * rate
        floor = top
    return _round(total)


def irrf(income: float, inss_paid: float, dependents: int = 0) -> float:
    """Monthly IRRF on taxable income, with the better of legal deductions or the simplified discount."""
    base = income - max(inss_paid + dependents * DEPENDENT_DEDUCTION, SIMPLIFIED_DISCOUNT)
    tax = 0.0
    for top, rate, deduction in IRRF_BANDS:
        if base <= top:
            tax = max(0.0, base * rate - deduction)
            break
    if income <= REDUCTION_FREE_UP_TO:
        tax = 0.0
    elif income <= REDUCTION_UP_TO:
        tax -= min(tax, max(0.0, REDUCTION_BASE - REDUCTION_SLOPE * income))
    return _round(tax)


def plr_tax(amount: float) -> float:
    for top, rate, deduction in PLR_BANDS:
        if amount <= top:
            return _round(max(0.0, amount * rate - deduction))
    return 0.0  # unreachable: the last band is open


def simples_rate(annual_revenue: float, anexo: str) -> float:
    """Effective DAS rate for a year's revenue."""
    if annual_revenue <= 0:
        return 0.0
    for top, rate, deduction in (ANEXO_III if anexo == "III" else ANEXO_V):
        if annual_revenue <= top:
            return (annual_revenue * rate - deduction) / annual_revenue
    raise ValueError("faturamento acima do limite do Simples Nacional (R$ 4,8 milhões por ano)")


def clt(salary: float, vr: float = 0, health: float = 0, other: float = 0, plr: float = 0,
        dependents: int = 0) -> dict:
    """One year of CLT: net cash, FGTS and benefits."""
    month_inss = inss(salary)
    month_tax = irrf(salary, month_inss, dependents)
    month_net = salary - month_inss - month_tax
    vacation = salary * 4 / 3
    vacation_inss = inss(vacation)
    vacation_net = vacation - vacation_inss - irrf(vacation, vacation_inss, dependents)
    thirteenth_net = month_net  # same pay, taxed on its own: same deductions as a regular month
    plr_net = plr - plr_tax(plr)
    fgts = FGTS * salary * (13 + 1 / 3)
    benefits = 12 * (vr + health + other)
    cash = 11 * month_net + vacation_net + thirteenth_net + plr_net
    return {
        "salario": _round(salary),
        "inss_mensal": month_inss,
        "irrf_mensal": month_tax,
        "liquido_mensal": _round(month_net),
        "ferias_liquidas": _round(vacation_net),
        "decimo_terceiro_liquido": _round(thirteenth_net),
        "plr_liquida": _round(plr_net),
        "fgts_anual": _round(fgts),
        "beneficios_anuais": _round(benefits),
        "dinheiro_anual": _round(cash),
        "total_anual": _round(cash + fgts + benefits),
    }


def pj(revenue: float, months: int = 11, pro_labore: float | None = None, accountant: float = 300,
       costs: float = 0, benefits: float = 0, dependents: int = 0) -> dict:
    """One year of PJ in the Simples Nacional: net cash and benefits."""
    annual = revenue * months
    if pro_labore is None:
        # The smallest pró-labore that keeps the Fator R at 28% (Anexo III), never below the minimum wage.
        pro_labore = max(MIN_WAGE, math.ceil(FATOR_R * annual / 12 * 100) / 100)
    fator = 12 * pro_labore / annual if annual else 0.0
    anexo = "III" if fator >= FATOR_R else "V"
    rate = simples_rate(annual, anexo)
    das = annual * rate
    pl_inss = _round(min(pro_labore, INSS_CEILING) * PRO_LABORE_INSS)
    pl_tax = irrf(pro_labore, pl_inss, dependents)
    distributed = annual - das - 12 * (pro_labore + accountant + costs)
    cash = 12 * (pro_labore - pl_inss - pl_tax) + distributed
    alerts = []
    if distributed < 0:
        alerts.append("O faturamento não cobre o pró-labore e os custos: a empresa fecha o ano no prejuízo.")
    if distributed / 12 > DIVIDEND_MONTHLY_LIMIT:
        alerts.append("Lucro distribuído acima de R$ 50 mil por mês: desde 2026 há retenção de 10% na fonte, "
                      "que esta conta não inclui.")
    return {
        "faturamento_mensal": _round(revenue),
        "meses_faturados": months,
        "faturamento_anual": _round(annual),
        "anexo": anexo,
        "fator_r": round(fator, 4),
        "aliquota_efetiva": round(rate, 4),
        "das_anual": _round(das),
        "pro_labore": _round(pro_labore),
        "inss_pro_labore": pl_inss,
        "irrf_pro_labore": pl_tax,
        "custos_anuais": _round(12 * (accountant + costs)),
        "lucro_distribuido": _round(distributed),
        "beneficios_anuais": _round(12 * benefits),
        "dinheiro_anual": _round(cash),
        "total_anual": _round(cash + 12 * benefits),
        "alertas": alerts,
    }


def _search(total_of, target: float, high: float) -> float:
    """The monthly value whose annual total reaches the target (totals grow with the value)."""
    while total_of(high) < target:
        high *= 2
        if high > 1e7:
            raise ValueError("não há valor equivalente dentro dos limites das tabelas")
    low = 0.0
    for _ in range(60):
        mid = (low + high) / 2
        if total_of(mid) < target:
            low = mid
        else:
            high = mid
    return math.ceil(high * 100) / 100


def equivalent_pj(target: float, **pj_args) -> float:
    """The monthly invoice that matches a CLT annual total."""
    return _search(lambda v: pj(v, **pj_args)["total_anual"], target, max(target / 12, 1000))


def equivalent_clt(target: float, **clt_args) -> float:
    """The monthly CLT salary that matches a PJ annual total."""
    return _search(lambda v: clt(v, **clt_args)["total_anual"], target, max(target / 12, 1000))


ASSUMPTIONS = [
    f"Tabelas de {TABLES_YEAR}: INSS, IRRF (com a redução da Lei 15.270), PLR e Simples Nacional.",
    "CLT: 11 meses de salário, 1 mês de férias com 1/3 e o 13º, todos líquidos de INSS e IR; "
    "FGTS de 8% contado como seu (ele só é sacável em algumas situações); benefícios pelo valor que a empresa paga.",
    "PJ: empresa no Simples Nacional; sem 13º, férias pagas e FGTS, salvo o que o contrato prever; "
    "pró-labore pago nos 12 meses, com INSS de 11% e IR; o resto distribuído como lucro, isento.",
    "PJ: plano de saúde, VR e o que mais o CLT dá, se você quiser manter, saem do seu bolso: por isso entram "
    "como benefício só no lado CLT.",
    "Alíquotas do Simples dependem da atividade (CNAE) e o ISS do município pode mudar a conta; a reforma "
    "tributária muda regras de 2026 a 2033. Confirme com um contador antes de assinar.",
]


def compare(salary: float | None = None, revenue: float | None = None, clt_opts: dict | None = None,
            pj_opts: dict | None = None) -> dict:
    """Either side, or both: each side's year, the other side's equivalent and the gap.

    clt_opts and pj_opts (benefits, months, costs...) shape both a side and the
    equivalent searched on it, so a CLT-only question still uses the PJ terms given.
    """
    if salary is None and revenue is None:
        raise ValueError("informe o salário CLT, o valor PJ, ou os dois")
    clt_opts, pj_opts = clt_opts or {}, pj_opts or {}
    out = {"premissas": ASSUMPTIONS, "ano_das_tabelas": TABLES_YEAR}
    if salary is not None:
        out["clt"] = clt(salary, **clt_opts)
        out["pj_equivalente"] = equivalent_pj(out["clt"]["total_anual"], **pj_opts)
    if revenue is not None:
        out["pj"] = pj(revenue, **pj_opts)
        out["clt_equivalente"] = equivalent_clt(out["pj"]["total_anual"], **clt_opts)
    if salary is not None and revenue is not None:
        out["diferenca_anual"] = _round(out["pj"]["total_anual"] - out["clt"]["total_anual"])
    return out


def brl(value: float) -> str:
    text = f"{abs(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-R$ " if value < 0 else "R$ ") + text


def pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}".replace(".", ",") + "%"


def report(result: dict) -> str:
    lines = [f"# CLT × PJ (tabelas de {result['ano_das_tabelas']})", ""]
    c, p = result.get("clt"), result.get("pj")
    if c:
        lines += ["## CLT", f"- Salário bruto: {brl(c['salario'])} (INSS {brl(c['inss_mensal'])}, "
                  f"IR {brl(c['irrf_mensal'])}, líquido {brl(c['liquido_mensal'])} por mês)",
                  f"- Férias com 1/3, líquidas: {brl(c['ferias_liquidas'])}",
                  f"- 13º líquido: {brl(c['decimo_terceiro_liquido'])}",
                  f"- PLR líquida: {brl(c['plr_liquida'])}",
                  f"- FGTS no ano: {brl(c['fgts_anual'])}",
                  f"- Benefícios no ano: {brl(c['beneficios_anuais'])}",
                  f"- **Total no ano: {brl(c['total_anual'])}** (dinheiro {brl(c['dinheiro_anual'])})",
                  f"- PJ equivalente: **{brl(result['pj_equivalente'])} por mês** de nota", ""]
    if p:
        lines += ["## PJ", f"- Nota: {brl(p['faturamento_mensal'])} × {p['meses_faturados']} meses = "
                  f"{brl(p['faturamento_anual'])}",
                  f"- Simples Nacional, Anexo {p['anexo']} (Fator R {pct(p['fator_r'], 0)}): alíquota efetiva "
                  f"{pct(p['aliquota_efetiva'])}, DAS {brl(p['das_anual'])} no ano",
                  f"- Pró-labore: {brl(p['pro_labore'])} por mês (INSS {brl(p['inss_pro_labore'])}, "
                  f"IR {brl(p['irrf_pro_labore'])})",
                  f"- Contador e custos: {brl(p['custos_anuais'])} no ano",
                  f"- Lucro distribuído: {brl(p['lucro_distribuido'])} no ano",
                  f"- Benefícios do contrato: {brl(p['beneficios_anuais'])} no ano",
                  f"- **Total no ano: {brl(p['total_anual'])}**",
                  f"- CLT equivalente: **{brl(result['clt_equivalente'])} por mês** de salário bruto", ""]
        lines += [f"⚠ {a}" for a in p["alertas"]] + ([""] if p["alertas"] else [])
    if "diferenca_anual" in result:
        d = result["diferenca_anual"]
        lines += [f"## Resultado: o PJ dá {brl(abs(d))} {'a mais' if d >= 0 else 'a menos'} por ano que o CLT", ""]
    lines += ["## Premissas"] + [f"- {a}" for a in result["premissas"]]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compara uma proposta CLT com uma PJ; veja o docstring.")
    ap.add_argument("--clt", type=float, help="salário bruto mensal CLT")
    ap.add_argument("--vr", type=float, default=0, help="VR/VA por mês, pago pela empresa")
    ap.add_argument("--saude", type=float, default=0, help="plano de saúde por mês, pago pela empresa")
    ap.add_argument("--outros", type=float, default=0, help="outros benefícios CLT por mês")
    ap.add_argument("--plr", type=float, default=0, help="PLR ou bônus por ano")
    ap.add_argument("--pj", type=float, help="valor mensal da nota PJ")
    ap.add_argument("--meses", type=int, default=11, help="meses faturados no ano (padrão 11: um mês de descanso sem receber)")
    ap.add_argument("--contador", type=float, default=300, help="contador por mês (padrão R$ 300, uma suposição)")
    ap.add_argument("--custos", type=float, default=0, help="outros custos fixos da empresa por mês")
    ap.add_argument("--beneficios-pj", type=float, default=0, help="benefícios que o contrato PJ paga por mês")
    ap.add_argument("--pro-labore", type=float, default=None, help="pró-labore mensal (padrão: o menor que mantém o Anexo III)")
    ap.add_argument("--dependentes", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    values = [args.clt, args.pj, args.vr, args.saude, args.outros, args.plr, args.contador, args.custos,
              args.beneficios_pj, args.pro_labore]
    if any(v is not None and (v < 0 or not math.isfinite(v)) for v in values) or args.dependentes < 0 \
            or not 1 <= args.meses <= 13 or (args.clt is not None and args.clt <= 0) or (args.pj is not None and args.pj <= 0):
        ap.error("valores precisam ser positivos, e --meses de 1 a 13")
    clt_opts = {"vr": args.vr, "health": args.saude, "other": args.outros, "plr": args.plr,
                "dependents": args.dependentes}
    pj_opts = {"months": args.meses, "pro_labore": args.pro_labore, "accountant": args.contador,
               "costs": args.custos, "benefits": args.beneficios_pj, "dependents": args.dependentes}
    try:
        result = compare(args.clt, args.pj, clt_opts, pj_opts)
    except ValueError as exc:
        print(f"clt_pj: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
