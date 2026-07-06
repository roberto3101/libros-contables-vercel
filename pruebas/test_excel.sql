SET NOCOUNT ON;
USE PLE_TEST;
GO
PRINT '=== EXCEL 030800 ===';
DECLARE @idempresa varchar(100)='1-TEST';
DECLARE @periodo varchar(6)='202606';
if object_id('tempdb..#inv_balances_030800') is not null drop table #inv_balances_030800;
select periodo_tributario,codigo_unico_operacion,correlativo_asiento_contable,tipo_documento_identidad_emisor,numero_documento_identidad_emisor,razon_social_emisor,codigo_tipo_titulo,valor_nominal_unitario_titulo,cantidad_titulos,costo_total_titulos_en_libros,provision_total_titulos_en_libros,estado_operacion,campo_libre_utilizacion
into #inv_balances_030800
from (	select d.periodo+'00' as periodo_tributario,
				d.cuo as codigo_unico_operacion,
				d.amc as correlativo_asiento_contable,
				ISNULL(c.idtipodocidentidad,'0') as tipo_documento_identidad_emisor,
				ISNULL(c.rucdni,'0') as numero_documento_identidad_emisor,
				REPLACE(REPLACE(REPLACE(left(ISNULL(c.razonsocial,''),100),CHAR(9),''),CHAR(10),''),CHAR(13),'') as razon_social_emisor,
				'00' as codigo_tipo_titulo,   --TODO campo 7 (Tabla 15): el sistema no almacena el tipo de titulo
				convert(decimal(18,2),0) as valor_nominal_unitario_titulo,   --TODO campo 8: sin fuente de valor nominal unitario
				0 as cantidad_titulos,   --TODO campo 9: sin fuente de cantidad de titulos
				convert(decimal(18,2),ISNULL(SUM(d.debe_mna-d.haber_mna),0)) as costo_total_titulos_en_libros,
				convert(decimal(18,2),0) as provision_total_titulos_en_libros,   --TODO campo 11: sin fuente de provision (negativo o 0.00)
				case when isnull(d.estado_sunat,0) in (1,8,9) then d.estado_sunat else 1 end as estado_operacion,
				'' as campo_libre_utilizacion
			from ct_diarios d left join zg_auxiliares c on c.idempresa=d.idempresa and c.rucdni=d.rucdni_auxiliares
			where d.idempresa=@idempresa and d.idaniopro=left(@periodo,4) and d.periodo=@periodo and d.idcuenta like '30%'
			group by d.periodo,d.cuo,d.amc,c.idtipodocidentidad,c.rucdni,c.razonsocial,d.estado_sunat
		) t
select periodo_tributario as [(01) PERIODO TRIBUTARIO],
				codigo_unico_operacion as [(02) CODIGO UNICO OPERACION],
				correlativo_asiento_contable as [(03) CORRELATIVO ASIENTO CONTABLE],
				tipo_documento_identidad_emisor as [(04) TIPO DOCUMENTO IDENTIDAD EMISOR],
				numero_documento_identidad_emisor as [(05) NUMERO DOCUMENTO IDENTIDAD EMISOR],
				razon_social_emisor as [(06) RAZON SOCIAL EMISOR],
				codigo_tipo_titulo as [(07) CODIGO TIPO TITULO],
				valor_nominal_unitario_titulo as [(08) VALOR NOMINAL UNITARIO TITULO],
				cantidad_titulos as [(09) CANTIDAD TITULOS],
				costo_total_titulos_en_libros as [(10) COSTO TOTAL TITULOS EN LIBROS],
				provision_total_titulos_en_libros as [(11) PROVISION TOTAL TITULOS EN LIBROS],
				estado_operacion as [(12) ESTADO OPERACION],
				campo_libre_utilizacion as [(13) CAMPO LIBRE UTILIZACION] from #inv_balances_030800 order by codigo_unico_operacion, correlativo_asiento_contable;
GO

PRINT '=== EXCEL 030900 ===';
DECLARE @idempresa varchar(100)='1-TEST';
DECLARE @periodo varchar(6)='202606';
if object_id('tempdb..#inv_balances_030900') is not null drop table #inv_balances_030900;
select periodo_tributario,codigo_unico_operacion,correlativo_asiento_contable,fecha_inicio_operacion,codigo_cuenta_contable,descripcion_intangible,valor_contable_intangible,amortizacion_contable_acumulada,estado_operacion,campo_libre_utilizacion
into #inv_balances_030900
from (	select d.periodo+'00' as periodo_tributario,
				d.cuo as codigo_unico_operacion,
				d.amc as correlativo_asiento_contable,
				convert(varchar,d.fecha_contable,103) as fecha_inicio_operacion,
				d.idcuenta as codigo_cuenta_contable,
				REPLACE(REPLACE(REPLACE(left(af.descripcion,40),CHAR(9),''),CHAR(10),''),CHAR(13),'') as descripcion_intangible,
				convert(decimal(18,2),af.valor_activo_mna) as valor_contable_intangible,
				convert(decimal(18,2),0) as amortizacion_contable_acumulada,   --TODO campo 8 amortizacion acum (negativo o 0.00): confirmar fuente (cta 39 / campo en ct_activo_fijo)
				case when isnull(d.estado_sunat,0) in (1,8,9) then d.estado_sunat else 1 end as estado_operacion,
				'' as campo_libre_utilizacion
			from ct_diarios d inner join ct_activo_fijo af on d.idempresa=af.idempresa and d.idactivofijo=af.idactivofijo and d.idaniopro=af.idaniopro
			where d.idempresa=@idempresa and d.idaniopro=left(@periodo,4) and d.periodo=@periodo and d.idcuenta like '34%'
			group by d.periodo,d.cuo,d.amc,d.fecha_contable,d.idcuenta,af.descripcion,af.valor_activo_mna,d.estado_sunat
		) t
select periodo_tributario as [(01) PERIODO TRIBUTARIO],
				codigo_unico_operacion as [(02) CODIGO UNICO OPERACION],
				correlativo_asiento_contable as [(03) CORRELATIVO ASIENTO CONTABLE],
				fecha_inicio_operacion as [(04) FECHA INICIO OPERACION],
				codigo_cuenta_contable as [(05) CODIGO CUENTA CONTABLE],
				descripcion_intangible as [(06) DESCRIPCION INTANGIBLE],
				valor_contable_intangible as [(07) VALOR CONTABLE INTANGIBLE],
				amortizacion_contable_acumulada as [(08) AMORTIZACION CONTABLE ACUMULADA],
				estado_operacion as [(09) ESTADO OPERACION],
				campo_libre_utilizacion as [(10) CAMPO LIBRE UTILIZACION] from #inv_balances_030900 order by codigo_unico_operacion, correlativo_asiento_contable, codigo_cuenta_contable;
GO

PRINT '=== EXCEL 031100 ===';
DECLARE @idempresa varchar(100)='1-TEST';
DECLARE @periodo varchar(6)='202606';
if object_id('tempdb..#inv_balances_031100') is not null drop table #inv_balances_031100;
select periodo_tributario,codigo_unico_operacion,correlativo_asiento_contable,codigo_cuenta_contable,tipo_documento_identidad_trabajador,numero_documento_identidad_trabajador,codigo_trabajador,apellidos_nombres_trabajador,saldo_final_por_pagar,estado_operacion,campo_libre_utilizacion
into #inv_balances_031100
from (	select d.periodo+'00' as periodo_tributario,
				d.cuo as codigo_unico_operacion,
				d.amc as correlativo_asiento_contable,
				d.idcuenta as codigo_cuenta_contable,
				ax.idtipodocidentidad as tipo_documento_identidad_trabajador,
				ax.rucdni as numero_documento_identidad_trabajador,
				ax.codigo as codigo_trabajador,
				REPLACE(REPLACE(REPLACE(left(ax.razonsocial,100),CHAR(9),''),CHAR(10),''),CHAR(13),'') as apellidos_nombres_trabajador,
				convert(decimal(18,2),ISNULL(SUM(d.haber_mna-d.debe_mna),0)) as saldo_final_por_pagar,
				case when isnull(d.estado_sunat,0) in (1,8,9) then d.estado_sunat else 1 end as estado_operacion,
				'' as campo_libre_utilizacion
			from ct_diarios d inner join zg_auxiliares ax on d.idempresa=ax.idempresa and d.rucdni_auxiliares=ax.rucdni
			where d.idempresa=@idempresa and d.idaniopro=left(@periodo,4) and d.periodo=@periodo and d.idcuenta like '41%'
			group by d.periodo,d.cuo,d.amc,d.idcuenta,ax.idtipodocidentidad,ax.rucdni,ax.codigo,ax.razonsocial,d.estado_sunat
		) t
select periodo_tributario as [(01) PERIODO TRIBUTARIO],
				codigo_unico_operacion as [(02) CODIGO UNICO OPERACION],
				correlativo_asiento_contable as [(03) CORRELATIVO ASIENTO CONTABLE],
				codigo_cuenta_contable as [(04) CODIGO CUENTA CONTABLE],
				tipo_documento_identidad_trabajador as [(05) TIPO DOCUMENTO IDENTIDAD TRABAJADOR],
				numero_documento_identidad_trabajador as [(06) NUMERO DOCUMENTO IDENTIDAD TRABAJADOR],
				codigo_trabajador as [(07) CODIGO TRABAJADOR],
				apellidos_nombres_trabajador as [(08) APELLIDOS NOMBRES TRABAJADOR],
				saldo_final_por_pagar as [(09) SALDO FINAL POR PAGAR],
				estado_operacion as [(10) ESTADO OPERACION],
				campo_libre_utilizacion as [(11) CAMPO LIBRE UTILIZACION] from #inv_balances_031100 order by codigo_unico_operacion, correlativo_asiento_contable, codigo_cuenta_contable;
GO

PRINT '=== EXCEL 031200 ===';
DECLARE @idempresa varchar(100)='1-TEST';
DECLARE @periodo varchar(6)='202606';
if object_id('tempdb..#inv_balances_031200') is not null drop table #inv_balances_031200;
select periodo_tributario,codigo_unico_operacion,correlativo_asiento_contable,tipo_documento_identidad_proveedor,numero_documento_identidad_proveedor,fecha_emision_comprobante,razon_social_proveedor,monto_cuenta_por_pagar,estado_operacion,campo_libre_utilizacion
into #inv_balances_031200
from (	select d.periodo+'00' as periodo_tributario,
				d.cuo as codigo_unico_operacion,
				d.amc as correlativo_asiento_contable,
				ax.idtipodocidentidad as tipo_documento_identidad_proveedor,
				ax.rucdni as numero_documento_identidad_proveedor,
				convert(varchar,d.fecha_contable,103) as fecha_emision_comprobante,
				REPLACE(REPLACE(REPLACE(left(ax.razonsocial,100),CHAR(9),''),CHAR(10),''),CHAR(13),'') as razon_social_proveedor,
				convert(decimal(18,2),ISNULL(SUM(d.haber_mna-d.debe_mna),0)) as monto_cuenta_por_pagar,
				case when isnull(d.estado_sunat,0) in (1,8,9) then d.estado_sunat else 1 end as estado_operacion,
				'' as campo_libre_utilizacion
			from ct_diarios d inner join zg_proveedores ax on d.idempresa=ax.idempresa and d.rucdni_proveedores=ax.rucdni
			where d.idempresa=@idempresa and d.idaniopro=left(@periodo,4) and d.periodo=@periodo and (d.idcuenta like '42%' or d.idcuenta like '43%')
			group by d.periodo,d.cuo,d.amc,ax.idtipodocidentidad,ax.rucdni,d.fecha_contable,ax.razonsocial,d.estado_sunat
		) t
select periodo_tributario as [(01) PERIODO TRIBUTARIO],
				codigo_unico_operacion as [(02) CODIGO UNICO OPERACION],
				correlativo_asiento_contable as [(03) CORRELATIVO ASIENTO CONTABLE],
				tipo_documento_identidad_proveedor as [(04) TIPO DOCUMENTO IDENTIDAD PROVEEDOR],
				numero_documento_identidad_proveedor as [(05) NUMERO DOCUMENTO IDENTIDAD PROVEEDOR],
				fecha_emision_comprobante as [(06) FECHA EMISION COMPROBANTE],
				razon_social_proveedor as [(07) RAZON SOCIAL PROVEEDOR],
				monto_cuenta_por_pagar as [(08) MONTO CUENTA POR PAGAR],
				estado_operacion as [(09) ESTADO OPERACION],
				campo_libre_utilizacion as [(10) CAMPO LIBRE UTILIZACION] from #inv_balances_031200 order by codigo_unico_operacion, correlativo_asiento_contable;
GO

PRINT '=== EXCEL 031300 ===';
DECLARE @idempresa varchar(100)='1-TEST';
DECLARE @periodo varchar(6)='202606';
if object_id('tempdb..#inv_balances_031300') is not null drop table #inv_balances_031300;
select periodo_tributario,codigo_unico_operacion,correlativo_asiento_contable,tipo_documento_identidad_tercero,numero_documento_identidad_tercero,fecha_emision_comprobante,apellidos_nombres_tercero,codigo_cuenta_contable,monto_pendiente_pago_tercero,estado_operacion,campo_libre_utilizacion
into #inv_balances_031300
from (	select d.periodo+'00' as periodo_tributario,
				d.cuo as codigo_unico_operacion,
				d.amc as correlativo_asiento_contable,
				ax.idtipodocidentidad as tipo_documento_identidad_tercero,
				ax.rucdni as numero_documento_identidad_tercero,
				convert(varchar,d.fecha_contable,103) as fecha_emision_comprobante,
				REPLACE(REPLACE(REPLACE(left(ax.razonsocial,100),CHAR(9),''),CHAR(10),''),CHAR(13),'') as apellidos_nombres_tercero,
				d.idcuenta as codigo_cuenta_contable,
				convert(decimal(18,2),ISNULL(SUM(d.haber_mna-d.debe_mna),0)) as monto_pendiente_pago_tercero,
				case when isnull(d.estado_sunat,0) in (1,8,9) then d.estado_sunat else 1 end as estado_operacion,
				'' as campo_libre_utilizacion
			from ct_diarios d inner join zg_proveedores ax on d.idempresa=ax.idempresa and d.rucdni_proveedores=ax.rucdni
			where d.idempresa=@idempresa and d.idaniopro=left(@periodo,4) and d.periodo=@periodo and (d.idcuenta like '46%' or d.idcuenta like '47%')
			group by d.periodo,d.cuo,d.amc,ax.idtipodocidentidad,ax.rucdni,d.fecha_contable,ax.razonsocial,d.idcuenta,d.estado_sunat
		) t
select periodo_tributario as [(01) PERIODO TRIBUTARIO],
				codigo_unico_operacion as [(02) CODIGO UNICO OPERACION],
				correlativo_asiento_contable as [(03) CORRELATIVO ASIENTO CONTABLE],
				tipo_documento_identidad_tercero as [(04) TIPO DOCUMENTO IDENTIDAD TERCERO],
				numero_documento_identidad_tercero as [(05) NUMERO DOCUMENTO IDENTIDAD TERCERO],
				fecha_emision_comprobante as [(06) FECHA EMISION COMPROBANTE],
				apellidos_nombres_tercero as [(07) APELLIDOS NOMBRES TERCERO],
				codigo_cuenta_contable as [(08) CODIGO CUENTA CONTABLE],
				monto_pendiente_pago_tercero as [(09) MONTO PENDIENTE PAGO TERCERO],
				estado_operacion as [(10) ESTADO OPERACION],
				campo_libre_utilizacion as [(11) CAMPO LIBRE UTILIZACION] from #inv_balances_031300 order by codigo_unico_operacion, correlativo_asiento_contable, codigo_cuenta_contable;
GO

