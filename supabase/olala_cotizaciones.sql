-- Solicitudes de cotización desde el catálogo público
create table if not exists olala_cotizaciones (
  id bigint generated always as identity primary key,
  destino text not null,
  fecha_salida date not null,
  noches integer not null check (noches > 0),
  categoria_hotel text not null default '',
  regimen text not null default '',
  adultos integer not null default 1 check (adultos >= 0),
  menores jsonb not null default '[]'::jsonb,
  aclaraciones text not null default '',
  email text not null default '',
  whatsapp text not null default '',
  estado text not null default 'pendiente',
  creado_en timestamptz not null default now()
);

alter table olala_cotizaciones enable row level security;
-- Sin políticas para anon: inserta solo el backend Django con service_role.
