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
