-- Ejecutar en Supabase → SQL Editor (si ya creaste la tabla olala_alertas)

-- Permite que el formulario de la web guarde alertas SIN pasar por Render.



drop policy if exists "olala_alertas_insert_publica" on public.olala_alertas;

create policy "olala_alertas_insert_publica"

  on public.olala_alertas for insert

  to anon, authenticated

  with check (

    estado = 'activa'

    and (length(trim(destino)) > 0 or length(trim(categoria)) > 0)

    and (length(trim(email)) > 0 or length(trim(whatsapp)) > 0)

  );


