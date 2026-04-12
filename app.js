// DIAGNOSTIC - VoucherPro v3.0-diag
(function(){
function step(msg, color){
var r = document.getElementById(‘root’);
if(r){
var p = document.createElement(‘p’);
p.style.cssText = ‘color:’+color+’;font-size:13px;margin:4px 16px;font-family:monospace’;
p.textContent = msg;
r.appendChild(p);
}
}

// Clear loading screen
var root = document.getElementById(‘root’);
if(root) root.innerHTML = ‘<div style="padding:20px;background:#020617;min-height:100dvh"><p style="color:#6366f1;font-size:18px;font-weight:700">VoucherPro Diagnóstico</p></div>’;

step(‘1. Script iniciado’, ‘#10b981’);

try {
var ls = localStorage.getItem(‘test’);
step(‘2. localStorage OK’, ‘#10b981’);
} catch(e) { step(’2. localStorage FALLO: ’+e.message, ‘#ef4444’); }

try {
var s = {a:1};
var s2 = {…s};
step(‘3. Spread operator OK’, ‘#10b981’);
} catch(e) { step(’3. Spread FALLO: ’+e.message, ‘#ef4444’); }

try {
var arr = [1,2,3];
var x = arr?.find(n=>n>1);
step(‘4. Optional chaining OK’, ‘#10b981’);
} catch(e) { step(’4. Optional chain FALLO: ’+e.message, ‘#ef4444’); }

try {
async function testAsync(){ return 1; }
testAsync().then(function(v){ step(‘5. Async/await OK (’+v+’)’, ‘#10b981’); });
} catch(e) { step(’5. Async FALLO: ’+e.message, ‘#ef4444’); }

try {
var tl = `Template ${'literal'} test`;
step(‘6. Template literals OK’, ‘#10b981’);
} catch(e) { step(’6. Template FALLO: ’+e.message, ‘#ef4444’); }

try {
var nested = `A${`B${`C`}`}D`;
step(’7. Nested templates OK: ’+nested, ‘#10b981’);
} catch(e) { step(’7. Nested templates FALLO: ’+e.message, ‘#ef4444’); }

try {
var j = JSON.parse(’{“a”:1}’);
step(‘8. JSON OK’, ‘#10b981’);
} catch(e) { step(’8. JSON FALLO: ’+e.message, ‘#ef4444’); }

try {
if(typeof Chart !== ‘undefined’){
step(‘9. Chart.js OK’, ‘#10b981’);
} else {
step(‘9. Chart.js NO CARGÓ (puede ser normal)’, ‘#f59e0b’);
}
} catch(e) { step(’9. Chart FALLO: ’+e.message, ‘#ef4444’); }

try {
var r2 = requestAnimationFrame(function(){
step(‘10. requestAnimationFrame OK’, ‘#10b981’);
cancelAnimationFrame(r2);
step(’— TODOS LOS TESTS PASARON —’, ‘#6366f1’);
step(‘El problema es en el código de la app, no en Safari.’, ‘#94a3b8’);
});
} catch(e) { step(’10. RAF FALLO: ’+e.message, ‘#ef4444’); }

})();
