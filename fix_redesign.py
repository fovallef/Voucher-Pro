#!/usr/bin/env python3
"""
fix_redesign.py — VoucherPro Glass Design System (Sofía)
Sprints 1-3: CSS foundation + Nav SVG icons + Glass cards + Typography
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── SPRINT 1: CSS FOUNDATION ─────────────────────────────────────────────────
OLD_STYLE_START = '<style>\n:root{'
OLD_STYLE_END = '</style>'

style_start = content.find(OLD_STYLE_START)
style_end = content.find(OLD_STYLE_END, style_start) + len(OLD_STYLE_END)

NEW_CSS = '''<style>
:root{
--bg:#09090f;--bg2:#111118;--bg3:#1a1a24;--bd:rgba(255,255,255,.07);--glass:rgba(255,255,255,.04);
--tx:#f0f0f8;--tx2:#8a8ab0;--tx3:#44446a;
--in:#6366f1;--in2:#818cf8;--em:#10b981;--am:#f59e0b;--rd:#f43f5e;--vi:#a78bfa;--wa:#25D366;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display',sans-serif;background:var(--bg);color:var(--tx);height:100dvh;overflow:hidden;max-width:430px;margin:0 auto;position:relative}
#root{display:flex;flex-direction:column;height:100dvh}
.hdr{background:rgba(9,9,15,.88);border-bottom:1px solid rgba(255,255,255,.06);padding:52px 18px 14px;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;-webkit-backdrop-filter:blur(24px);backdrop-filter:blur(24px)}
.cnt{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;position:relative}
.pad{padding:16px;padding-bottom:36px}
.bnav{background:rgba(9,9,15,.92);border-top:1px solid rgba(255,255,255,.06);display:flex;justify-content:space-around;padding:10px 4px 30px;flex-shrink:0;-webkit-backdrop-filter:blur(24px);backdrop-filter:blur(24px)}
.ntit{font-size:20px;font-weight:700;letter-spacing:-.6px;color:var(--tx)}
.etog{display:flex;background:rgba(255,255,255,.07);border-radius:22px;padding:3px;gap:2px}
.ebtn{padding:5px 12px;border-radius:20px;font-size:11px;font-weight:600;border:none;cursor:pointer;background:transparent;color:var(--tx2);transition:all .2s;white-space:nowrap}
.ebtn.ap{background:var(--in);color:#fff;box-shadow:0 2px 12px rgba(99,102,241,.35)}
.ebtn.ae{background:var(--em);color:#fff;box-shadow:0 2px 12px rgba(16,185,129,.35)}
.nbtn{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 10px 4px;border-radius:14px;border:none;background:transparent;color:var(--tx3);cursor:pointer;font-size:10px;font-weight:500;letter-spacing:.01em;transition:color .22s,background .22s;min-width:44px}
.nbtn .ni{width:26px;height:26px;display:flex;align-items:center;justify-content:center;transition:transform .22s cubic-bezier(.34,1.56,.64,1)}
.nbtn.ap{color:var(--in);background:rgba(99,102,241,.12)}
.nbtn.ae{color:var(--em);background:rgba(16,185,129,.12)}
.nbtn.ap .ni,.nbtn.ae .ni{transform:scale(1.1)}
.card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:20px;padding:18px;margin-bottom:14px}
.btn{width:100%;padding:14px;border-radius:14px;border:none;font-size:14px;font-weight:700;cursor:pointer;transition:all .15s;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:6px;letter-spacing:-.01em}
.btn:last-child{margin-bottom:0}
.btn:active{transform:scale(.97);opacity:.88}
.btn:disabled{opacity:.35;cursor:not-allowed}
.bp{background:var(--in);color:#fff;box-shadow:0 4px 18px rgba(99,102,241,.28)}
.be{background:var(--em);color:#fff;box-shadow:0 4px 18px rgba(16,185,129,.28)}
.bs{background:rgba(255,255,255,.07);color:var(--tx2);font-size:13px;font-weight:600;border:1px solid rgba(255,255,255,.06)}
.bv{background:var(--vi);color:#fff;box-shadow:0 4px 18px rgba(167,139,250,.28)}
.bw{background:var(--wa);color:#fff}
.br{background:var(--rd);color:#fff;box-shadow:0 4px 18px rgba(244,63,94,.28)}
.fld{margin-bottom:12px}
.fld label{display:block;font-size:10px;font-weight:700;color:var(--tx3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.7px}
.inp{width:100%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:13px;padding:12px 14px;color:var(--tx);font-size:14px;outline:none;-webkit-appearance:none;font-family:inherit;transition:border-color .2s,background .2s}
.inp:focus{border-color:var(--in);background:rgba(99,102,241,.06)}
.frow{display:flex;gap:8px}
.frow .fld{flex:1}
.frow .fn{flex:0 0 90px}
.txr{display:flex;align-items:flex-start;gap:12px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:13px;margin-bottom:8px;transition:opacity .15s}
.txr.rc{background:rgba(16,185,129,.05);border-color:rgba(16,185,129,.2)}
.txr.ur{background:rgba(244,63,94,.05);border-color:rgba(244,63,94,.2)}
.txr.mn{background:rgba(167,139,250,.05);border-color:rgba(167,139,250,.2)}
.txr.dp{background:rgba(244,63,94,.07);border-color:rgba(244,63,94,.3)}
.txi{width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.txin{flex:1;min-width:0}
.txn{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--tx)}
.txs{font-size:11px;color:var(--tx2);margin-top:1px}
.txm{font-size:11px;color:var(--in2);margin-top:2px}
.txa{text-align:right;flex-shrink:0}
.txa .am{font-size:16px;font-weight:800;line-height:1.1;letter-spacing:-.02em}
.txa .cu{font-size:10px;color:var(--tx3)}
.stit{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.9px;margin-bottom:10px}
.sgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.sbox{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:14px}
.sv{font-size:21px;font-weight:700;margin-top:2px;letter-spacing:-.03em}
.sl{font-size:11px;color:var(--tx2)}
.empty{text-align:center;padding:60px 16px;color:var(--tx3)}
.empty .ei{font-size:52px;margin-bottom:12px;opacity:.6}
.lovo{position:fixed;inset:0;background:rgba(9,9,15,.88);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:200;-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}
.spin{width:36px;height:36px;border:2.5px solid rgba(255,255,255,.1);border-top-color:var(--in);border-radius:50%;animation:sp .8s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.ebr{background:rgba(244,63,94,.08);border:1px solid rgba(244,63,94,.2);border-radius:14px;padding:13px;margin:12px 16px 0;display:flex;align-items:flex-start;gap:8px}
.msib{height:3px;background:rgba(255,255,255,.08);border-radius:2px;margin:6px 0 2px}
.msif{height:3px;background:var(--in);border-radius:2px}
.fpills{display:flex;gap:6px;overflow-x:auto;margin-bottom:12px;padding-bottom:2px;scrollbar-width:none}
.fpills::-webkit-scrollbar{display:none}
.fp{padding:6px 14px;border-radius:22px;font-size:11px;font-weight:600;border:none;cursor:pointer;white-space:nowrap;background:rgba(255,255,255,.07);color:var(--tx2);flex-shrink:0;transition:all .18s}
.fp.fa{background:var(--in);color:#fff;box-shadow:0 2px 10px rgba(99,102,241,.3)}
.vprev{width:100%;max-height:130px;object-fit:contain;border-radius:14px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);margin-bottom:12px}
.bbk{font-size:13px;color:var(--tx2);background:none;border:none;cursor:pointer;padding:0;margin-bottom:12px;display:inline-flex;align-items:center;gap:4px;transition:color .15s}
.bbk:active{color:var(--in)}
.mono{font-family:'SF Mono','Courier New',monospace;font-size:12px}
.ic{border-radius:16px;padding:15px;margin-bottom:10px}
.ir{background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.2)}
.id{background:rgba(244,63,94,.07);border:1px solid rgba(244,63,94,.2)}
.iok{background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.2)}
.hidden{display:none!important}
.row-edit{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.row-edit:last-child{border-bottom:none}
.row-actions{display:flex;gap:6px;flex-shrink:0}
.rib{background:none;border:none;cursor:pointer;font-size:14px;padding:2px 4px}
.tmpl-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
.tmpl{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:12px;cursor:pointer;text-align:center;transition:all .18s}
.tmpl:active{transform:scale(.95);opacity:.85}
.tmpl .ti{font-size:24px;margin-bottom:4px}
.tmpl .tn{font-size:11px;font-weight:600;color:var(--tx)}
.tmpl .tp{font-size:10px;color:var(--tx2);margin-top:2px}
.badge{display:inline-flex;align-items:center;gap:3px;padding:2px 7px;border-radius:7px;font-size:9px;font-weight:700;text-transform:uppercase}
.badge-rec{background:rgba(99,102,241,.18);color:#a5b4fc}
.badge-man{background:rgba(167,139,250,.18);color:#c4b5fd}
.modal-overlay{position:fixed;inset:0;background:rgba(9,9,15,.75);z-index:150;display:flex;align-items:flex-end;-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}
.modal{background:var(--bg2);border-radius:26px 26px 0 0;padding:8px 20px 20px;width:100%;max-height:85vh;overflow-y:auto;border-top:1px solid rgba(255,255,255,.08)}
.modal-title{font-size:16px;font-weight:700;margin-bottom:16px;letter-spacing:-.02em;padding-top:12px}
.fab{position:fixed;bottom:98px;right:18px;width:56px;height:56px;border-radius:28px;background:var(--in);border:none;color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 6px 24px rgba(99,102,241,.5),0 2px 8px rgba(99,102,241,.25);z-index:90;transition:transform .18s cubic-bezier(.34,1.56,.64,1),box-shadow .18s;-webkit-tap-highlight-color:transparent}
.fab:active{transform:scale(.88);box-shadow:0 2px 8px rgba(99,102,241,.25)}
.txr:active{opacity:.75}.sbox:active{opacity:.75}.fp:active{opacity:.7}.tmpl:active{transform:scale(.94)}
.mnavbtn{background:none;border:none;color:var(--tx2);font-size:22px;cursor:pointer;padding:4px 14px;border-radius:10px;line-height:1;transition:background .15s}
.mnavbtn:active{background:rgba(255,255,255,.07)}
.mnavbtn:disabled{opacity:.2;cursor:default}
.srch-wrap{position:relative;margin-bottom:10px}
.srch{width:100%;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.07);border-radius:13px;padding:9px 12px 9px 36px;color:var(--tx);font-size:13px;outline:none;-webkit-appearance:none;font-family:inherit;transition:border-color .2s,background .2s}
.srch:focus{border-color:var(--in);background:rgba(99,102,241,.06)}
.srch-ico{position:absolute;left:11px;top:50%;transform:translateY(-50%);font-size:14px;pointer-events:none;opacity:.45}
.sw-wrap{position:relative;overflow:hidden;border-radius:16px;margin-bottom:8px}
.sw-del{position:absolute;right:0;top:0;bottom:0;width:72px;background:var(--rd);border:none;color:#fff;font-size:20px;cursor:pointer;border-radius:0 16px 16px 0;display:flex;align-items:center;justify-content:center}
.sw-inner{transform:translateX(0);touch-action:pan-y;will-change:transform;border-radius:16px;margin:0}
.bprog{height:4px;background:rgba(255,255,255,.08);border-radius:2px;margin-top:5px;overflow:hidden}
.bprogf{height:4px;border-radius:2px;transition:width .4s}
</style>'''

if style_start >= 0 and style_end > style_start:
    content = content[:style_start] + NEW_CSS + content[style_end:]
    changes += 1
    print('OK 1: CSS Foundation (Glass Design System) aplicado')
else:
    print('FAIL 1: style block not found')

# ── SPRINT 2: NAV SVG ICONS ──────────────────────────────────────────────────
# SVG icons as single-quoted JS strings (double-quoted SVG attributes = safe)
DASHBOARD_SVG = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>'
SCAN_SVG      = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>'
MANUAL_SVG    = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>'
GMAIL_SVG     = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="2,4 12,13 22,4"/></svg>'
HISTORY_SVG   = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><polyline points="12,7 12,12 15,15"/></svg>'
RECON_SVG     = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>'
SETTINGS_SVG  = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>'

OLD_NAV = "const NAV=[{id:'dashboard',ic:'\U0001f4ca',lb:'Dashboard'},{id:'scan',ic:'\U0001f4f7',lb:'Escanear'},{id:'manual',ic:'➕',lb:'Manual'},{id:'gmail',ic:'\U0001f4e7',lb:'Gmail'},{id:'history',ic:'\U0001f4cb',lb:'Historial'},{id:'reconcile',ic:'\U0001f504',lb:'Conciliar'},{id:'settings',ic:'⚙️',lb:'Config'}];"

NEW_NAV = (
    "const NAV=["
    "{id:'dashboard',ic:'" + DASHBOARD_SVG + "',lb:'Dashboard'},"
    "{id:'scan',ic:'" + SCAN_SVG + "',lb:'Escanear'},"
    "{id:'manual',ic:'" + MANUAL_SVG + "',lb:'Manual'},"
    "{id:'gmail',ic:'" + GMAIL_SVG + "',lb:'Gmail'},"
    "{id:'history',ic:'" + HISTORY_SVG + "',lb:'Historial'},"
    "{id:'reconcile',ic:'" + RECON_SVG + "',lb:'Conciliar'},"
    "{id:'settings',ic:'" + SETTINGS_SVG + "',lb:'Config'}"
    "];"
)

if OLD_NAV in content:
    content = content.replace(OLD_NAV, NEW_NAV, 1)
    changes += 1
    print('OK 2: NAV SVG icons aplicados (7 tabs)')
else:
    print('SKIP 2: NAV constant not found (encoding issue?)')
    idx = content.find("const NAV=[")
    if idx > 0:
        print(f'  NAV at {idx}: {repr(content[idx:idx+120])}')

# ── SPRINT 3: FAB SVG icon ────────────────────────────────────────────────────
FAB_CAMERA_SVG = (
    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>'
    '<circle cx="12" cy="13" r="4"/></svg>'
)

OLD_FAB = '>📷</button>'
NEW_FAB = '>' + FAB_CAMERA_SVG + '</button>'

if OLD_FAB in content:
    content = content.replace(OLD_FAB, NEW_FAB, 1)
    changes += 1
    print('OK 3: FAB camera emoji → SVG icon')
else:
    print('SKIP 3: FAB emoji not found')

# ── SPRINT 4: Header subtitle color ──────────────────────────────────────────
# Update hardcoded colors in header subtitle to use CSS vars
OLD_HDR_SUB = '<p style="font-size:10px;color:#94a3b8;margin-top:1px">'
NEW_HDR_SUB = '<p style="font-size:11px;color:var(--tx2);margin-top:2px;letter-spacing:.01em">'

if OLD_HDR_SUB in content:
    content = content.replace(OLD_HDR_SUB, NEW_HDR_SUB, 1)
    changes += 1
    print('OK 4: Header subtitle — hardcoded color → CSS var')
else:
    print('SKIP 4: header subtitle not found')

OLD_HDR_VER = '<span style="color:#334155;margin-left:4px">'
NEW_HDR_VER = '<span style="color:var(--tx3);margin-left:6px;font-size:10px">'

if OLD_HDR_VER in content:
    content = content.replace(OLD_HDR_VER, NEW_HDR_VER, 1)
    changes += 1
    print('OK 5: Header version color → CSS var')
else:
    print('SKIP 5: version span not found')

print(f'\nTotal changes: {changes}/5')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
