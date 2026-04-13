# 💳 VoucherPro

**Personal credit card expense tracking and reconciliation app.**  
Built as a PWA (Progressive Web App) hosted on GitHub Pages.  
Powered by Claude Vision AI · Anthropic

**Current version: v3.8 · 12 Apr 2026**

-----

## 🚀 Access

**URL:** https://fovallef.github.io/Voucher-Pro/

Install from Safari on iPhone: `Share → Add to Home Screen`

-----

## ✨ Features

### 📷 Voucher Scanning

- Take a photo or select from gallery
- Claude Vision automatically extracts: merchant, amount, date, time, card, category
- **Two-pass system**: full extraction + simplified fallback if needed
- **Image compression**: photos stored at 480px grayscale JPEG 35% (~20KB vs ~3MB original). Claude receives full-resolution for OCR, compressed version is stored
- **Circular image recycling**: images from reconciled/approved transactions older than 60 days are automatically purged on startup. Transaction data (amount, merchant, date, etc.) is never deleted
- Optional **notes field** per voucher
- Terminal badge displayed (`📟 Terminal: Getnet · *7848`)
- **Duplicate detection**: alerts before saving if a matching transaction (same merchant + amount + card within 3 days) already exists

### 📟 Supported Mexican Payment Terminals (v3.8)

|Terminal                      |Bank / Fintech  |Amount field            |
|------------------------------|----------------|------------------------|
|Getnet                        |Santander       |`Import =` / `Importe =`|
|BBVA own terminal             |BBVA            |`TOTAL A PAGAR`         |
|Mifel / Smart Payment Services|Mifel           |`TOTAL MXN`             |
|Mercado Pago Point            |Fintech         |`Total $X`              |
|EVO Payments International    |International   |`Monto $X`              |
|50CBS                         |Generic         |`Total: X MXN`          |
|Clip                          |Fintech         |`Total`                 |
|iZettle / Zettle (PayPal)     |Fintech         |`Total`                 |
|Square                        |Fintech         |`Total`                 |
|Banorte own terminal          |Banorte         |`Importe`               |
|Banamex / Citibanamex         |Banamex         |`Importe`               |
|Santander own terminal        |Santander       |`Importe`               |
|HSBC                          |HSBC            |`Importe`               |
|Inbursa                       |Inbursa         |`Importe`               |
|Sr. Pago                      |Fintech         |`Total`                 |
|American Express own          |Amex            |`Importe`               |
|Any other                     |Generic fallback|Largest number visible  |

### ➕ Manual Entry

- Register expenses without scanning a voucher
- **37 one-tap templates**: Netflix ($219/$299), Spotify, Prime Video ad-free ($99), Meli+ ($149), Apple TV+, YouTube Premium, iCloud+, Microsoft 365, Claude Pro, ChatGPT Plus, Costco membership, Amex annual fees by tier, and more
- Prices updated for Mexico 2026
- **Monthly recurring toggle** — auto-registers every month
- MSI (interest-free installments) support for Amex, BBVA, Banamex
- **Duplicate detection**: warns before saving manual entries that match existing records

### 📧 Gmail Import

- OAuth 2.0 connection with Gmail (one-time authorization)
- Searches emails from **Rappi, Uber Eats, DiDi Food, Amazon** (last 45 days)
- Claude classifies each email with strict rules:
  - 💳 **Real charge** — confirmed and billed order (must have a numeric amount)
  - 💚 **Refund** — money returned (positive income)
  - 🚫 **Scheduled order** — ignored automatically
  - 🚫 **Shipping notification / promo / marketing** — ignored automatically
- Detail screen per email: subject, order summary, order number
- Editable fields before approving: amount, card, category, merchant, notes
- Approval flow: **⏳ Pending → ✅ Approve / ❌ Reject / ↩️ Undo Approval**
- Only approved items are recorded as transactions
- **Automatic duplicate skip**: already-imported emails are never re-imported

> **For Amazon orders from Hotmail:** Set up auto-forwarding of amazon.com.mx emails to your Gmail in Hotmail Settings.

### 📋 History

- Full view of all transactions
- Filters: All / Pending / Reconciled / Disputed / Recurring / Manual
- **⚠️ Duplicate banner**: yellow warning shown at top if existing duplicate records are detected, with details on which ones to review
- Inline editing of any field
- Individual delete with confirmation
- Notes displayed with 📝

### 🔄 Reconciliation

- Upload bank statement as PDF
- Claude extracts charges and reconciles against registered vouchers
- **Rich post-analysis summary**: bank name, cut date, total due, charges identified
- Unrecognized charges with 3 actions: register, mark recurring, dispute
- **Per-card view**: pending vouchers + upcoming cut date per card
- **Statement history** with metrics per period
- Cut date auto-extracted from PDF and saved to card catalog

### 📊 Dashboard

- Pie chart by spending category (MXN)
- Bar chart by card
- Current vs previous month comparison
- USD spending tracked separately
- Monthly recurring total with annual estimate

### ⚙️ Settings

- **Anthropic API Key** — for Claude Vision scanning
- **Google Client ID** — for Gmail import
- **Card catalog**: add, rename, delete, set cut day (📅)
- **Category catalog**: add, rename, delete custom categories
- **Export CSV** — 14 columns including RFC, CFDI Folio, Recurring, Manual flags
- **Import CSV** — restore from backup, auto-detects and skips duplicates
- Storage indicator: shows vouchers with images vs. data-only (purged)
- Delete all records (double confirmation required)

-----

## 👤 Profiles

### Personal

5 cards: American Express, BBVA, Santander, Banamex, Morgan Stanley  
14 categories including Interest Charges and Annual Fees  
MSI available on Amex, BBVA, Banamex  
Multi-currency: MXN, USD, EUR, GBP, CAD

### 🏢 Business

Card: Clara  
11 categories  
CFDI fields: Supplier RFC + Folio/UUID  
📲 WhatsApp button to request invoice

-----

## 💾 Storage Architecture

|Scenario              |Size per voucher|Capacity (5MB localStorage)|
|----------------------|----------------|---------------------------|
|Original iPhone photo |~3MB            |~1–2 vouchers              |
|**Compressed (v3.6+)**|**~20KB**       |**~250 vouchers**          |

**Circular recycling strategy:**

- Images are automatically purged from reconciled/approved transactions older than 60 days
- Transaction metadata (amount, merchant, date, category, card) is **never deleted**
- At ~30 vouchers/month: ~7 months of images before any purging needed
- With auto-purge enabled: effectively unlimited capacity

-----

## 🛠️ Tech Stack

|Component |Technology                                   |
|----------|---------------------------------------------|
|Frontend  |HTML5 + CSS3 + Vanilla JavaScript            |
|AI        |Claude Vision API (Anthropic) — claude-sonnet|
|Charts    |Chart.js 4.4.0                               |
|Gmail Auth|Google Identity Services (OAuth 2.0)         |
|Storage   |Device localStorage                          |
|Hosting   |GitHub Pages                                 |
|Format    |Installable PWA (no App Store needed)        |

**Architecture:** Single-file PWA split into 2 `<script>` blocks for Safari iOS compatibility (~80KB limit per block). Both scripts minified with jsmin before each release.

-----

## 📁 Repository Files

|File        |Description                             |
|------------|----------------------------------------|
|`index.html`|Full app (core + Gmail module, minified)|
|`README.md` |This document                           |

-----

## 🔐 Initial Setup

### 1. Anthropic API Key

1. Get your key at [console.anthropic.com](https://console.anthropic.com)
1. In the app: ⚙️ Settings → API Key → Save

### 2. Google Client ID (for Gmail Import)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
1. Create project → enable **Gmail API**
1. Credentials → OAuth 2.0 → Web Application
1. Authorized origin: `https://fovallef.github.io`
1. In the app: ⚙️ Settings → Google Client ID → Save
1. In Google Cloud → Audience → Test users → add your Gmail address

### 3. Card Cut Dates

- ⚙️ Settings → tap 📅 next to each card to set manually
- Or upload a PDF bank statement — cut date is extracted and saved automatically

-----

## 🔄 Release Process

For every code update:

1. Apply changes
1. Audit (49 critical functions + 28 state variables + routing + bug checks)
1. Minify both script blocks with jsmin (required for Safari iOS)
1. Validate syntax with Node.js `--check` on each script
1. Upload `index.html` to GitHub
1. Wait 1–2 min → close app completely → reopen from home screen icon

-----

## 📅 Version History

|Version|Date    |Main Changes                                                            |
|-------|--------|------------------------------------------------------------------------|
|v1.0   |Mar 2026|MVP: basic scanning, history, CSV export                                |
|v2.0   |Mar 2026|Business profile, CFDI, multi-currency, MSI                             |
|v2.4   |Apr 2026|Dashboard, PDF reconciliation, recurring templates                      |
|v2.7   |Apr 2026|Gmail OAuth integration (first version)                                 |
|v2.8   |Apr 2026|Improved scanning for Getnet and Mexican terminals                      |
|v3.0   |Apr 2026|Split into 2 scripts (Safari iOS fix)                                   |
|v3.2   |Apr 2026|Statement history, rich post-analysis summary                           |
|v3.3   |Apr 2026|Card cut dates, per-card reconcile view, CSV import                     |
|v3.4   |Apr 2026|Gmail detail screen with approve/reject, notes field, mCard bugfix      |
|v3.5   |Apr 2026|Improved voucher scan prompt (Mifel, BBVA own terminal, EVO Payments)   |
|v3.6   |Apr 2026|Image compression (~20KB/voucher), circular purge, Mercado Pago terminal|
|v3.7   |Apr 2026|Comprehensive terminal coverage (17 terminals), improved card mapping   |
|v3.8   |Apr 2026|Duplicate detection on scan/manual/Gmail, history dupe banner           |

-----

## ⚠️ Important Notes

- **Local data**: Everything lives in the iPhone’s `localStorage`. Not synced to the cloud.
- **Backup**: Export CSV regularly from ⚙️ Settings and save to OneDrive.
- **Updating the app**: Never remove the home screen icon — just update `index.html` on GitHub and reopen.
- **Gmail in Testing mode**: The app is in “Testing” state on Google Cloud — only works with emails added as test users in Google Cloud Console.
- **Amazon from Hotmail**: Set up auto-forwarding in Hotmail → Gmail so orders appear in the import.
- **Duplicate detection window**: 3 days — transactions with same merchant + amount + card within 3 days trigger a warning. Recurring transactions are excluded from this check.

-----

*Built with Claude (Anthropic) · Francisco Ovalle Félix · ONESEC · 2026*
