# Libros Contables — PLE Libro 3 (Inventarios y Balances)

Implementación y documentación de **5 formatos del Libro 3** (Programa de Libros Electrónicos de SUNAT) en el stored procedure `Ct_Pro_PLE` del sistema Codeplex (BD `CodeplexWeb_2020`).

## Documentación

**[`index.html`](index.html)** es una página estática — se despliega en **Vercel sin build**. Ábrela localmente con doble clic o míra el deploy de Vercel. Incluye: comparación antes/después de cada rama, tooltips por campo con la descripción SUNAT, y descargables (BD de prueba y scripts).

## Formatos implementados

| `@Accion` | Formato | Cuenta contable |
|---|---|---|
| `030800` | 3.8 | 30 — Inversiones Mobiliarias |
| `030900` | 3.9 | 34 — Intangibles |
| `031100` | 3.11 | 41 — Remuneraciones y Participaciones por Pagar |
| `031200` | 3.12 | 42 / 43 — Cuentas por Pagar Comerciales |
| `031300` | 3.13 | 46 / 47 — Cuentas por Pagar Diversas |

Cada rama devuelve el archivo oficial en palotes (`@exportar_excel=0`) o su equivalente en Excel (`@exportar_excel=1`).

## Contenido del repo

- `index.html` — documentación interactiva (entrada de Vercel).
- `Ct_Pro_PLE_20260701.sql` — SP con las 5 ramas implementadas.
- `Ct_Pro_PLE_20260701.sql.bak` — respaldo del SP original.
- `pruebas/`
  - `schema.sql` — BD de prueba (tablas mock + datos de casos borde)
  - `test_bodies.sql` / `test_excel.sql` — ejecutan las 5 ramas (TXT / Excel)
  - `validate.py` — aserciones automáticas
  - `gen.py` — genera las ramas del SP y el test desde una fuente única
  - `build_html.py` — genera `index.html`
- `referencia/` — layouts oficiales SUNAT (estructura del PLE y anexo de tablas).

## Criterio de implementación (senior)

- Salida dual TXT / Excel con tabla temporal (patrón del formato ya validado `030700`).
- Alias de salida en **lenguaje ubicuo** (español, sin abreviaturas); las columnas/tablas existentes de Codeplex2020 se leen **tal cual**.
- Predicados SARGables (`idcuenta like '30%'`), signo positivo en pasivos, `ISNULL` en sumas, estado 1/8/9, saneo de CR/LF/TAB, solo lectura.

## Estado

Probado en SQL Server (LocalDB): estructura de campos, signos, fechas, `SUM` por asiento y saneo de texto; el procedimiento completo pasa `SET PARSEONLY`; el diff confirma que **solo cambiaron estas 5 ramas**. Pendiente: 4 confirmaciones de negocio (fuentes de datos de los campos TODO y validación con un periodo real) — detalladas en la documentación.

## Deploy en Vercel

Sitio estático, sin build. Vercel sirve `index.html` desde la raíz automáticamente. No requiere `vercel.json`.
