# PDF Converter · Corporepol

Convierte DOCX y PDF a PDF con fuentes correctamente embebidas usando LibreOffice.

## Añadir la fuente Hey August

1. Descarga el archivo `HeyAugust.ttf` (o `.otf`)
2. Colócalo en la carpeta `fonts/`
3. El servidor la instalará automáticamente al arrancar

## Despliegue gratuito en Railway

1. Crea una cuenta en https://railway.app (gratis)
2. Instala Railway CLI:
   ```
   npm install -g @railway/cli
   ```
3. Desde la carpeta del proyecto:
   ```
   railway login
   railway init
   railway up
   ```
4. Railway te dará una URL pública. Compártela con Marta.

### Notas Railway plan gratuito
- 500 horas/mes de uso (suficiente para uso interno)
- El servidor puede dormirse tras 10 min de inactividad, la primera conversión tarda ~5s en arrancar
- No requiere tarjeta de crédito

## Despliegue alternativo en Render

1. Crea cuenta en https://render.com
2. New > Web Service > conecta tu repositorio de GitHub
3. Runtime: Docker
4. Plan: Free
5. Deploy

## Uso local (para pruebas)

```bash
pip install -r requirements.txt
python app.py
```

Abre http://localhost:5000
