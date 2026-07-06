IF DB_ID('PLE_TEST') IS NOT NULL
BEGIN
    ALTER DATABASE PLE_TEST SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE PLE_TEST;
END
GO
CREATE DATABASE PLE_TEST;
GO
USE PLE_TEST;
GO

CREATE TABLE ct_diarios(
    idempresa varchar(100), idaniopro varchar(4), periodo varchar(6),
    idcuenta varchar(24), cuo varchar(40), amc varchar(10),
    fecha_contable date, debe_mna decimal(18,2), haber_mna decimal(18,2),
    estado_sunat int, rucdni_auxiliares varchar(15), rucdni_proveedores varchar(15),
    rucdni_clientes varchar(15), idactivofijo int
);
CREATE TABLE zg_auxiliares(idempresa varchar(100), rucdni varchar(15), idtipodocidentidad varchar(1), razonsocial varchar(200), codigo varchar(20));
CREATE TABLE zg_proveedores(idempresa varchar(100), rucdni varchar(15), idtipodocidentidad varchar(1), razonsocial varchar(200));
CREATE TABLE ct_activo_fijo(idempresa varchar(100), idactivofijo int, idaniopro varchar(4), descripcion varchar(200), valor_activo_mna decimal(18,2));
GO

-- Maestros
INSERT INTO zg_auxiliares VALUES
 ('1-TEST','20111111111','6','INVERSIONES XYZ SAC','A001'),
 ('1-TEST','10222222','1','JUAN PEREZ LOPEZ','T001');
-- razon social SUCIA: trae TAB + CR + LF embebidos (caso real que rompe el TXT si no se limpia)
INSERT INTO zg_proveedores VALUES
 ('1-TEST','20333333333','6','PROVEEDOR'+CHAR(9)+'COMERCIAL'+CHAR(13)+CHAR(10)+'S/A \ SAC'),
 ('1-TEST','20444444444','6','SERVICIOS DIVERSOS EIRL');
INSERT INTO ct_activo_fijo VALUES
 ('1-TEST',1,'2026','SOFTWARE CONTABLE ERP',12000.00);
GO

-- ============ ct_diarios ============
-- 3.8 cuenta 30: dos lineas mismo CUO (prueba SUM). subdivisionaria 3011 (prueba like '30%'). saldo 5000-1000=4000
INSERT INTO ct_diarios VALUES
 ('1-TEST','2026','202606','3011','AS-30-01','M001','2026-06-02',5000,0,   1,'20111111111',NULL,NULL,NULL),
 ('1-TEST','2026','202606','3011','AS-30-01','M001','2026-06-02',0,1000,   1,'20111111111',NULL,NULL,NULL);
-- 3.9 cuenta 34 intangible
INSERT INTO ct_diarios VALUES
 ('1-TEST','2026','202606','3411','AS-34-01','M002','2026-06-15',12000,0,  1,NULL,NULL,NULL,1);
-- 3.11 cuenta 41: saldo acreedor (haber>debe) => positivo 3000. estado NULL => debe salir '1'
INSERT INTO ct_diarios VALUES
 ('1-TEST','2026','202606','4111','AS-41-01','M003','2026-06-30',0,3000,   NULL,'10222222',NULL,NULL,NULL);
-- 3.12 cuentas 42 y 43: prov 20333. 42 con estado 8 (debe preservarse). 43 incluida.
INSERT INTO ct_diarios VALUES
 ('1-TEST','2026','202606','4212','AS-42-01','M004','2026-06-10',0,8000,   8,NULL,'20333333333',NULL,NULL),
 ('1-TEST','2026','202606','4311','AS-43-01','M006','2026-06-11',0,2000,   1,NULL,'20333333333',NULL,NULL);
-- 3.13 cuentas 46 y 47 diversas
INSERT INTO ct_diarios VALUES
 ('1-TEST','2026','202606','4699','AS-46-01','M005','2026-06-05',0,1500,   1,NULL,'20444444444',NULL,NULL),
 ('1-TEST','2026','202606','4712','AS-47-01','M007','2026-06-06',0,900,    1,NULL,'20444444444',NULL,NULL);
-- Ruido que NO debe aparecer: cuenta 40 (no es 30/34/41/42/43/46/47), y periodo distinto
INSERT INTO ct_diarios VALUES
 ('1-TEST','2026','202606','4011','AS-40-01','M099','2026-06-09',0,999,    1,NULL,'20333333333',NULL,NULL),
 ('1-TEST','2026','202605','4212','AS-42-05','M050','2026-05-10',0,7777,   1,NULL,'20333333333',NULL,NULL);
GO
PRINT 'PLE_TEST creada.';
