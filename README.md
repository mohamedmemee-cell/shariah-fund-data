# Shariah Fund Data Feed

A small public data feed for a personal Shariah investment calculator.

## What it does

- Stores selected South African Shariah-compliant funds in one standard JSON format.
- Publishes `docs/shariah-funds.json` through GitHub Pages.
- Runs a scheduled GitHub Action every Sunday.
- Automatically updates sources only where a conservative parser is configured.
- Falls back to the last manual values if an official website/PDF changes.
- Saves dated snapshots in `data/history/`.

## Important

This is a research/planning feed, not financial advice. Past performance does not guarantee future performance. Always verify figures against the official manager fact sheet before investing.

## First-time setup

1. Create a **public** GitHub repository named `shariah-fund-data`.
2. Upload all files from this project ZIP to the root of the repository.
3. Open **Settings → Actions → General**. Under **Workflow permissions**, select **Read and write permissions** and save.
4. Open **Settings → Pages**. Under **Build and deployment → Source**, select **GitHub Actions**.
5. Open the **Actions** tab, choose **Update and publish Shariah fund data**, then **Run workflow**.
6. When the run is green, go to **Settings → Pages** and click **Visit site**.
7. The feed URL will normally be:
   `https://YOUR-GITHUB-USERNAME.github.io/shariah-fund-data/shariah-funds.json`
8. Put that URL into the calculator's **Optional JSON feed URL** and click **Refresh fund data**.

## Manual values

Edit `data/manual_values.json` in GitHub if a fund is not yet automatically collected. Do not edit `docs/shariah-funds.json` directly because the workflow rebuilds it.

## Adding a fund

Add the fund to `sources/funds.json`, then add a matching entry in `data/manual_values.json`.

## Automatic adapters

Version 1 includes a conservative Camissa consolidated-performance PDF adapter. Other managers are configured as manual/fallback while their official publishing formats are validated. This is intentional: a failed scraper must never silently replace good values with bad values.
