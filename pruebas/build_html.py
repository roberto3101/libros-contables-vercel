# -*- coding: utf-8 -*-
import io, html, base64, json

PROJ = r"C:/Users/user/Desktop/libros-contables"
SCR  = r"C:/Users/user/AppData/Local/Temp/claude/C--Users-user-Desktop-libros-contables/00d8bcd0-b8c0-4bcc-a6f3-485232b243a8/scratchpad"
OUT  = SCR + "/ple_libro3.html"

# ---------- extraer ramas antes/despues ----------
def branches(path):
    t=io.open(path,encoding="utf-16").read()
    accs=['030800','030900','031100','031200','031300','031400']
    out={}
    for i in range(5):
        a=t.find("else If @Accion='"+accs[i]+"'"); z=t.find("else If @Accion='"+accs[i+1]+"'")
        out[accs[i]]=t[a:z].rstrip("\n\t ")
    return out
BEF=branches(PROJ+"/Ct_Pro_PLE_20260701.sql.bak")
AFT=branches(PROJ+"/Ct_Pro_PLE_20260701.sql")

# ---------- descargables (base64) ----------
def enc(s): return base64.b64encode(s.encode("utf-8")).decode()
ORDER=['030800','030900','031100','031200','031300']
BOOK = {
 '030800': ("3.8","Cuenta 30 — Inversiones Mobiliarias","Detalle del saldo de la cuenta 30"),
 '030900': ("3.9","Cuenta 34 — Intangibles","Detalle del saldo de la cuenta 34"),
 '031100': ("3.11","Cuenta 41 — Remuneraciones y Participaciones por Pagar","Detalle del saldo de la cuenta 41"),
 '031200': ("3.12","Cuentas 42 y 43 — Cuentas por Pagar Comerciales","Detalle del saldo de las cuentas 42/43"),
 '031300': ("3.13","Cuentas 46 y 47 — Cuentas por Pagar Diversas","Detalle del saldo de las cuentas 46/47"),
}
DL_FILE = {
 '030800':"libro_3.8_cuenta_30.sql", '030900':"libro_3.9_cuenta_34.sql",
 '031100':"libro_3.11_cuenta_41.sql", '031200':"libro_3.12_cuentas_42-43.sql",
 '031300':"libro_3.13_cuentas_46-47.sql",
}
def perbook_sql(acc):
    num,titulo,sub=BOOK[acc]
    hdr=("/* =====================================================================\n"
         "   PLE Libro 3 - Formato %s  (%s)\n"
         "   Rama @Accion='%s' del stored procedure Ct_Pro_PLE (BD CodeplexWeb_2020).\n"
         "   Contiene UNICAMENTE este libro; no modifica los demas formatos del SP.\n"
         "   ===================================================================== */\n\n") % (num, titulo, acc)
    return hdr+AFT[acc]
global_sql=("/* =====================================================================\n"
   "   PLE Libro 3 - Los 5 formatos ASIGNADOS: 3.8, 3.9, 3.11, 3.12, 3.13\n"
   "   Ramas del stored procedure Ct_Pro_PLE (BD CodeplexWeb_2020).\n"
   "   Solo estos libros; NO tocan los demas (~40) formatos del procedimiento.\n"
   "   ===================================================================== */\n\n"
   + "\n\n\n".join(AFT[k] for k in ORDER))
SCHEMA_B64 = enc(io.open(SCR+"/schema.sql",encoding="utf-8").read())
GLOBAL_B64 = enc(global_sql)
PERBOOK_B64 = {a: enc(perbook_sql(a)) for a in ORDER}

# ---------- metadata de formatos ----------
BOOK = {
 '030800': ("3.8","Cuenta 30 — Inversiones Mobiliarias","Detalle del saldo de la cuenta 30"),
 '030900': ("3.9","Cuenta 34 — Intangibles","Detalle del saldo de la cuenta 34"),
 '031100': ("3.11","Cuenta 41 — Remuneraciones y Participaciones por Pagar","Detalle del saldo de la cuenta 41"),
 '031200': ("3.12","Cuentas 42 y 43 — Cuentas por Pagar Comerciales","Detalle del saldo de las cuentas 42/43"),
 '031300': ("3.13","Cuentas 46 y 47 — Cuentas por Pagar Diversas","Detalle del saldo de las cuentas 46/47"),
}

# fuente / grano / decisiones senior por formato
DESC = {
 '030800': dict(
   fuente="ct_diarios (cuentas 30x) + LEFT JOIN zg_auxiliares para el emisor del título.",
   grano="Un registro por asiento contable y emisor; el costo total es SUM(debe − haber) = saldo deudor (activo).",
   cambios=[
     "El original filtraba <code>left(idcuenta,2)='14'</code> (bug: cuenta equivocada) → corregido a <code>idcuenta like '30%'</code>.",
     "Se añadió la salida dual TXT / Excel (antes sólo devolvía un SELECT crudo).",
     "Predicado SARGable, saneamiento de texto y estado 1/8/9."],
   todos=["Campos 7–9 y 11 (código de título, valor nominal, cantidad, provisión): el sistema no captura datos de títulos → salen en '00' / '0.00'. Confirmar fuente."]),
 '030900': dict(
   fuente="ct_diarios (cuentas 34x) + INNER JOIN ct_activo_fijo (descripción y valor contable).",
   grano="Un registro por asiento contable e intangible.",
   cambios=[
     "Campo 4 pasa a ser la fecha de inicio de operación con formato DD/MM/AAAA.",
     "Se unificó el correlativo del asiento (el original arrastraba dos columnas).",
     "Salida dual TXT / Excel, SARGable y estado 1/8/9."],
   todos=["Campo 8 (amortización acumulada, debe ser negativa): falta la fuente real (cuenta 39 asociada o campo de ct_activo_fijo) → sale en 0.00. Confirmar."]),
 '031100': dict(
   fuente="ct_diarios (cuentas 41x) + INNER JOIN zg_auxiliares (datos del trabajador).",
   grano="Un registro por asiento contable y trabajador.",
   cambios=[
     "Saldo final = SUM(haber − debe) → POSITIVO como exige el layout (el original daba negativo).",
     "Salida dual TXT / Excel, SARGable, saneamiento de texto y estado 1/8/9."],
   todos=[]),
 '031200': dict(
   fuente="ct_diarios (cuentas 42x y 43x) + INNER JOIN zg_proveedores.",
   grano="Un registro por asiento contable y proveedor.",
   cambios=[
     "Monto por pagar = SUM(haber − debe) → POSITIVO (el original daba negativo).",
     "Campo 6 es la fecha de emisión del comprobante en formato DD/MM/AAAA.",
     "Salida dual TXT / Excel, SARGable y estado 1/8/9."],
   todos=[]),
 '031300': dict(
   fuente="ct_diarios (cuentas 46x y 47x) + INNER JOIN zg_proveedores.",
   grano="Un registro por asiento contable, tercero y cuenta contable.",
   cambios=[
     "Monto pendiente = SUM(haber − debe) → POSITIVO. Incluye el código de cuenta contable (campo 8).",
     "Salida dual TXT / Excel, SARGable y estado 1/8/9."],
   todos=["Se asume que la contraparte es proveedor (como el código original). Confirmar si puede ser cliente/auxiliar."]),
}

# campos por formato: (num, etiqueta ubicua, descripcion completa SUNAT)
F = {
 '030800': [
  (1,"Periodo tributario","Periodo del libro en formato AAAAMMDD (el día se registra como '00'). Debe ser menor o igual al periodo informado."),
  (2,"Código único de operación","Código Único de la Operación: llave del asiento contable, idéntica a la del Libro Diario. Alias en el SP: codigo_unico_operacion (lee la columna existente d.cuo)."),
  (3,"Correlativo del asiento","Número correlativo del asiento. El primer dígito es A (apertura), M (movimiento del mes) o C (cierre)."),
  (4,"Tipo documento identidad emisor","Tipo de documento de identidad del emisor del título (Tabla 2). Si no existe se registra '0'."),
  (5,"Número documento identidad emisor","Número de documento de identidad del emisor. Si no existe se registra '0'."),
  (6,"Razón social del emisor","Apellidos y nombres, denominación o razón social del emisor. Saneado de tabs/saltos de línea."),
  (7,"Código tipo de título","Tipo de título según Tabla 15. TODO: el sistema no captura este dato → '00'."),
  (8,"Valor nominal unitario","Valor nominal unitario del título. TODO: sin fuente → 0.00."),
  (9,"Cantidad de títulos","Cantidad de títulos. TODO: sin fuente → 0."),
  (10,"Costo total en libros","Valor en libros: costo total de los títulos. Positivo o 0.00. Calculado como SUM(debe − haber)."),
  (11,"Provisión total en libros","Valor en libros: provisión total. Negativo o 0.00. TODO: sin fuente → 0.00."),
  (12,"Estado de operación","Estado de la operación: 1 = del periodo, 8 = anterior no anotada, 9 = anterior anotada. Por defecto 1."),
 ],
 '030900': [
  (1,"Periodo tributario","Periodo AAAAMMDD (día '00'). Menor o igual al periodo informado."),
  (2,"Código único de operación","Código Único de la Operación, igual al del Libro Diario. Alias en el SP: codigo_unico_operacion (lee d.cuo)."),
  (3,"Correlativo del asiento","Correlativo del asiento; primer dígito A / M / C."),
  (4,"Fecha inicio de operación","Fecha de inicio de la operación en formato DD/MM/AAAA."),
  (5,"Código de cuenta contable","Código de la cuenta contable (34…) al máximo nivel de dígitos utilizado."),
  (6,"Descripción del intangible","Descripción del intangible. Saneada de tabs/saltos de línea, hasta 40 caracteres."),
  (7,"Valor contable del intangible","Valor contable del intangible. Positivo o 0.00."),
  (8,"Amortización contable acumulada","Amortización contable acumulada. Negativo o 0.00. TODO: confirmar fuente → 0.00."),
  (9,"Estado de operación","1 = del periodo, 8 = anterior no anotada, 9 = anterior anotada. Por defecto 1."),
 ],
 '031100': [
  (1,"Periodo tributario","Periodo AAAAMMDD (día '00')."),
  (2,"Código único de operación","Código Único de la Operación, igual al del Libro Diario. Alias: codigo_unico_operacion (lee d.cuo)."),
  (3,"Correlativo del asiento","Correlativo del asiento; primer dígito A / M / C."),
  (4,"Código de cuenta contable","Código de la cuenta contable de la obligación (41…)."),
  (5,"Tipo documento identidad trabajador","Tipo de documento de identidad del trabajador (Tabla 2)."),
  (6,"Número documento identidad trabajador","Número de documento de identidad del trabajador."),
  (7,"Código del trabajador","Código interno del trabajador."),
  (8,"Apellidos y nombres del trabajador","Apellidos y nombres del trabajador. Saneado de tabs/saltos de línea."),
  (9,"Saldo final por pagar","Saldo final de la cuenta por pagar. Positivo o 0.00. Calculado como SUM(haber − debe)."),
  (10,"Estado de operación","1 = del periodo, 8 = anterior no anotada, 9 = anterior anotada. Por defecto 1."),
 ],
 '031200': [
  (1,"Periodo tributario","Periodo AAAAMMDD (día '00')."),
  (2,"Código único de operación","Código Único de la Operación, igual al del Libro Diario. Alias: codigo_unico_operacion (lee d.cuo)."),
  (3,"Correlativo del asiento","Correlativo del asiento; primer dígito A / M / C."),
  (4,"Tipo documento identidad proveedor","Tipo de documento de identidad del proveedor (Tabla 2)."),
  (5,"Número documento identidad proveedor","Número de documento de identidad del proveedor."),
  (6,"Fecha de emisión del comprobante","Fecha de emisión del comprobante de pago, formato DD/MM/AAAA."),
  (7,"Razón social del proveedor","Apellidos y nombres, denominación o razón social del proveedor. Saneado."),
  (8,"Monto de cuenta por pagar","Monto de cada cuenta por pagar al proveedor. Positivo o 0.00. SUM(haber − debe)."),
  (9,"Estado de operación","1 = del periodo, 8 = anterior no anotada, 9 = anterior anotada. Por defecto 1."),
 ],
 '031300': [
  (1,"Periodo tributario","Periodo AAAAMMDD (día '00')."),
  (2,"Código único de operación","Código Único de la Operación, igual al del Libro Diario. Alias: codigo_unico_operacion (lee d.cuo)."),
  (3,"Correlativo del asiento","Correlativo del asiento; primer dígito A / M / C."),
  (4,"Tipo documento identidad tercero","Tipo de documento de identidad del tercero (Tabla 2)."),
  (5,"Número documento identidad tercero","Número de documento de identidad del tercero."),
  (6,"Fecha de emisión del comprobante","Fecha de emisión del comprobante o de inicio de la operación, DD/MM/AAAA."),
  (7,"Apellidos y nombres del tercero","Apellidos y nombres de terceros. Saneado de tabs/saltos de línea."),
  (8,"Código de cuenta contable","Código de la cuenta contable de la obligación (46/47…)."),
  (9,"Monto pendiente de pago","Monto pendiente de pago al tercero. Positivo o 0.00. SUM(haber − debe)."),
  (10,"Estado de operación","1 = del periodo, 8 = anterior no anotada, 9 = anterior anotada. Por defecto 1."),
 ],
}

e=html.escape
ORDER=['030800','030900','031100','031200','031300']

def code_block(txt):
    return '<pre class="code"><code>'+e(txt)+'</code></pre>'

def fields_html(acc):
    out=['<div class="fields">']
    for num,lbl,desc in F[acc]:
        todo=' is-todo' if 'TODO' in desc else ''
        out.append(f'<button class="chip{todo}" data-tip="{e(desc)}" data-num="{num}"><span class="chip-n">{num:02d}</span>{e(lbl)}</button>')
    out.append('</div>')
    return ''.join(out)

def section(acc):
    num,titulo,sub=BOOK[acc]; d=DESC[acc]
    cambios=''.join(f'<li>{c}</li>' for c in d['cambios'])
    todos=''.join(f'<li>{e(t)}</li>' for t in d['todos']) if d['todos'] else '<li class="none">Sin pendientes — listo salvo validación con datos reales.</li>'
    return f'''
<section class="fmt" id="s-{acc}" data-acc="{acc}" hidden>
  <header class="fmt-head">
    <div class="fmt-id">{e(num)}</div>
    <div>
      <h2>{e(titulo)}</h2>
      <p class="fmt-sub">@Accion = <code>'{acc}'</code> &nbsp;·&nbsp; {e(sub)}</p>
    </div>
  </header>

  <div class="grid2">
    <div class="panel">
      <h3 class="eyebrow">Descripción</h3>
      <dl class="meta">
        <dt>Fuente de datos</dt><dd>{e(d['fuente'])}</dd>
        <dt>Grano</dt><dd>{e(d['grano'])}</dd>
      </dl>
      <h3 class="eyebrow">Qué cambió</h3>
      <ul class="bullets">{cambios}</ul>
      <h3 class="eyebrow warn-eye">Pendiente de confirmar</h3>
      <ul class="bullets todos">{todos}</ul>
    </div>
    <div class="panel">
      <h3 class="eyebrow">Campos de salida — <span class="hint">pasa el cursor sobre cada campo</span></h3>
      {fields_html(acc)}
      <p class="fieldnote">Los campos libres de utilización no se emiten en el TXT (regla SUNAT: sin dato ni palote).</p>
    </div>
  </div>

  <div class="diff">
    <div class="seg" role="tablist" aria-label="Antes o después">
      <button class="seg-btn is-active" data-code="after" aria-pressed="true">Después</button>
      <button class="seg-btn" data-code="before" aria-pressed="false">Antes</button>
    </div>
    <div class="code-wrap" data-show="after">
      <div class="code-side" data-code="after">{code_block(AFT[acc])}</div>
      <div class="code-side" data-code="before" hidden>{code_block(BEF[acc])}</div>
    </div>
  </div>
</section>'''

tabs=''.join(f'<button class="tab{" is-active" if i==0 else ""}" data-target="{acc}">{e(BOOK[acc][0])}<span>{e(BOOK[acc][1].split("—")[0].strip())}</span></button>' for i,acc in enumerate(ORDER))
sections=''.join(section(a) for a in ORDER)
def dlcard(name,title,sub,data,cls=""):
    return f'<a class="dl {cls}" download="{name}" href="data:application/sql;base64,{data}"><span class="dl-ic">↓</span><span class="dl-t">{e(title)}</span><span class="dl-s">{e(sub)}</span></a>'
global_cards=(dlcard("libros_3.8_a_3.13_asignados.sql","Los 5 libros asignados","Solo 3.8 / 3.9 / 3.11 / 3.12 / 3.13 — no toca los demás",GLOBAL_B64,"dl-global")
             +dlcard("PLE_TEST_db.sql","Base de datos de prueba","Tablas mock + datos de casos borde para reproducir",SCHEMA_B64))
perbook_cards=''.join(dlcard(DL_FILE[a], BOOK[a][0]+" · "+BOOK[a][1].split("—")[1].strip(), "Rama del SP · solo este libro", PERBOOK_B64[a]) for a in ORDER)
downloads=(f'<div class="dl-group"><span class="dl-label">Descarga global</span><div class="dl-row">{global_cards}</div></div>'
           f'<div class="dl-group"><span class="dl-label">Descarga por libro</span><div class="dl-row dl-row-5">{perbook_cards}</div></div>')

HTML=f'''<title>PLE Libro 3 · Ct_Pro_PLE — 5 formatos</title>
<style>
:root{{
  --paper:#F4F6F5; --card:#FBFCFB; --ink:#16201E; --ink-soft:#586662; --line:#DCE3E0;
  --accent:#0B6E63; --accent-deep:#083F39; --before:#B4442E; --ok:#1C7A4E; --warn:#98690F;
  --chip:#EBF1EF; --code-bg:#101E1B; --code-fg:#D7E4E0; --code-dim:#6E9B92;
  --serif:Georgia,'Iowan Old Style','Times New Roman',serif;
  --sans:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  --mono:'Cascadia Code',Consolas,'SFMono-Regular',ui-monospace,monospace;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.55;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1140px;margin:0 auto;padding:0 24px}}
code{{font-family:var(--mono);font-size:.9em}}

/* header */
.top{{border-bottom:1px solid var(--line);background:linear-gradient(180deg,#fff,var(--paper))}}
.top .wrap{{padding:34px 24px 26px}}
.kicker{{font:600 12px/1 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}}
h1{{font-family:var(--serif);font-weight:600;font-size:clamp(28px,4vw,44px);line-height:1.05;margin:12px 0 8px;text-wrap:balance;letter-spacing:-.01em}}
.lede{{max-width:66ch;color:var(--ink-soft);font-size:16px;margin:0}}
.status{{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}}
.pill{{display:inline-flex;align-items:center;gap:7px;font:600 12.5px/1 var(--sans);padding:7px 12px;border-radius:999px;border:1px solid var(--line);background:#fff}}
.pill.ok{{color:var(--ok);border-color:#BEE3CE;background:#F1FaF4}}
.pill .dot{{width:7px;height:7px;border-radius:50%;background:currentColor}}

/* downloads */
.downloads{{display:flex;flex-direction:column;gap:16px;margin-top:22px}}
.dl-label{{display:block;font:600 10.5px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:9px}}
.dl-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
.dl-row-5{{grid-template-columns:repeat(auto-fit,minmax(175px,1fr))}}
.dl-global{{border-color:var(--accent);background:#F1FAF7}}
.dl{{display:flex;flex-direction:column;gap:2px;text-decoration:none;color:var(--ink);border:1px solid var(--line);background:var(--card);border-radius:12px;padding:14px 16px;transition:border-color .15s,transform .15s,box-shadow .15s}}
.dl:hover{{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px -14px rgba(11,110,99,.5)}}
.dl:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.dl-ic{{font-size:15px;color:var(--accent);font-weight:700}}
.dl-t{{font-family:var(--mono);font-size:13.5px;font-weight:600}}
.dl-s{{font-size:12px;color:var(--ink-soft)}}

/* overview */
.section-lead{{padding:34px 0 6px}}
.section-lead h2{{font-family:var(--serif);font-weight:600;font-size:22px;margin:0 0 6px}}
.overview{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;padding:8px 0 6px}}
.ov{{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:16px 18px}}
.ov h4{{margin:0 0 6px;font:600 13px/1.2 var(--sans);letter-spacing:.02em}}
.ov p{{margin:0;font-size:13.5px;color:var(--ink-soft)}}
.ov .k{{font-family:var(--mono);color:var(--accent-deep);font-size:12.5px}}

/* tabs */
.tabbar{{position:sticky;top:0;z-index:20;background:rgba(244,246,245,.9);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);margin-top:26px}}
.tabs{{display:flex;gap:4px;overflow-x:auto;padding:10px 0}}
.tab{{flex:0 0 auto;display:flex;flex-direction:column;gap:2px;align-items:flex-start;border:1px solid transparent;background:transparent;border-radius:10px;padding:8px 14px;cursor:pointer;font:700 15px/1 var(--sans);font-family:var(--serif);color:var(--ink)}}
.tab span{{font-family:var(--sans);font-weight:500;font-size:11.5px;color:var(--ink-soft);letter-spacing:.01em}}
.tab:hover{{background:#fff}}
.tab.is-active{{background:#fff;border-color:var(--line);box-shadow:0 2px 0 var(--accent) inset}}
.tab.is-active{{color:var(--accent-deep)}}

/* format section */
.fmt{{padding:26px 0 8px;animation:fade .25s ease}}
@keyframes fade{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
.fmt-head{{display:flex;gap:16px;align-items:center;margin-bottom:20px}}
.fmt-id{{font-family:var(--serif);font-weight:600;font-size:30px;color:#fff;background:var(--accent);width:64px;height:64px;flex:0 0 auto;border-radius:14px;display:flex;align-items:center;justify-content:center;letter-spacing:-.02em}}
.fmt-head h2{{margin:0;font-family:var(--serif);font-weight:600;font-size:22px}}
.fmt-sub{{margin:3px 0 0;color:var(--ink-soft);font-size:13.5px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.panel{{border:1px solid var(--line);background:var(--card);border-radius:14px;padding:18px 20px}}
.eyebrow{{font:600 11.5px/1.3 var(--sans);letter-spacing:.13em;text-transform:uppercase;color:var(--accent);margin:16px 0 8px}}
.eyebrow:first-child{{margin-top:0}}
.warn-eye{{color:var(--warn)}}
.meta{{margin:0;display:grid;grid-template-columns:auto;gap:2px}}
.meta dt{{font-weight:600;font-size:12.5px;margin-top:6px}}
.meta dd{{margin:0;color:var(--ink-soft);font-size:13.5px}}
.bullets{{margin:0;padding-left:18px}}
.bullets li{{font-size:13.5px;color:var(--ink-soft);margin:5px 0}}
.bullets code{{background:var(--chip);padding:1px 5px;border-radius:5px;color:var(--accent-deep)}}
.todos li{{color:#7a5a12}} .todos .none{{color:var(--ok)}}
.hint{{font-weight:400;text-transform:none;letter-spacing:0;color:var(--ink-soft);font-size:11px}}

/* fields / chips */
.fields{{display:flex;flex-wrap:wrap;gap:7px;margin:2px 0 4px}}
.chip{{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:#fff;border-radius:8px;padding:6px 10px;font:500 12.5px/1 var(--sans);color:var(--ink);cursor:help;transition:border-color .12s,background .12s}}
.chip:hover,.chip:focus-visible{{border-color:var(--accent);background:#F1FAF7;outline:none}}
.chip-n{{font-family:var(--mono);font-size:10.5px;color:#fff;background:var(--accent);border-radius:5px;padding:2px 5px;font-weight:600}}
.chip.is-todo .chip-n{{background:var(--warn)}}
.chip.is-todo{{border-style:dashed}}
.fieldnote{{font-size:12px;color:var(--ink-soft);margin:12px 0 0}}

/* diff */
.diff{{margin-top:16px}}
.seg{{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#fff;margin-bottom:10px}}
.seg-btn{{border:0;background:transparent;padding:8px 18px;font:600 13px/1 var(--sans);cursor:pointer;color:var(--ink-soft)}}
.seg-btn.is-active{{background:var(--accent);color:#fff}}
.seg-btn:first-child.is-active{{background:var(--accent)}}
.code-wrap[data-show="before"] .seg-btn:first-child{{}}
.code{{margin:0;background:var(--code-bg);color:var(--code-fg);border-radius:12px;padding:18px 20px;overflow-x:auto;font-family:var(--mono);font-size:12.5px;line-height:1.7;tab-size:2;white-space:pre}}
.code-side[data-code="before"] .code{{box-shadow:inset 4px 0 0 var(--before)}}
.code-side[data-code="after"] .code{{box-shadow:inset 4px 0 0 var(--accent)}}

/* tooltip */
#tip{{position:fixed;z-index:60;max-width:320px;background:var(--ink);color:#EAF1EE;font-size:13px;line-height:1.5;padding:11px 14px;border-radius:10px;box-shadow:0 12px 34px -12px rgba(0,0,0,.5);pointer-events:none;opacity:0;transform:translateY(4px);transition:opacity .12s,transform .12s}}
#tip.show{{opacity:1;transform:none}}
#tip .tn{{font-family:var(--mono);font-size:11px;color:#7FD9C8;display:block;margin-bottom:3px}}

footer{{border-top:1px solid var(--line);margin-top:40px;padding:26px 0 60px;color:var(--ink-soft);font-size:13px}}
footer .grid2{{margin-top:8px}}
footer b{{color:var(--ink)}}
@media (max-width:760px){{.grid2{{grid-template-columns:1fr}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
</style>

<div class="top"><div class="wrap">
  <div class="kicker">SUNAT · Programa de Libros Electrónicos (PLE)</div>
  <h1>Libro 3 — Inventarios y Balances</h1>
  <p class="lede">Cinco formatos del procedimiento <code>Ct_Pro_PLE</code> (BD <code>CodeplexWeb_2020</code>): implementación, comparación antes / después y campos de salida documentados. Cada rama genera el archivo oficial en palotes y su equivalente en Excel para revisión.</p>
  <div class="status">
    <span class="pill ok"><span class="dot"></span>Probado en SQL Server · todas las aserciones OK</span>
    <span class="pill ok"><span class="dot"></span>Cambio quirúrgico · diff verificado</span>
    <span class="pill"><span class="dot" style="background:var(--warn)"></span>4 puntos de negocio por confirmar</span>
  </div>
  <div class="downloads">{downloads}</div>
</div></div>

<div class="wrap">
  <div class="section-lead"><h2>Cómo funciona</h2></div>
  <div class="overview">
    <div class="ov"><h4>Salida dual</h4><p><span class="k">@exportar_excel=0</span> → TXT en palotes (oficial SUNAT). <span class="k">=1</span> → Excel con columnas <span class="k">(NN)</span> para revisar.</p></div>
    <div class="ov"><h4>Patrón</h4><p>Tabla temporal por rama + <span class="k">if/else</span>, siguiendo el modelo ya validado de <span class="k">030700</span>. Temporales por sesión = seguros en concurrencia.</p></div>
    <div class="ov"><h4>Criterio senior</h4><p>Predicados SARGables (<span class="k">like '30%'</span>), signo correcto en pasivos, <span class="k">ISNULL</span> en sumas, estado 1/8/9, saneo de CR/LF/TAB, solo lectura.</p></div>
    <div class="ov"><h4>Periodo &amp; estado</h4><p>Periodo en <span class="k">AAAAMMDD</span> (día 00). Estado: 1 del periodo · 8 anterior no anotada · 9 anterior anotada.</p></div>
  </div>
</div>

<div class="tabbar"><div class="wrap"><div class="tabs" role="tablist">{tabs}</div></div></div>

<div class="wrap">{sections}</div>

<div class="wrap"><footer>
  <div class="section-lead" style="padding-top:6px"><h2 style="font-size:20px">Verificación</h2></div>
  <div class="grid2">
    <div><b>Probado, correcto y seguro para producción.</b> Ejecución real en SQL Server (LocalDB) con datos de casos borde: conteo de campos por formato, signos, fechas DD/MM/AAAA, periodo AAAAMMDD, <code>SUM</code> por asiento, estado nulo→1 y 8 preservado, exclusión de ruido, y razón social con CR/LF/TAB que no parte el registro. Todo el procedimiento pasa <code>SET PARSEONLY</code> y el diff confirma que sólo cambiaron estas 5 ramas.</div>
    <div><b>Pendiente de negocio (no son bugs).</b> 3.8: título/valor nominal/cantidad/provisión sin fuente en el sistema. 3.9: fuente real de la amortización acumulada. 3.11–3.13: confirmar que el Libro Diario es la fuente correcta (vs. cuentas corrientes). 3.13: contraparte proveedor/cliente/auxiliar. Y validar un periodo real contra el validador PLE de SUNAT.</div>
  </div>
</footer></div>

<div id="tip" role="tooltip"></div>

<script>
(function(){{
  const tabs=[...document.querySelectorAll('.tab')];
  const secs=[...document.querySelectorAll('.fmt')];
  function show(acc){{
    secs.forEach(s=>s.hidden = s.dataset.acc!==acc);
    tabs.forEach(t=>t.classList.toggle('is-active', t.dataset.target===acc));
  }}
  tabs.forEach(t=>t.addEventListener('click',()=>show(t.dataset.target)));
  show(tabs[0].dataset.target);

  // before/after toggle (por seccion)
  document.querySelectorAll('.diff').forEach(diff=>{{
    const btns=[...diff.querySelectorAll('.seg-btn')];
    const sides=[...diff.querySelectorAll('.code-side')];
    btns.forEach(b=>b.addEventListener('click',()=>{{
      const code=b.dataset.code;
      btns.forEach(x=>{{const on=x===b;x.classList.toggle('is-active',on);x.setAttribute('aria-pressed',on)}});
      sides.forEach(s=>s.hidden = s.dataset.code!==code);
      diff.querySelector('.code-wrap').dataset.show=code;
    }}));
  }});

  // tooltip
  const tip=document.getElementById('tip');
  let cur=null;
  function place(el){{
    const r=el.getBoundingClientRect();
    tip.style.left='0px';tip.style.top='0px';
    const tr=tip.getBoundingClientRect();
    let x=r.left+r.width/2-tr.width/2;
    x=Math.max(10,Math.min(x,innerWidth-tr.width-10));
    let y=r.top-tr.height-9;
    if(y<8) y=r.bottom+9;
    tip.style.left=x+'px';tip.style.top=y+'px';
  }}
  function open(el){{
    const num=el.dataset.num?('<span class="tn">Campo '+el.dataset.num+'</span>'):'';
    tip.innerHTML=num+el.dataset.tip;
    tip.classList.add('show');place(el);cur=el;
  }}
  function close(){{tip.classList.remove('show');cur=null;}}
  document.addEventListener('mouseover',e=>{{const c=e.target.closest('[data-tip]');if(c&&c!==cur)open(c);}});
  document.addEventListener('mouseout',e=>{{const c=e.target.closest('[data-tip]');if(c&&!c.contains(e.relatedTarget))close();}});
  document.addEventListener('focusin',e=>{{const c=e.target.closest('[data-tip]');if(c)open(c);}});
  document.addEventListener('focusout',close);
  addEventListener('scroll',()=>{{if(cur)place(cur);}},true);
}})();
</script>'''

io.open(OUT,"w",encoding="utf-8").write(HTML)
print("HTML escrito:",OUT,len(HTML),"chars")
