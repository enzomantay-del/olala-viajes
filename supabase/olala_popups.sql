-- Popups / avisos modales en la web pública Olalá Viajes
-- Ejecutar en Supabase → SQL Editor

create table if not exists public.olala_popups (
  id bigint primary key,
  titulo text not null default '',
  mensaje text not null default '',
  imagen_url text not null default '',
  fecha_desde date not null,
  fecha_hasta date not null,
  enlace_url text not null default '',
  enlace_texto text not null default 'Ver más',
  activo boolean not null default true,
  orden integer not null default 0,
  creado_en timestamptz not null default now()
);

alter table public.olala_popups enable row level security;

drop policy if exists "olala_popups_lectura_publica" on public.olala_popups;
create policy "olala_popups_lectura_publica"
  on public.olala_popups for select
  using (
    activo = true
    and fecha_desde <= current_date
    and fecha_hasta >= current_date
  );
