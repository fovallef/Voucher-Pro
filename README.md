# 💳 VoucherPro

A personal expense tracking app for scanning and reconciling credit card vouchers, powered by Claude Vision AI by Anthropic.

## Features

- 📷 **Scan vouchers** using your iPhone camera — automatically extracts card, merchant, amount, date, time and category
- 🔄 **Reconcile** monthly PDF statements against your registered vouchers
- 📊 **Dashboard** with spending breakdown by category and card
- 🔍 **Detect** recurring charges, direct debits and potential duplicate transactions
- 📅 **Track** installment purchases (MSI — Meses Sin Intereses)
- 📲 **Send vouchers** directly to your invoicing service via WhatsApp
- 📥 **Export** all data to CSV compatible with Excel and OneDrive

## Profiles

|Profile   |Cards                                                             |
|----------|------------------------------------------------------------------|
|👤 Personal|American Express · BBVA · Santander · Banamex · Morgan Stanley    |
|🏢 Business|Clara (with RFC and CFDI Folio capture for Mexican tax compliance)|

## Tech Stack

- Vanilla HTML / CSS / JavaScript — no frameworks
- [Claude Vision API](https://anthropic.com) for intelligent data extraction
- Local storage on device (localStorage)
- PWA — installable on iPhone directly from Safari

## Installation on iPhone

1. Open this URL in **Safari**
1. Tap share ↑ → **“Add to Home Screen”**
1. Enter your Anthropic API Key on the welcome screen
1. Done!

## Notes

This is a personal project for private use.
Multi-currency support: MXN · USD · EUR · GBP · CAD
