# Fotos — solución definitiva

## El problema
Render **borra** las fotos del disco al reiniciar. Por eso al subir un paquete nuevo solo queda esa imagen.

## La solución (3 capas)

1. **`seed_media/salidas/`** — Las 32 fotos van en el repositorio Git. Render las tiene siempre al desplegar.
2. **Cloudinary** — `CLOUDINARY_URL` en Render. Al desplegar y al publicar, las fotos se suben a la nube.
3. **Web pública** — Usa URLs de Cloudinary (no dependen del disco de Render).

## Una sola vez (vos)

```powershell
cd C:\Users\Enzo\olala-viajes
git add .
git commit -m "Solución definitiva fotos: seed_media + Cloudinary automático"
git push
```

Esperá 3–5 min el deploy en Render. Verificá que `CLOUDINARY_URL` esté en Environment.

## Después de eso

- Subís paquetes y fotos desde el panel (Render o celular).
- **Publicar en web** sincroniza fotos solo y publica.
- No hace falta `publicar-web.bat` ni scripts en la PC.

## Si algo falla

- Cartel rojo en Salidas → falta `CLOUDINARY_URL` en Render.
- Cartel amarillo → esperá el redeploy o tocá Publicar (sincroniza solo).
