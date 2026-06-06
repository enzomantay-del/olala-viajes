# Olalá Viajes — Un solo flujo (simple)

## Dos URLs, un solo lugar para gestionar

| URL | Para qué |
|-----|----------|
| **https://olala-viajes.onrender.com** | Panel de gestión (celular, PC, tablet) |
| **https://olala-viajes.web.app** | Web pública para clientes (se actualiza sola) |

No hace falta usar `localhost` para el día a día.  
No hace falta `publicar-web.bat` (es opcional / respaldo).

---

## Qué hacer siempre

1. Entrá al panel: **https://olala-viajes.onrender.com/accounts/login/**
2. Editá salidas, fotos, precios, etc.
3. **Salidas → Publicar en web** (un solo botón)
4. Esperá 1–2 minutos y **refrescá** la página de Salidas
5. Los clientes ven los cambios en **olala-viajes.web.app** (Ctrl+F5)

---

## Configuración única en Render (para publicar desde el celular)

En Render → tu servicio → **Environment**, agregá:

```
FIREBASE_TOKEN = (token de una sola vez, ver abajo)
```

### Cómo obtener el token (una vez, en tu PC)

```powershell
firebase.cmd login --reauth
firebase.cmd login:ci
```

Copiá el token que muestra y pegalo en Render como `FIREBASE_TOKEN`.

Sin este token, el panel genera el sitio pero **no puede subirlo** a Firebase desde Render.

---

## Fotos de paquetes (importante en Render)

En Render el disco **se borra** al reiniciar. Si subís una foto nueva y desaparecen las demás, es por eso.

### Configuración única: Cloudinary (gratis) — **obligatorio en Render**

Sin esto, cada vez que subís un paquete nuevo **se borran las fotos de los demás**.

1. Creá cuenta en **https://cloudinary.com**
2. En el panel → **API Keys** → copiá la URL completa (`cloudinary://...`)
3. En Render → **Environment** → agregá:

```
CLOUDINARY_URL = cloudinary://...
```

4. **Restaurar todas las fotos** (una sola vez, en tu PC):

```powershell
cd c:\Users\Enzo\olala-viajes
copy .env.ejemplo.txt .env
# Editá .env: pegá CLOUDINARY_URL y DATABASE_URL (copiá de Render → Environment)
.\restaurar-fotos.bat
```

5. En el panel de Render → **Salidas** debe verse el cartel verde *"Fotos en la nube: X/X"*
6. Ahí recién **Publicar en web** funciona bien desde el celular o Render.

El panel **bloquea** publicar si faltan fotos o no hay Cloudinary.

### Si las fotos siguen sin verse

Suele ser por una de estas tres cosas:

1. **CLOUDINARY_URL en Render pero el código nuevo no está desplegado** — hay que subir los cambios a GitHub y esperar el redeploy de Render.
2. **No se subieron las fotos viejas a Cloudinary** — en tu PC, con las fotos en `media/salidas/`:
   ```powershell
   firebase.cmd login --reauth
   restaurar-fotos.bat
   ```
3. **Publicaste desde Render sin Cloudinary** — en el servidor solo queda la última foto subida.

**Arreglo rápido (desde tu PC, con todas las fotos locales):**

```powershell
cd c:\Users\Enzo\olala-viajes
firebase.cmd login --reauth
publicar-web.bat
```

Luego Ctrl+F5 en olala-viajes.web.app.

---

## ¿Y localhost?

Solo para desarrolladores que cambian código. La agencia puede ignorarlo.

---

## Resumen

```
Editás en Render (cualquier dispositivo)
        ↓
Publicar en web (mismo panel)
        ↓
olala-viajes.web.app se actualiza
```

Un panel. Un botón. Una web pública.
