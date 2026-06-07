# Olalá Viajes — arquitectura simple

Igual que **Jardín Sale Week**: sitio estático rápido + Supabase para datos e imágenes.

| Qué | Dónde |
|-----|--------|
| **Catálogo público** (link para clientes) | https://olala-viajes.web.app (Firebase Hosting) |
| **Datos + fotos** | Supabase (tabla `olala_salidas`, bucket `olala-salidas`) |
| **Panel de gestión** | Tu PC: `iniciar-panel.bat` → http://127.0.0.1:8000 |

**No se usa Render** para el link que compartís. Firebase abre al instante, sin pantalla de “Render”.

## Configuración única

1. En Supabase → SQL Editor: ejecutá `supabase/olala_salidas.sql`
2. En Supabase → Storage: creá bucket público `olala-salidas`
3. Copiá `.env.example` → `.env` y pegá `SUPABASE_SERVICE_KEY` (service_role)
4. `python manage.py sincronizar_supabase`
5. `publicar-web.bat` (sube el sitio a Firebase)

## Uso diario

1. `iniciar-panel.bat`
2. Editás salidas → se sincronizan solas a Supabase
3. Los clientes ven cambios en https://olala-viajes.web.app al refrescar

## Si cambiás el diseño del sitio público

Ejecutá `publicar-web.bat` otra vez (solo sube HTML/CSS/JS a Firebase).
