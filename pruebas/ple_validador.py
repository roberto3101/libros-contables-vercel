# -*- coding: utf-8 -*-
"""
Validador estructural PLE (replica las reglas del validador oficial de SUNAT para el
Libro de Inventarios y Balances, formatos 3.8/3.9/3.11/3.12/3.13).
Verifica: nomenclatura del nombre de archivo + estructura de cada registro (campos,
formatos, tablas, longitudes, caracteres prohibidos). Fuente: Estructura del PLE + Anexo 3.
NO es el binario de SUNAT; reproduce sus reglas de forma auditable.
"""
import re, io, sys, glob, os

# ---- catalogos ----
T2 = {'0','1','4','6','7','A'}                       # Tabla 2: tipo de documento de identidad
DOC = {'0':(15,'A','V'),'1':(8,'N','F'),'4':(12,'A','V'),'6':(11,'N','F'),'7':(12,'A','V'),'A':(15,'N','F')}  # (longitud, tipo, F/V)
T15 = {'01','02','03','04','05','06','07','08','09','10','99','00'}  # Tabla 15 tipo de titulo
ESTADOS = {'0','1','2','8','9'}
FORBID = ('|','/','\\')

DEC   = re.compile(r'^-?\d{1,12}\.\d{2}$')
INT12 = re.compile(r'^\d{1,12}$')
DATE  = re.compile(r'^(\d{2})/(\d{2})/(\d{4})$')
PERI  = re.compile(r'^\d{8}$')
AMC   = re.compile(r'^[AMC].{1,9}$')
CUENTA= re.compile(r'^\d{2,24}$')
FNAME = re.compile(r'^LE\d{11}\d{4}\d{2}\d{2}\d{6}\d{2}[012][01][12]1\.TXT$')

def periodo_ok(s):
    if not PERI.match(s): return False
    mm=int(s[4:6]); return 0<=mm<=12
def date_ok(s):
    m=DATE.match(s)
    if not m: return False
    d,mo,y=map(int,m.groups()); return 1<=d<=31 and 1<=mo<=12 and 1900<y<2100
def texto_ok(s,mx): return len(s)<=mx and not any(c in s for c in FORBID) and not any(c in s for c in '\t\r\n')

# ---- especificacion de campos por formato: (nombre, tipo[, arg]) ----
# tipos: PERIODO CUO AMC TIPODOC NUMDOC TEXTO FECHA DEC INT T15 CUENTA ESTADO
SPEC = {
 '030800': [('Periodo tributario','PERIODO'),('Codigo unico de operacion','CUO'),('Correlativo del asiento','AMC'),
   ('Tipo doc. emisor','TIPODOC'),('Numero doc. emisor','NUMDOC'),('Razon social emisor','TEXTO',100),
   ('Codigo tipo de titulo','T15'),('Valor nominal unitario','DEC'),('Cantidad de titulos','INT'),
   ('Costo total en libros','DEC'),('Provision total en libros','DEC'),('Estado de operacion','ESTADO')],
 '030900': [('Periodo tributario','PERIODO'),('Codigo unico de operacion','CUO'),('Correlativo del asiento','AMC'),
   ('Fecha inicio de operacion','FECHA'),('Codigo cuenta contable','CUENTA'),('Descripcion del intangible','TEXTO',40),
   ('Valor contable del intangible','DEC'),('Amortizacion contable acumulada','DEC'),('Estado de operacion','ESTADO')],
 '031100': [('Periodo tributario','PERIODO'),('Codigo unico de operacion','CUO'),('Correlativo del asiento','AMC'),
   ('Codigo cuenta contable','CUENTA'),('Tipo doc. trabajador','TIPODOC'),('Numero doc. trabajador','NUMDOC'),
   ('Codigo del trabajador','TEXTO',11),('Apellidos y nombres del trabajador','TEXTO',100),
   ('Saldo final por pagar','DEC'),('Estado de operacion','ESTADO')],
 '031200': [('Periodo tributario','PERIODO'),('Codigo unico de operacion','CUO'),('Correlativo del asiento','AMC'),
   ('Tipo doc. proveedor','TIPODOC'),('Numero doc. proveedor','NUMDOC'),('Fecha de emision','FECHA'),
   ('Razon social proveedor','TEXTO',100),('Monto de cuenta por pagar','DEC'),('Estado de operacion','ESTADO')],
 '031300': [('Periodo tributario','PERIODO'),('Codigo unico de operacion','CUO'),('Correlativo del asiento','AMC'),
   ('Tipo doc. tercero','TIPODOC'),('Numero doc. tercero','NUMDOC'),('Fecha de emision','FECHA'),
   ('Apellidos y nombres del tercero','TEXTO',100),('Codigo cuenta contable','CUENTA'),
   ('Monto pendiente de pago','DEC'),('Estado de operacion','ESTADO')],
}

def check_field(kind, val, arg, prev_tipo):
    if kind=='PERIODO': return periodo_ok(val), "formato AAAAMMDD (MM 00-12)"
    if kind=='CUO':     return (0<len(val)<=40 and texto_ok(val,40)), "1..40, sin | / \\"
    if kind=='AMC':     return bool(AMC.match(val)), "2..10, primer caracter A/M/C"
    if kind=='TIPODOC': return val in T2, "Tabla 2 (0,1,4,6,7,A)"
    if kind=='NUMDOC':
        if val in ('0','00',''): return True,""                           # 'no existe' permitido
        if prev_tipo not in DOC: return False,"tipo de doc invalido"
        ln,t,fx=DOC[prev_tipo]
        if t=='N' and not val.isdigit(): return False,"debe ser numerico"
        if fx=='F' and len(val)!=ln: return False,f"longitud fija {ln} para el tipo"
        if fx=='V' and len(val)>ln:  return False,f"longitud <= {ln}"
        return True,""
    if kind=='TEXTO':   return texto_ok(val,arg), f"texto <= {arg}, sin | / \\ ni saltos"
    if kind=='FECHA':   return date_ok(val), "DD/MM/AAAA valida"
    if kind=='DEC':     return bool(DEC.match(val)), "hasta 12 enteros y 2 decimales, sin miles"
    if kind=='INT':     return bool(INT12.match(val)), "entero hasta 12 digitos"
    if kind=='T15':     return val in T15, "Tabla 15 (00..10,99)"
    if kind=='CUENTA':  return bool(CUENTA.match(val)), "cuenta contable 2..24 digitos"
    if kind=='ESTADO':  return val in ESTADOS, "0,1,2,8,9"
    return False,"tipo desconocido"

def validate_file(path):
    fname=os.path.basename(path)
    errs=[]; rows=0
    # 1) nombre
    name_ok = bool(FNAME.match(fname.upper()))
    # codigo de libro dentro del nombre (pos 22-27, 0-based 21:27)
    code = fname[21:27] if len(fname)>=27 else '??????'
    spec = SPEC.get(code)
    if not name_ok: errs.append(("NOMBRE", fname, f"no cumple la mascara LE+RUC+AAAAMMDD+codigo+CC+O+I+M+G.TXT"))
    if spec is None: errs.append(("NOMBRE", fname, f"codigo de libro '{code}' no reconocido"));
    # 2) registros
    lines=[l.rstrip('\r\n') for l in io.open(path,encoding='utf-8') if l.strip()!='']
    for li,line in enumerate(lines,1):
        rows+=1
        f=line.split('|')
        if spec is None: break
        if len(f)!=len(spec):
            errs.append((f"L{li}","conteo",f"{len(f)} campos, se esperaban {len(spec)}")); continue
        prev_tipo=None
        for idx,(campo) in enumerate(spec):
            name=campo[0]; kind=campo[1]; arg=campo[2] if len(campo)>2 else None
            ok,rule=check_field(kind,f[idx],arg,prev_tipo)
            if kind=='TIPODOC': prev_tipo=f[idx]
            if not ok:
                errs.append((f"L{li}",f"c{idx+1} {name}",f"valor='{f[idx]}' viola: {rule}"))
    return name_ok and spec is not None, rows, errs

def main():
    files=sorted(glob.glob(sys.argv[1]))
    total_err=0
    print("="*74)
    print("VALIDADOR ESTRUCTURAL PLE  ·  Libro 3 (3.8/3.9/3.11/3.12/3.13)")
    print("="*74)
    for p in files:
        ok,rows,errs=validate_file(p)
        estado = "VALIDO" if (ok and not errs) else "RECHAZADO"
        print(f"\n[{estado}]  {os.path.basename(p)}   ({rows} registro/s)")
        if errs:
            total_err+=len(errs)
            for where,campo,msg in errs[:20]:
                print(f"    - {where} · {campo}: {msg}")
        else:
            print("    sin observaciones")
    print("\n"+"-"*74)
    print("RESULTADO:", "TODOS LOS ARCHIVOS VALIDOS" if total_err==0 else f"{total_err} observacion/es")
    return 0 if total_err==0 else 1

if __name__=='__main__':
    sys.exit(main())
