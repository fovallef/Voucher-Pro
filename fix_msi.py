#!/usr/bin/env python3
"""
MSI (Meses Sin Intereses) tracking feature.

Changes:
A. pdfPrompt — add MSI detection instructions + msi_charges to JSON schema
B. stmt object — add msi_charges field
C. S object — add msiCommitments:[]
D. persist — save vp_msic
E. loadState — load vp_msic
F. rReconResult — add MSI section with register buttons
G. attachReconResult — add [data-msi] click handler
H. rDash — add MSI committed balance section
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ─── A. pdfPrompt: add MSI instructions + msi_charges to JSON schema ──────────
OLD_SCHEMA = (
    ',"status":"matched|unrecognized"}],"summary":"resumen"}\'+\'CRITICO'
)
NEW_SCHEMA = (
    ',"status":"matched|unrecognized"}]'
    ',"msi_charges":[{"merchant":"nombre","amount":0,"installments":3,"monthly_amount":0,"date":"YYYY-MM-DD"}]'
    ',"summary":"resumen"}\''
    '+"MSI(MESES SIN INTERESES):Si detectas cargos a plazos(palabras clave:\'3 MSI\',\'6 MSI\',\'12 MSI\',\'meses sin intereses\',\'(001:003)\',\'plan de pagos\'),inclúyelos en msi_charges con el monto TOTAL del cargo,el número de meses y monthly_amount=amount/installments.IMPORTANTE:inclúyelos TAMBIÉN en statement_txs como cualquier otro cargo."'
    "+'CRITICO"
)

if OLD_SCHEMA in content:
    content = content.replace(OLD_SCHEMA, NEW_SCHEMA, 1)
    changes += 1
    print('OK A: pdfPrompt — MSI detection + msi_charges schema')
else:
    print('SKIP A: schema anchor not found')
    idx = content.find('"status":"matched|unrecognized"')
    print(f'  idx: {idx}')
    if idx > 0:
        print(repr(content[idx:idx+120]))

# ─── B. stmt object: add msi_charges ─────────────────────────────────────────
OLD_STMT = "statement_txs:res.statement_txs||[]};if(!Object.keys(res).length)"
NEW_STMT = "statement_txs:res.statement_txs||[],msi_charges:res.msi_charges||[]};if(!Object.keys(res).length)"

if OLD_STMT in content:
    content = content.replace(OLD_STMT, NEW_STMT, 1)
    changes += 1
    print('OK B: stmt object — msi_charges added')
else:
    print('SKIP B: stmt object pattern not found')

# ─── C. S object: add msiCommitments ─────────────────────────────────────────
OLD_S = "manualForm:{merchant:'',category:'',amount:'',currency:'MXN',date:'',time:'',card:'',msi:null,cfdi:{rfc:'',folio:''},isRecurring:false,notes:''},};"
NEW_S = "manualForm:{merchant:'',category:'',amount:'',currency:'MXN',date:'',time:'',card:'',msi:null,cfdi:{rfc:'',folio:''},isRecurring:false,notes:''},msiCommitments:[]};"

if OLD_S in content:
    content = content.replace(OLD_S, NEW_S, 1)
    changes += 1
    print('OK C: S object — msiCommitments:[] added')
else:
    print('SKIP C: S object manualForm tail not found')

# ─── D. persist: save vp_msic ────────────────────────────────────────────────
OLD_PERSIST = "_save('vp_st',JSON.stringify(S.statements));_save('vp_bg'"
NEW_PERSIST = "_save('vp_st',JSON.stringify(S.statements));_save('vp_msic',JSON.stringify(S.msiCommitments||[]));_save('vp_bg'"

if OLD_PERSIST in content:
    content = content.replace(OLD_PERSIST, NEW_PERSIST, 1)
    changes += 1
    print('OK D: persist — vp_msic added')
else:
    print('SKIP D: persist anchor not found')

# ─── E. loadState: load vp_msic ──────────────────────────────────────────────
OLD_LOAD = "try{const _bg=localStorage.getItem('vp_bg');if(_bg)S.budgets=JSON.parse(_bg);}catch(e){}"
NEW_LOAD = (
    "try{const _msic=localStorage.getItem('vp_msic');if(_msic)S.msiCommitments=JSON.parse(_msic);}catch(e){}"
    "try{const _bg=localStorage.getItem('vp_bg');if(_bg)S.budgets=JSON.parse(_bg);}catch(e){}"
)

if OLD_LOAD in content:
    content = content.replace(OLD_LOAD, NEW_LOAD, 1)
    changes += 1
    print('OK E: loadState — vp_msic load added')
else:
    print('SKIP E: loadState budgets anchor not found')

# ─── F. rReconResult: add MSI section before matched section ─────────────────
# Find the unique end of the unrecog section, just before the matched section
OLD_RECON_END = (
    "}\`:''}${matched.length?`"
    "<p class=\"stit\"style=\"color:#10b981;margin-top:4px\">"
    "✅ Conciliados correctamente(${matched.length})</p>"
)
NEW_RECON_END = (
    "}`:''}${(r.msi_charges||[]).length?"
    # MSI detected section
    "`<p class=\"stit\" style=\"color:#818cf8;margin-top:4px\">📅 Cargos MSI detectados en el estado de cuenta</p>"
    "${(r.msi_charges||[]).map((m,i)=>`"
    "<div style=\"background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.3);border-radius:14px;padding:13px;margin-bottom:9px\">"
    "<div style=\"display:flex;justify-content:space-between;align-items:start;margin-bottom:8px\">"
    "<div><p style=\"font-weight:700;font-size:13px\">${esc(m.merchant)}</p>"
    "<p style=\"font-size:11px;color:#94a3b8\">${m.date} · Total: ${fS(m.amount)}</p>"
    "<p style=\"font-size:11px;color:#818cf8;margin-top:2px\">${m.installments} meses · ${fS(m.monthly_amount)}/mes</p>"
    "</div><span style=\"font-size:20px\">💳</span></div>"
    "<button class=\"btn\" style=\"margin:0;padding:9px;font-size:12px;background:rgba(99,102,241,.15);"
    "border:1px solid rgba(99,102,241,.4);color:#818cf8\" data-msi=\"${i}\">📅 Registrar compromiso MSI</button>"
    "</div>`).join('')}"
    "`:''}${matched.length?`"
    "<p class=\"stit\"style=\"color:#10b981;margin-top:4px\">"
    "✅ Conciliados correctamente(${matched.length})</p>"
)

if OLD_RECON_END in content:
    content = content.replace(OLD_RECON_END, NEW_RECON_END, 1)
    changes += 1
    print('OK F: rReconResult — MSI section added')
else:
    print('SKIP F: rReconResult end anchor not found')
    idx = content.find('Conciliados correctamente')
    print(f'  idx: {idx}')
    if idx > 0:
        print(repr(content[idx-80:idx+80]))

# ─── G. attachReconResult: add [data-msi] handler ────────────────────────────
OLD_ATTACH_END = (
    "document.querySelectorAll('[data-disputar]').forEach(b=>b.addEventListener('click',()=>"
    "{const t=unrecog[parseInt(b.dataset.disputar)];if(!t)return;S.disputeModal={tx:t};render();}));"
    "}"
)
NEW_ATTACH_END = (
    "document.querySelectorAll('[data-disputar]').forEach(b=>b.addEventListener('click',()=>"
    "{const t=unrecog[parseInt(b.dataset.disputar)];if(!t)return;S.disputeModal={tx:t};render();}));"
    # MSI handler: register commitment
    "document.querySelectorAll('[data-msi]').forEach(b=>b.addEventListener('click',()=>{"
    "const m=(r.msi_charges||[])[parseInt(b.dataset.msi)];if(!m)return;"
    "if(!confirm('Registrar compromiso MSI:\\n'+m.merchant+'\\n'+m.installments+' meses · '+fS(m.monthly_amount)+'/mes\\nTotal: '+fS(m.amount)))return;"
    "const cmt={id:uid(),merchant:m.merchant,cardName:r.card_name||'',totalAmount:parseFloat(m.amount||0),"
    "installments:parseInt(m.installments||0),monthlyAmount:parseFloat(m.monthly_amount||0),"
    "startDate:m.date||td(),registeredAt:new Date().toISOString()};"
    "if(!S.msiCommitments)S.msiCommitments=[];"
    "S.msiCommitments.push(cmt);persist();"
    "b.textContent='✅ Registrado';b.disabled=true;"
    "}));"
    "}"
)

if OLD_ATTACH_END in content:
    content = content.replace(OLD_ATTACH_END, NEW_ATTACH_END, 1)
    changes += 1
    print('OK G: attachReconResult — [data-msi] handler added')
else:
    print('SKIP G: attachReconResult end not found')

# ─── H. rDash: add MSI committed section ─────────────────────────────────────
# Insert after the recTot section (recurring subscriptions card)
OLD_DASH_AFTER_REC = (
    "+(recTot>0?'<div class=\"sbox\"style=\"margin-bottom:12px;display:flex;align-items:center;gap:12px\">"
    "<span style=\"font-size:26px\">🔁</span><div>"
    "<p style=\"font-size:11px;color:var(--tx2)\">Recurrentes mensuales</p>"
    "<p style=\"font-size:14px;font-weight:700;color:var(--am)\">'+fS(recTot)+'/mes</p>"
    "<p style=\"font-size:10px;color:#64748b\">~'+fS(recTot*12)+'/año estimado</p>"
    "</div></div>':'')"
    "+'<div class=\"card\"style=\"padding:12px\"><p class=\"stit\">Por Categoría(MXN)</p>"
)
NEW_DASH_AFTER_REC = (
    "+(recTot>0?'<div class=\"sbox\"style=\"margin-bottom:12px;display:flex;align-items:center;gap:12px\">"
    "<span style=\"font-size:26px\">🔁</span><div>"
    "<p style=\"font-size:11px;color:var(--tx2)\">Recurrentes mensuales</p>"
    "<p style=\"font-size:14px;font-weight:700;color:var(--am)\">'+fS(recTot)+'/mes</p>"
    "<p style=\"font-size:10px;color:#64748b\">~'+fS(recTot*12)+'/año estimado</p>"
    "</div></div>':'')"
    # MSI committed balance section
    "+(()=>{"
    "const now=new Date();"
    "const active=(S.msiCommitments||[]).filter(c=>{"
    "const start=new Date(c.startDate||'');if(isNaN(start.getTime()))return false;"
    "const end=new Date(start);end.setMonth(end.getMonth()+parseInt(c.installments||0));"
    "return end>now;"
    "});"
    "if(!active.length)return'';"
    "const totalMsi=active.reduce((s,c)=>s+parseFloat(c.monthlyAmount||0),0);"
    "const byCard={};"
    "active.forEach(c=>{const k=c.cardName||'Sin tarjeta';if(!byCard[k])byCard[k]=0;byCard[k]+=parseFloat(c.monthlyAmount||0);});"
    "const rows=Object.entries(byCard).map(([k,v])=>'<div style=\"display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(99,102,241,.1)\"><span style=\"font-size:12px;color:#94a3b8\">'+esc(k)+'</span><span style=\"font-size:12px;font-weight:600;color:#818cf8\">'+fS(v)+'/mes</span></div>').join('');"
    "return'<div class=\"sbox\"style=\"margin-bottom:12px\">'"
    "+'<div style=\"display:flex;align-items:center;gap:10px;margin-bottom:10px\">'"
    "+'<span style=\"font-size:24px\">💳</span>'"
    "+'<div><p style=\"font-size:11px;color:var(--tx2)\">MSI Comprometido</p>'"
    "+'<p style=\"font-size:16px;font-weight:700;color:#818cf8\">'+fS(totalMsi)+'/mes</p>'"
    "+'<p style=\"font-size:10px;color:#64748b\">'+active.length+' compromiso'+(active.length>1?'s':'')+' activo'+(active.length>1?'s':'')+'</p></div></div>'"
    "+rows+'</div>';"
    "})()"
    "+'<div class=\"card\"style=\"padding:12px\"><p class=\"stit\">Por Categoría(MXN)</p>"
)

if OLD_DASH_AFTER_REC in content:
    content = content.replace(OLD_DASH_AFTER_REC, NEW_DASH_AFTER_REC, 1)
    changes += 1
    print('OK H: rDash — MSI committed section added')
else:
    print('SKIP H: rDash recTot anchor not found')
    idx = content.find('Recurrentes mensuales')
    print(f'  idx: {idx}')
    if idx > 0:
        print(repr(content[idx-30:idx+100]))

print(f'\nTotal changes: {changes}/8')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
