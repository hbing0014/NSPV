alter table public.projects
    add column if not exists target_price_min double precision,
    add column if not exists target_price_max double precision,
    add column if not exists status varchar(50) not null default 'active';

create index if not exists ix_projects_status on public.projects(status);
