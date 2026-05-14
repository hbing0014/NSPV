alter table public.users
    add column if not exists password_hash varchar(255);

create index if not exists ix_users_email on public.users(email);
