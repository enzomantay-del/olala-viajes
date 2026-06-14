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
-- Sin políticas para anon: inserta solo el backend Django con service_role.

-- Campo adicional en salidas (si aún no existe)
alter table public.olala_salidas add column if not exists salida_confirmada boolean default false;
