# Validación PLE — Libro 3 (3.8 / 3.9 / 3.11 / 3.12 / 3.13)

## Alcance

El **validador oficial PLE de SUNAT** es una aplicación de escritorio (Java) que se ejecuta en la
máquina del contribuyente con su RUC real y emite la constancia. No se ejecuta en CI ni de forma
headless. Para tener una verificación **automática y auditable**, se implementó
`pruebas/ple_validador.py`, que **replica las reglas del validador PLE** para estos formatos:

- **Nomenclatura del archivo**: `LE + RUC(11) + AAAA + MM + DD + código(6) + CC + O + I + M + G + .TXT`
  (Anexo 2 — hoja "Reglas de nombres de libros").
- **Estructura de cada registro**: número de campos, formatos (periodo AAAAMMDD, fecha DD/MM/AAAA,
  decimales `#.##` hasta 12 enteros, sin separador de miles), tablas (Tabla 2 tipo de documento,
  Tabla 15 tipo de título, estados 0/1/2/8/9), longitudes máximas, y caracteres prohibidos en texto
  (`| / \`, tabs y saltos de línea) — Regla General 2.0.
- **Consistencia tipo/número de documento** (DNI→8, RUC→11, etc.).

Fuente de las reglas: `referencia/Estructura_del_PLE.xls` y `referencia/Anexo_Tabla_13.xls`.

## Resultado

Se generó un `.txt` por libro desde la base de prueba y se pasó por el validador:

```
[VALIDO]  LE2012345678920260030030800071111.TXT   (3.8  · 1 registro)
[VALIDO]  LE2012345678920260030030900071111.TXT   (3.9  · 1 registro)
[VALIDO]  LE2012345678920260030031100071111.TXT   (3.11 · 1 registro)
[VALIDO]  LE2012345678920260030031200071111.TXT   (3.12 · 2 registros)
[VALIDO]  LE2012345678920260030031300071111.TXT   (3.13 · 2 registros)
RESULTADO: TODOS LOS ARCHIVOS VALIDOS
```

El validador se probó también con un archivo con errores deliberados (periodo de 7 dígitos, fecha en
formato ISO, decimal con 1 decimal, estado inválido, correlativo sin A/M/C y un `|` dentro de un
texto) y los **rechazó todos** — confirma que no es un validador vacío.

## Hallazgo relevante

El validador detectó un caso de **inconsistencia tipo/número de documento**: un número de 11 dígitos
etiquetado como DNI (que exige 8). Era un dato de prueba mal armado, pero destapa una decisión real:
las 5 ramas emiten el `idtipodocidentidad` **almacenado** en `zg_auxiliares`/`zg_proveedores` tal
cual. Si esa columna no está bien mantenida, SUNAT rechaza. Los libros de ventas/compras del mismo SP
lo **derivan** del largo del número. Decisión a confirmar con el equipo.

Además, a raíz de la Regla General 2.0 se reforzó el saneo de texto: ahora también se eliminan
`| / \` (antes sólo TAB/CR/LF).

## Importante

Esta verificación es **estructural**. La constancia oficial sigue requiriendo ejecutar el validador
PLE de SUNAT con el **RUC real** de la empresa y un **periodo con datos reales**.
