# -*- coding: utf-8 -*-
import re, io
p=r"C:/Users/user/AppData/Local/Temp/claude/C--Users-user-Desktop-libros-contables/00d8bcd0-b8c0-4bcc-a6f3-485232b243a8/scratchpad/out.txt"
lines=[l.rstrip("\n") for l in io.open(p,encoding="utf-8") if "|" in l]
ok=True
def check(cond,msg):
    global ok
    print(("  OK  " if cond else "FALLO ")+msg); ok = ok and cond

DDMMYYYY=re.compile(r"^\d{2}/\d{2}/\d{4}$")
def f(line): return line.split("|")

# clasifica por CUO
by={}
for l in lines:
    by.setdefault(f(l)[1][:5], []).append(f(l))

print("== Integridad de registros ==")
check(len(lines)==7,"exactamente 7 lineas TXT (razon social con CR/LF/TAB no partio el registro)")
check(all(("PROVEEDOR" not in x) or ("PROVEEDORCOMERCIALSAC" in x.replace(' ','') or "PROVEEDOR COMERCIAL" in x) for x in lines),"razon social sucia limpiada")

print("== 3.8 cuenta 30 ==")
r=by["AS-30"][0]
check(len(r)==12,"12 campos (obligatorios, sin campo libre)")
check(len(r[0])==8 and r[0]=="20260600","periodo AAAAMMDD = 20260600")
check(r[9]=="4000.00","costo_total = SUM(5000-1000)=4000.00")
check(r[11] in ("1","8","9"),"estado valido")

print("== 3.9 cuenta 34 ==")
r=by["AS-34"][0]
check(len(r)==9,"9 campos")
check(bool(DDMMYYYY.match(r[3])),"fecha inicio DD/MM/AAAA = "+r[3])
check(r[6]=="12000.00","valor contable 12000.00")
check(r[7]=="0.00","amortizacion 0.00 (TODO fuente)")

print("== 3.11 cuenta 41 ==")
r=by["AS-41"][0]
check(len(r)==10,"10 campos")
check(float(r[8])>0 and r[8]=="3000.00","saldo POSITIVO (haber-debe)=3000.00")
check(r[9]=="1","estado NULL -> default 1")

print("== 3.12 cuentas 42/43 ==")
rows=by["AS-42"]+by["AS-43"]
check(len(rows)==2,"incluye 42 y 43 (2 filas)")
for r in rows: check(len(r)==9,"9 campos ("+r[1]+")")
check(any(r[8] and float(r[8])>0 for r in rows),"montos positivos")
check(any(r[7]=="8000.00" and r[8]=="8" for r in rows),"estado 8 preservado en la 42")

print("== 3.13 cuentas 46/47 ==")
rows=by["AS-46"]+by["AS-47"]
check(len(rows)==2,"incluye 46 y 47 (2 filas)")
for r in rows: check(len(r)==10,"10 campos ("+r[1]+")")

print("== Ruido excluido ==")
blob="\n".join(lines)
check("AS-40-01" not in blob,"cuenta 40 (fuera de rango) NO aparece")
check("7777" not in blob and "AS-42-05" not in blob,"periodo 202605 NO aparece")

print("\nRESULTADO:", "TODO OK" if ok else "HUBO FALLOS")
