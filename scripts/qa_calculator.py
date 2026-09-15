#!/usr/bin/env python3
"""Reference QA checks for the investment calculator projection logic.

Keeps the calculator's core business rules independently testable in GitHub Actions:
- monthly contributions
- annual 5% contribution escalation
- effective annual return converted to monthly compounding
- TFSA annual and lifetime contribution limits
"""
from math import isclose


def project(max_years, annual_rate, start=6000.0, annual_increase=5.0,
            annual_tfsa=46000.0, lifetime_tfsa=500000.0):
    balance = capital = tfsa_capital = non_tfsa_capital = lifetime_used = 0.0
    monthly_rate = (1 + annual_rate / 100.0) ** (1 / 12.0) - 1
    growth = annual_increase / 100.0
    rows = []

    for year in range(1, max_years + 1):
        monthly = start * ((1 + growth) ** (year - 1))
        year_tfsa = 0.0
        for _ in range(12):
            annual_left = max(0.0, annual_tfsa - year_tfsa)
            lifetime_left = max(0.0, lifetime_tfsa - lifetime_used)
            to_tfsa = min(monthly, annual_left, lifetime_left)
            to_non = monthly - to_tfsa

            year_tfsa += to_tfsa
            lifetime_used += to_tfsa
            tfsa_capital += to_tfsa
            non_tfsa_capital += to_non
            capital += monthly
            balance = balance * (1 + monthly_rate) + monthly

        rows.append({
            "year": year,
            "capital": capital,
            "profit": balance - capital,
            "balance": balance,
            "tfsaCapital": tfsa_capital,
            "nonCapital": non_tfsa_capital,
            "lifetimeUsed": lifetime_used,
        })
    return rows


def assert_close(actual, expected, tol=0.02):
    if not isclose(actual, expected, abs_tol=tol):
        raise AssertionError(f"Expected {expected:.2f}, got {actual:.2f}")


def main():
    # Canonical user case: R6,000/month, +5% p.a., R46k annual TFSA,
    # R500k lifetime TFSA, and 8/10/12% comparison returns.
    expected = {
        8: {
            5: (397845.45, 82218.24, 480063.69, 230000.00),
            10: (905608.26, 412459.23, 1318067.49, 460000.00),
            12: (1146033.11, 650200.43, 1796233.54, 500000.00),
            20: (2380748.70, 2611853.22, 4992601.91, 500000.00),
        },
        10: {
            5: (397845.45, 105123.02, 502968.47, 230000.00),
            10: (905608.26, 546356.89, 1451965.15, 460000.00),
            12: (1146033.11, 874355.77, 2020388.87, 500000.00),
            20: (2380748.70, 3750373.19, 6131121.89, 500000.00),
        },
        12: {
            5: (397845.45, 129036.69, 526882.14, 230000.00),
            10: (905608.26, 695388.06, 1600996.32, 460000.00),
            12: (1146033.11, 1130466.23, 2276499.34, 500000.00),
            20: (2380748.70, 5199557.15, 7580305.85, 500000.00),
        },
    }

    for rate, milestones in expected.items():
        rows = project(20, rate)
        for year, values in milestones.items():
            row = rows[year - 1]
            for key, exp in zip(("capital", "profit", "balance", "lifetimeUsed"), values):
                assert_close(row[key], exp)

    # Annual TFSA cap must never be exceeded in a contribution year.
    rows = project(3, 0, start=10000, annual_increase=0)
    assert_close(rows[0]["tfsaCapital"], 46000.00)
    assert_close(rows[1]["tfsaCapital"], 92000.00)
    assert_close(rows[2]["tfsaCapital"], 138000.00)

    # Lifetime cap must stop at exactly R500,000 and never rise again.
    rows = project(20, 0, start=50000, annual_increase=0)
    if rows[-1]["lifetimeUsed"] != 500000.0:
        raise AssertionError("TFSA lifetime contribution cap was not enforced")
    if max(r["lifetimeUsed"] for r in rows) > 500000.0:
        raise AssertionError("TFSA lifetime contribution cap was exceeded")

    print("Calculator QA passed: contribution growth, compounding, annual TFSA cap and lifetime TFSA cap.")


if __name__ == "__main__":
    main()
