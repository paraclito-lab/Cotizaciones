# Cotizaciones emitidas

Copia de cada cotización que **ya se envió al cliente**, en dos archivos por N°:

- `NNNN-AAAA.jpg` — la imagen comprimida, copia de lo que vio el cliente.
- `NNNN-AAAA.json` — **la fuente**: el JSON con el que se generó. Es lo que permite corregir un
  ítem semanas después sin rehacer la cotización de memoria. Antes vivía solo en `/tmp` y se
  perdía con el contenedor (hallazgos-abiertos.md, N02). Lleva además `nota_interna`: por qué
  se cobró lo que se cobró (excepciones, precios dados directamente). Ese campo **nunca** se
  imprime en el PDF.

## Por qué imagen y no PDF

El PDF de una cotización pesa ~334 KB y el PNG de vista previa ~675 KB (sale a 2x para verse
nítido en pantalla). Bajado a 1x y codificado en JPEG queda en ~227 KB: se lee perfecto y el
repositorio no crece a saltos. A 20 cotizaciones al mes son ~4.5 MB al mes en vez de ~8 MB con
PDF, y el archivo sigue siendo consultable desde el celular sin abrir nada.

El PDF se sigue generando — es lo que se le envía al cliente. Lo que no se guarda acá es el PDF.

## Cómo se archiva

No es automático. Se archiva la cotización **aprobada**:

```bash
python3 plantilla/generar.py cotizacion.json salida/ --archivar
```

Sin `--archivar` no se toca esta carpeta. La razón es concreta: cuando el archivado era
automático, regenerar el JSON de ejemplo (que lleva un placeholder en el nombre de contacto)
sobrescribió la copia de la cotización real ya enviada. El archivo guarda una copia por N° de
cotización, así que volver a archivar el mismo número reemplaza su copia: queda siempre la
última versión aprobada de cada una.

## Sobre los datos del cliente

Esta carpeta es la **única excepción** a la regla de que los nombres de contacto del cliente no
van en archivos del repositorio (ver `.claude/skills/cotizar/SKILL.md`). Va acá porque la
imagen y su JSON fuente son copia fiel del documento que el cliente recibió — si el cliente reclama por lo
cotizado, esto es lo que se muestra. En todo lo demás (ejemplos, JSON de prueba, documentación)
va un placeholder.
