-- Alertas de destino: "avisame cuando salga" (catálogo público Olalá Viajes)



create table if not exists public.olala_alertas (

  id bigint generated always as identity primary key,

  destino text not null default '',

  categoria text not null default '',

  fecha_desde date,

  fecha_hasta date,

  email text not null default '',

  whatsapp text not null default '',

  estado text not null default 'activa',

  salidas_avisadas jsonb not null default '[]'::jsonb,

  creado_en timestamptz not null default now(),

  notificado_en timestamptz

);



alter table public.olala_alertas enable row level security;



-- La web pública (clave anon) puede CREAR alertas, no leerlas.

drop policy if exists "olala_alertas_insert_publica" on public.olala_alertas;

create policy "olala_alertas_insert_publica"

  on public.olala_alertas for insert

  to anon, authenticated

  with check (

    estado = 'activa'

    and (length(trim(destino)) > 0 or length(trim(categoria)) > 0)

    and (length(trim(email)) > 0 or length(trim(whatsapp)) > 0)

  );



-- Campo adicional en salidas (si aún no existe)

alter table public.olala_salidas add column if not exists salida_confirmada boolean default false;


