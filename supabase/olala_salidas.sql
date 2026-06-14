-- Ejecutar en Supabase → SQL Editor (proyecto de Olalá / compartido con Sale Week)

create table if not exists public.olala_salidas (
  id bigint primary key,
  nombre_paquete text not null,
  fecha_salida date not null,
  lugar_salida text default '',
  descripcion text default '',
  servicios_incluidos text default '',
  imagen_url text default '',
  precio numeric,
  moneda text default 'ARS',
  cupos integer,
  agotado boolean default false,
  pasa_por_jardin_america boolean default false,
  vacaciones_invierno boolean default false,
  categorias jsonb default '[]'::jsonb,
  cats jsonb default '[]'::jsonb,
  cat text default 'argentina',
  cat_label text default 'Argentina',
  emoji text default '✈️',
  operadora_nombre text default '',
  visible boolean default true,
  flyer_url text default '',
  updated_at timestamptz default now()
);

alter table public.olala_salidas add column if not exists flyer_url text default '';
alter table public.olala_salidas add column if not exists salida_confirmada boolean default false;

alter table public.olala_salidas enable row level security;

drop policy if exists "olala_salidas_lectura_publica" on public.olala_salidas;
create policy "olala_salidas_lectura_publica"
  on public.olala_salidas for select
  using (visible = true);

-- Bucket olala-salidas: crealo en Storage → Public (ya lo hiciste).
-- Política para que las fotos se vean en la web (ejecutá esto en SQL Editor):

insert into storage.buckets (id, name, public)
values ('olala-salidas', 'olala-salidas', true)
on conflict (id) do update set public = true;

drop policy if exists "public_can_read_olala_salidas" on storage.objects;
create policy "public_can_read_olala_salidas"
on storage.objects for select to public
using (bucket_id = 'olala-salidas');
