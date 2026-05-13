alter table public.selection_reports
    add column if not exists input_payload jsonb not null default '{}'::jsonb,
    add column if not exists scoring_version varchar(50) not null default 'v1.0.0',
    add column if not exists analysis_status varchar(50) not null default 'completed',
    add column if not exists error_message text;

create index if not exists ix_selection_reports_analysis_status on public.selection_reports(analysis_status);
create index if not exists ix_selection_reports_scoring_version on public.selection_reports(scoring_version);
