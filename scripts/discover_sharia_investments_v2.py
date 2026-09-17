#!/usr/bin/env python3
"""Discovery v2: run live search plus a conservative bootstrap set found in the
initial web sweep. Bootstrap entries are only DISCOVERY candidates; they still
require the same manual verification gate as live search results.
"""
import discover_sharia_investments as d

BOOTSTRAP = [
    {
        'title': 'Franklin Templeton Shariah Funds - South Africa',
        'url': 'https://www.franklintempleton.co.za/invest-with-us/legal-documents',
        'snippet': 'South African legal documents page specifically lists Franklin Templeton Shariah Funds, including current prospectus and reports.',
        'query': 'bootstrap: initial South Africa Shariah web sweep',
    },
    {
        'title': 'Other Shariah Compliant Unit Trust Funds - Al Baraka Bank',
        'url': 'https://www.albaraka.co.za/products/other-shariah-compliant-unit-trust-funds',
        'snippet': 'Al Baraka lists additional Shariah-compliant unit trust ranges including Camissa, Sentio and Oasis Shariah funds.',
        'query': 'bootstrap: initial South Africa Shariah web sweep',
    },
    {
        'title': "27four Shariah Active Equity Fund",
        'url': 'https://www.moneyweb.co.za/tools-and-data/click-a-unit-trust/27FA1/',
        'snippet': "South African unit trust listing for the 27four Shariah Active Equity Fund; Shariah-compliant equity investment product.",
        'query': 'bootstrap: initial South Africa Shariah web sweep',
    },
    {
        'title': "Wealthvest Shari'ah Equity 27four Fund",
        'url': 'https://www.moneyweb.co.za/tools-and-data/click-a-unit-trust/WSEFA/',
        'snippet': "South African equity unit trust whose objective states that investments are Shari'ah compliant.",
        'query': 'bootstrap: initial South Africa Shariah web sweep',
    },
    {
        'title': "Al Baraka SuperFund Retirement Fund",
        'url': 'https://www.albaraka.co.za/products/superfund-retirement-fund',
        'snippet': 'South African retirement product whose contributions are invested in unit trusts that pass Shariah screening and purification.',
        'query': 'bootstrap: initial South Africa Shariah web sweep',
    },
]

_original = d.search_bing_rss
_first = True

def search_with_bootstrap(query):
    global _first
    try:
        live = _original(query)
    except Exception:
        live = []
    if _first:
        _first = False
        return BOOTSTRAP + live
    return live

d.search_bing_rss = search_with_bootstrap

d.main()
