# 💳 VoucherPro

> **v4.4 · May 2026**  
> A personal and business expense tracking PWA powered by Claude AI — scan vouchers, reconcile statements, and import transactions from Gmail. No backend. No install. Runs entirely in your browser.

[![Live App](https://img.shields.io/badge/Live%20App-fovallef.github.io%2FVoucher--Pro-6366f1?style=for-the-badge)](https://fovallef.github.io/Voucher-Pro/)
![Platform](https://img.shields.io/badge/Platform-iOS%20Safari%20%7C%20PWA-black?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Claude%20by%20Anthropic-orange?style=for-the-badge)

-----

## What It Does

VoucherPro helps you track every peso (and dollar) you spend — by scanning physical vouchers with your camera, importing transactions from Gmail, manually logging expenses, and reconciling everything against your bank statements automatically with AI.

Designed for **Mexico-based users** with personal and business credit cards.

-----

## Features

### 📷 Voucher Scanning

- Point your camera at any payment voucher — Claude reads it automatically
- Supports all major Mexican POS terminals: **Getnet, Clip, iZettle, Square**
- Smart merchant detection: distinguishes the business name from the terminal brand
- Auto-maps `TECH/MasterCard` → Clara corporate card
- Two-pass extraction: primary structured prompt + fallback for difficult images
- Detects refunds/chargebacks and marks them as positive income
- Shows terminal name and last 4 card digits in the review screen

### 📧 Gmail Import

- Connects via Google OAuth — read-only, one-time authorization
- Searches the last 45 days for delivery and shopping emails
- Supported services: **Rappi, Uber Eats, DiDi Food, Amazon, Zettle, Stripe-billed services (Eleven Labs, etc.), 1Password**
- **Smart pre-classification by subject** — skips Claude for obvious cases (saves tokens)
- **Regex amount extraction** — extracts price before sending to Claude when possible
- **Smart classification by Claude:**
  - 💳 Real charges → imported
  - 💚 Refunds → imported as positive income
  - 🚫 Scheduled/programmed orders → ignored (not charged yet)
  - 🚫 Cancellations and marketing → ignored
- Select/deselect individual transactions before confirming import
- Amazon: only processes confirmed receipts — shipping/tracking emails are excluded
- Amazon orders from Hotmail: set up a forward rule to Gmail and they appear automatically

### ➕ Manual Expenses

- 37 one-tap templates with current Mexico 2026 prices
- Streaming: Netflix ($219/$299), Disney+, Max, Prime Video, Apple TV+, YouTube Premium
- Music: Spotify Individual/Duo/Family
- Shopping memberships: Amazon Prime, **Meli+**, Costco
- Tech: Apple One, iCloud+, Microsoft 365, Claude Pro, ChatGPT Plus, Google One
- Card fees: Amex Platinum/Gold/Green annual fees, BBVA, Banamex
- Business: Google Workspace, AWS, Azure, Microsoft 365 Business, Slack, Zoom
- Toggle auto-monthly recurrence on any expense
- MSI (months without interest) support for Amex, BBVA, and Banamex

### 🔄 Monthly Reconciliation

- Upload a PDF bank statement — Claude extracts all charges and matches them against your logged vouchers
- Supported banks: **BBVA, Banamex/Citibanamex, Santander, American Express MX, Morgan Stanley, Clara**
- Also supports the universal CONDUSEF format (Oct 2024+)
- Post-analysis summary card showing: cut date, bank, charges identified, total amount due
- Unrecognized charges: register as new expense, mark as subscription, or dispute
- Statement history log with metrics per upload (charges / reconciled / unrecognized)
- Auto-extracts cut day from statement and stores it per card

### 📊 Dashboard

- Spending by category (pie chart, MXN)
- Spending by card (bar chart)
- Month-over-month comparison
- USD expenses tracked separately
- Monthly recurring total with annual estimate

### 👤 / 🏢 Personal & Business Profiles

**Personal cards:** American Express, BBVA, Santander, Banamex, Morgan Stanley  
**Business cards:** Clara  
**Personal categories (15):** Restaurants, Supermarket, Gas, Health/Pharmacy, Entertainment, Travel, Clothing, Education, Home Services, Home/Hardware, Subscriptions, Auto, Fees/Annual, **Interest & Finance Charges**, Other  
**Business categories (12):** Per Diem/Food, Transport, Lodging, Suppliers, Advertising, Technology, Office Supplies, Training, Client Entertainment, Bank Fees, **Interest & Finance Charges**, Other

### 💾 Data & Export

- All data stored in browser localStorage — private, no servers
- Export to CSV (14 columns including Recurring, Manual, RFC, CFDI Folio)
- Import from CSV with automatic duplicate detection
- CFDI fields (RFC + Folio) for business expenses → WhatsApp invoice request button

-----

## Tech Stack

|Layer       |Technology                              |
|------------|----------------------------------------|
|Frontend    |Vanilla HTML/CSS/JS — no frameworks     |
|AI Vision   |Claude API (claude-sonnet) via Anthropic|
|Charts      |Chart.js 4.4                            |
|Gmail       |Google OAuth 2.0 + Gmail API            |
|Storage     |Browser localStorage                    |
|Hosting     |GitHub Pages                            |
|Distribution|PWA — installable to iOS home screen    |

-----

## Setup

### 1. Anthropic API Key

Go to ⚙️ **Config → API Key** and enter your Claude API key from [console.anthropic.com](https://console.anthropic.com).

- **Test your key** with the "🧪 Probar clave" button — confirms it's valid and has credit
- **Token counter** shows approximate tokens used in the current session
- **Low credit banner** appears automatically if your Anthropic balance runs out

### 2. Gmail Integration (optional)

To import transactions from Gmail:

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
1. Create a project → Enable **Gmail API**
1. Create an **OAuth 2.0 credential** (Web Application type)
1. Add authorized JavaScript origin: `https://fovallef.github.io`
1. Copy the Client ID → paste it in ⚙️ **Config → Gmail Integration**
1. Add your Gmail address as a test user in the OAuth consent screen

### 3. Amazon from Hotmail (optional)

In your Hotmail account, create a rule to forward all emails from `amazon.com.mx` and `amazon.com` to your Gmail. They will then appear in the Gmail import tab automatically.

### 4. Install as PWA on iPhone

1. Open `https://fovallef.github.io/Voucher-Pro/` in Safari
1. Tap the share button → **“Add to Home Screen”**
1. Launch from your home screen icon — runs in full-screen app mode

-----

## Update Protocol

> ⚠️ **Do not uninstall or re-anchor the app. Only update `index.html` on GitHub → wait 2 min → close app from multitasking → reopen from icon. Data is preserved.**

VoucherPro uses a two-file architecture:

- `index.html` — shell with CSS, loader, and embedded app code
- `app.js` — full application logic (source file)

-----

## Architecture Notes

- **No backend** — the app calls the Anthropic API directly from the browser using your personal API key
- **Two-pass voucher scanning** — structured extraction first, simple fallback if needed
- **Script loading** — uses `<script type="text/plain">` loader technique for Safari iOS compatibility
- **localStorage** — all transaction data, categories, card configs, and statement history persist across sessions
- Data is scoped to the browser/device where the PWA is installed

-----

## Changelog

### v4.4 (May 2026)

**API & Config:**
- API key test button — validates key and credit balance on demand
- Session token counter in Config screen
- Low-credit warning banner with direct link to Anthropic billing
- PDF reconciliation fix: added required `anthropic-beta: pdfs-2024-09-25` header (Amex and other PDFs now work)

**History:**
- Edit button on every transaction — tap to open full edit modal
- Editable fields: merchant, amount, currency, date, time, card, category, notes, MSI, RFC/CFDI folio
- "✏ editado" badge shown on modified records with timestamp

**Gmail import:**
- Added Stripe-billed services (Eleven Labs, and others)
- Added 1Password subscription receipts
- Amazon query narrowed to confirmed receipts only (excludes tracking/shipping emails — saves tokens)
- Pre-classification by email subject (skips Claude for obvious cases)
- Regex amount extraction before Claude call
- HTML email body cleaning to strip promo banners
- Improved Rappi MX prompt with explicit examples

### v4.3 (Apr 2026)

- Gmail import tab with OAuth integration (Rappi, Uber Eats, DiDi Food, Amazon)
- Smart email classification: real charges vs scheduled orders vs refunds
- Statement history log in Reconcile tab
- Post-analysis summary card (cut date, bank, charge count, total due)
- Interest & Finance Charges category (personal + business)
- 37 subscription templates with current Mexico 2026 prices (Meli+, Prime Video, Spotify tiers)
- Improved voucher scanning for Getnet, Clip, iZettle terminals
- Two-pass scanning with automatic fallback
- Safari iOS compatibility fix via external script architecture

-----

## License

Private — personal use by Francisco Ovalle Félix.  
Powered by [Claude](https://claude.ai) · Built with ❤️ in México
