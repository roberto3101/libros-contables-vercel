# -*- coding: utf-8 -*-
# Fuente unica: genera las 5 ramas del SP (3.8/3.9/3.11/3.12/3.13) y un script de prueba identico.
# Alias de salida en LENGUAJE UBICUO (espanol, sin abreviaturas).
# Columnas/tablas existentes de Codeplex2020 se leen TAL CUAL (no se renombran).
import io

SP_PATH   = r"C:/Users/user/Desktop/libros-contables/Ct_Pro_PLE_20260701.sql"
TEST_PATH = r"C:/Users/user/AppData/Local/Temp/claude/C--Users-user-Desktop-libros-contables/00d8bcd0-b8c0-4bcc-a6f3-485232b243a8/scratchpad/test_bodies.sql"

T = "\t"
ESTADO = "case when isnull(d.estado_sunat,0) in (1,8,9) then d.estado_sunat else 1 end"

def clean(expr, n):
    # quita TAB/CR/LF que romperian el TXT en palotes y recorta al maximo del layout
    return "REPLACE(REPLACE(REPLACE(left(%s,%d),CHAR(9),''),CHAR(10),''),CHAR(13),'')" % (expr, n)

def build(temp, pairs, frm, where, group, order_cols):
    # pairs: (expr_fuente, alias_ubicuo[, comentario])
    cols=[p[1] for p in pairs]
    b=["select "+",".join(cols), "into "+temp]
    inner=[]
    for i,p in enumerate(pairs):
        seg=p[0]+" as "+p[1]
        seg+= "," if i<len(pairs)-1 else ""
        if len(p)>2: seg+= "   --"+p[2]
        inner.append(seg)
    b.append("from (\tselect "+inner[0])
    for x in inner[1:]: b.append(T*4+x)
    b.append(T*3+"from "+frm)
    b.append(T*3+"where "+where)
    b.append(T*3+"group by "+group)
    b.append(T*2+") t")
    txt_cols=[c for c in cols if c!="campo_libre_utilizacion"]  # TXT: campos libres no usados no llevan dato ni palote
    txt="concat("+",'|',".join(txt_cols)+")"
    xls="select "+(",\n"+T*4).join("%s as [(%02d) %s]"%(cols[i], i+1, cols[i].replace('_',' ').upper()) for i in range(len(cols)))
    order="order by "+", ".join(order_cols)
    return b,temp,txt,xls,order

WHERE="d.idempresa=@idempresa and d.idaniopro=left(@periodo,4) and d.periodo=@periodo and "

def body_030800():
    return build("#inv_balances_030800",[
      ("d.periodo+'00'","periodo_tributario"),
      ("d.cuo","codigo_unico_operacion"),
      ("d.amc","correlativo_asiento_contable"),
      ("ISNULL(c.idtipodocidentidad,'0')","tipo_documento_identidad_emisor"),
      ("ISNULL(c.rucdni,'0')","numero_documento_identidad_emisor"),
      (clean("ISNULL(c.razonsocial,'')",100),"razon_social_emisor"),
      ("'00'","codigo_tipo_titulo","TODO campo 7 (Tabla 15): el sistema no almacena el tipo de titulo"),
      ("convert(decimal(18,2),0)","valor_nominal_unitario_titulo","TODO campo 8: sin fuente de valor nominal unitario"),
      ("0","cantidad_titulos","TODO campo 9: sin fuente de cantidad de titulos"),
      ("convert(decimal(18,2),ISNULL(SUM(d.debe_mna-d.haber_mna),0))","costo_total_titulos_en_libros"),
      ("convert(decimal(18,2),0)","provision_total_titulos_en_libros","TODO campo 11: sin fuente de provision (negativo o 0.00)"),
      (ESTADO,"estado_operacion"),
      ("''","campo_libre_utilizacion"),
     ],
     "ct_diarios d left join zg_auxiliares c on c.idempresa=d.idempresa and c.rucdni=d.rucdni_auxiliares",
     WHERE+"d.idcuenta like '30%'",
     "d.periodo,d.cuo,d.amc,c.idtipodocidentidad,c.rucdni,c.razonsocial,d.estado_sunat",
     ["codigo_unico_operacion","correlativo_asiento_contable"])

def body_030900():
    return build("#inv_balances_030900",[
      ("d.periodo+'00'","periodo_tributario"),
      ("d.cuo","codigo_unico_operacion"),
      ("d.amc","correlativo_asiento_contable"),
      ("convert(varchar,d.fecha_contable,103)","fecha_inicio_operacion"),
      ("d.idcuenta","codigo_cuenta_contable"),
      (clean("af.descripcion",40),"descripcion_intangible"),
      ("convert(decimal(18,2),af.valor_activo_mna)","valor_contable_intangible"),
      ("convert(decimal(18,2),0)","amortizacion_contable_acumulada","TODO campo 8 amortizacion acum (negativo o 0.00): confirmar fuente (cta 39 / campo en ct_activo_fijo)"),
      (ESTADO,"estado_operacion"),
      ("''","campo_libre_utilizacion"),
     ],
     "ct_diarios d inner join ct_activo_fijo af on d.idempresa=af.idempresa and d.idactivofijo=af.idactivofijo and d.idaniopro=af.idaniopro",
     WHERE+"d.idcuenta like '34%'",
     "d.periodo,d.cuo,d.amc,d.fecha_contable,d.idcuenta,af.descripcion,af.valor_activo_mna,d.estado_sunat",
     ["codigo_unico_operacion","correlativo_asiento_contable","codigo_cuenta_contable"])

def body_031100():
    return build("#inv_balances_031100",[
      ("d.periodo+'00'","periodo_tributario"),
      ("d.cuo","codigo_unico_operacion"),
      ("d.amc","correlativo_asiento_contable"),
      ("d.idcuenta","codigo_cuenta_contable"),
      ("ax.idtipodocidentidad","tipo_documento_identidad_trabajador"),
      ("ax.rucdni","numero_documento_identidad_trabajador"),
      ("ax.codigo","codigo_trabajador"),
      (clean("ax.razonsocial",100),"apellidos_nombres_trabajador"),
      ("convert(decimal(18,2),ISNULL(SUM(d.haber_mna-d.debe_mna),0))","saldo_final_por_pagar"),
      (ESTADO,"estado_operacion"),
      ("''","campo_libre_utilizacion"),
     ],
     "ct_diarios d inner join zg_auxiliares ax on d.idempresa=ax.idempresa and d.rucdni_auxiliares=ax.rucdni",
     WHERE+"d.idcuenta like '41%'",
     "d.periodo,d.cuo,d.amc,d.idcuenta,ax.idtipodocidentidad,ax.rucdni,ax.codigo,ax.razonsocial,d.estado_sunat",
     ["codigo_unico_operacion","correlativo_asiento_contable","codigo_cuenta_contable"])

def body_031200():
    return build("#inv_balances_031200",[
      ("d.periodo+'00'","periodo_tributario"),
      ("d.cuo","codigo_unico_operacion"),
      ("d.amc","correlativo_asiento_contable"),
      ("ax.idtipodocidentidad","tipo_documento_identidad_proveedor"),
      ("ax.rucdni","numero_documento_identidad_proveedor"),
      ("convert(varchar,d.fecha_contable,103)","fecha_emision_comprobante"),
      (clean("ax.razonsocial",100),"razon_social_proveedor"),
      ("convert(decimal(18,2),ISNULL(SUM(d.haber_mna-d.debe_mna),0))","monto_cuenta_por_pagar"),
      (ESTADO,"estado_operacion"),
      ("''","campo_libre_utilizacion"),
     ],
     "ct_diarios d inner join zg_proveedores ax on d.idempresa=ax.idempresa and d.rucdni_proveedores=ax.rucdni",
     WHERE+"(d.idcuenta like '42%' or d.idcuenta like '43%')",
     "d.periodo,d.cuo,d.amc,ax.idtipodocidentidad,ax.rucdni,d.fecha_contable,ax.razonsocial,d.estado_sunat",
     ["codigo_unico_operacion","correlativo_asiento_contable"])

def body_031300():
    return build("#inv_balances_031300",[
      ("d.periodo+'00'","periodo_tributario"),
      ("d.cuo","codigo_unico_operacion"),
      ("d.amc","correlativo_asiento_contable"),
      ("ax.idtipodocidentidad","tipo_documento_identidad_tercero"),
      ("ax.rucdni","numero_documento_identidad_tercero"),
      ("convert(varchar,d.fecha_contable,103)","fecha_emision_comprobante"),
      (clean("ax.razonsocial",100),"apellidos_nombres_tercero"),
      ("d.idcuenta","codigo_cuenta_contable"),
      ("convert(decimal(18,2),ISNULL(SUM(d.haber_mna-d.debe_mna),0))","monto_pendiente_pago_tercero"),
      (ESTADO,"estado_operacion"),
      ("''","campo_libre_utilizacion"),
     ],
     "ct_diarios d inner join zg_proveedores ax on d.idempresa=ax.idempresa and d.rucdni_proveedores=ax.rucdni",
     WHERE+"(d.idcuenta like '46%' or d.idcuenta like '47%')",
     "d.periodo,d.cuo,d.amc,ax.idtipodocidentidad,ax.rucdni,d.fecha_contable,ax.razonsocial,d.idcuenta,d.estado_sunat",
     ["codigo_unico_operacion","correlativo_asiento_contable","codigo_cuenta_contable"])

FORMATS=[
 ("030800","LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 30 INVERSIONES MOBILIARIAS (3.8)",body_030800),
 ("030900","LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 34 - INTANGIBLES (3.9)",body_030900),
 ("031100","LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LA CUENTA 41 REMUNERACIONES Y PARTICIPACIONES POR PAGAR (3.11)",body_031100),
 ("031200","LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LAS CUENTAS 42 Y 43 CUENTAS POR PAGAR COMERCIALES (3.12)",body_031200),
 ("031300","LIBRO DE INVENTARIOS Y BALANCES - DETALLE DEL SALDO DE LAS CUENTAS 46 Y 47 CUENTAS POR PAGAR DIVERSAS (3.13)",body_031300),
]

def indent(lines, base):
    return "\n".join(base+l for l in lines)

# ---------- 1) Bloque para el SP ----------
sp_block=""
for i,(acc,titulo,fn) in enumerate(FORMATS):
    b,temp,txt,xls,order = fn()
    sp_block += ("" if i==0 else T)+"else If @Accion='%s'  --%s\n" % (acc,titulo)
    sp_block += T*2+"begin\n"
    sp_block += indent(b, T*3)+"\n\n"
    sp_block += T*3+"if @exportar_excel=0\n"
    sp_block += T*4+"select "+txt+" as PLE\n"
    sp_block += T*4+"from "+temp+" "+order+"\n"
    sp_block += T*3+"else\n"
    sp_block += T*4+xls+"\n"
    sp_block += T*4+"from "+temp+" "+order+"\n"
    sp_block += T*2+"end\n"
sp_block += T

sp = io.open(SP_PATH, encoding="utf-16").read()
a = sp.find("else If @Accion='030800'")
z = sp.find("else If @Accion='031400'")
assert a>0 and z>0, "marcadores no encontrados"
sp = sp[:a] + sp_block + sp[z:]
io.open(SP_PATH,"w",encoding="utf-16").write(sp)
print("SP actualizado. Nueva longitud:", len(sp))

# ---------- 2) Script de prueba (mismo body, con params) ----------
test="SET NOCOUNT ON;\nUSE PLE_TEST;\nGO\n"
for acc,titulo,fn in FORMATS:
    b,temp,txt,xls,order = fn()
    test+="-----------------------------------------------------------------\n-- "+titulo+"\n-----------------------------------------------------------------\n"
    test+="DECLARE @idempresa varchar(100)='1-TEST';\nDECLARE @periodo varchar(6)='202606';\nDECLARE @exportar_excel bit=0;\n"
    test+="if object_id('tempdb..%s') is not null drop table %s;\n" % (temp,temp)
    test+=indent(b, "")+"\n\n"
    test+="select "+txt+" as PLE from "+temp+" "+order+";\nGO\n\n"
io.open(TEST_PATH,"w",encoding="utf-8").write(test)
print("Test script escrito.")
