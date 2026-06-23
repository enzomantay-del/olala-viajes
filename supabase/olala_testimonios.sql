-- Testimonios de viajeros (catálogo público Olalá Viajes)

create table if not exists public.olala_testimonios (
  id bigint generated always as identity primary key,
  salida_id bigint,
  nombre_cliente text not null default '',
  destino_label text not null default '',
  texto text not null default '',
  foto_url text not null default '',
  emoji_destino text not null default '✈️',
  estrellas smallint not null default 5 check (estrellas >= 1 and estrellas <= 5),
  anio smallint,
  orden integer not null default 0,
  visible boolean not null default true,
  creado_en timestamptz not null default now()
);

alter table public.olala_testimonios enable row level security;

drop policy if exists "olala_testimonios_lectura_publica" on public.olala_testimonios;
create policy "olala_testimonios_lectura_publica"
  on public.olala_testimonios for select
  using (visible = true);

-- Ejemplos iniciales (podés borrarlos o editarlos desde el panel /admin/)
insert into public.olala_testimonios (salida_id, nombre_cliente, destino_label, texto, emoji_destino, estrellas, anio, orden)
select v.salida_id, v.nombre, v.destino, v.texto, v.emoji, v.estrellas, v.anio, v.orden
from (values
  (null::bigint, 'María G.', 'Europa', 'Increíble organización. Recorrimos varias ciudades sin preocuparnos por nada. Olalá estuvo en cada detalle.', '🇪🇺', 5, 2025, 1),
  (null::bigint, 'Carlos y Laura', 'Puerto Madryn', 'Ver las ballenas en familia fue un sueño. El grupo era muy buena onda y los guías excelentes.', '🦭', 5, 2025, 2),
  (null::bigint, 'Silvia R.', 'Punta Cana', 'Playa, sol y hotel hermoso. Ya estamos averiguando el próximo viaje con Olalá.', '🏝️', 5, 2024, 3),
  (null::bigint, 'Pablo M.', 'Bariloche', 'Bariloche en invierno es otra cosa. Todo coordinado, traslados puntuales y muy buen precio.', '🇦🇷', 5, 2024, 4),
  (null::bigint, 'Familia Acosta', 'Brasil', 'Porto de Galinhas nos encantó. Los chicos no querían volver. Gracias Olalá por el viaje.', '🇧🇷', 5, 2025, 5)
) as v(salida_id, nombre, destino, texto, emoji, estrellas, anio, orden)
where not exists (select 1 from public.olala_testimonios limit 1);
