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
  updated_at timestamptz default now()
);

alter table public.olala_salidas enable row level security;

drop policy if exists "olala_salidas_lectura_publica" on public.olala_salidas;
create policy "olala_salidas_lectura_publica"
  on public.olala_salidas for select
  using (visible = true);

-- Bucket de fotos (Storage → New bucket → nombre: olala-salidas → Public)
-- Política de lectura pública en el bucket para objetos.
