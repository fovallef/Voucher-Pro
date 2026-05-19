#!/usr/bin/env python3
"""
fix_version_check_v590.py — Reemplazar SW por version-check directo v5.90

SW de v5.86-v5.88 no funciona en iOS Safari PWA standalone mode.
Cambio approach: fetch directo de index.html cada 3 min + al
volverse visible la app. Compara APP_VERSION local vs remoto.
Si distinto, muestra barra azul con boton Actualizar.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the SW block (if exists)
sw_start = content.find("<script>if('serviceWorker' in navigator)")
if sw_start > 0:
    sw_end = content.find('</script>', sw_start) + len('</script>')
    content = content[:sw_start] + content[sw_end:]
    print(f"Removed SW block ({sw_end - sw_start} chars)")

# Build new version-check JS (single line, no // comments)
VC_JS = (
    "<script>"
    "(function(){"
    "var curVer=null;"
    "try{var mm=document.documentElement.outerHTML.match(/APP_VERSION=." + r"(v[\d.]+)" + "/);if(mm)curVer=mm[1];}catch(e){}"
    "function check(){"
    "fetch('./index.html?_t='+Date.now(),{cache:'no-store'})"
    ".then(function(r){return r.text();})"
    ".then(function(html){"
    "var m2=html.match(/APP_VERSION=." + r"(v[\d.]+)" + "/);"
    "if(m2&&curVer&&m2[1]!==curVer){"
    "if(!document.getElementById('vp-update-bar')){"
    "var bar=document.createElement('div');"
    "bar.id='vp-update-bar';"
    "bar.style.cssText='position:fixed;top:0;left:0;right:0;background:#6366f1;color:#fff;padding:10px 16px;text-align:center;font-size:13px;font-weight:600;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,.3);font-family:-apple-system,sans-serif';"
    "bar.innerHTML='✨ Nueva versión ('+m2[1]+') disponible · <button id=\"vpUpd\" style=\"background:#fff;color:#6366f1;border:none;padding:5px 12px;border-radius:6px;font-weight:700;margin-left:8px;cursor:pointer\">Actualizar</button>';"
    "document.body.appendChild(bar);"
    "document.getElementById('vpUpd').onclick=function(){location.reload();};"
    "}}"
    "}).catch(function(e){});"
    "}"
    "window.addEventListener('load',function(){setTimeout(check,3000);setInterval(check,180000);});"
    "document.addEventListener('visibilitychange',function(){if(!document.hidden)check();});"
    "})();"
    "</script>"
)

# Insert before </body>
if '</body>' in content:
    content = content.replace('</body>', VC_JS + '</body>', 1)
    print('OK: version-check inserted before </body>')
else:
    print('FAIL: </body> not found')

# Bump version
m = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if m:
    new = re.sub(r'v[\d.]+', 'v5.90', m.group(1))
    content = content.replace(m.group(0), f"APP_VERSION='{new}'", 1)
    print(f'Version: {m.group(1)} -> {new}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
