create table if not exists parents (
    id uuid primary key default gen_random_uuid(),
    user_id uuid unique not null,
    created_at timestamptz default now()
);
alter table parents enable row level security;

create table if not exists children (
    id uuid primary key default gen_random_uuid(),
    user_id uuid unique,
    display_name text not null,
    parent_id uuid references parents(id) on delete set null,
    created_at timestamptz default now()
);
alter table children enable row level security;

create table if not exists family_links (
    code text primary key,
    parent_id uuid not null references parents(id) on delete cascade,
    expires_at timestamptz not null,
    used_by_child uuid references children(id),
    created_at timestamptz default now()
);
alter table family_links enable row level security;

create table if not exists chat_messages (
    id bigserial primary key,
    child_id uuid not null references children(id) on delete cascade,
    role text check (role in ('user', 'assistant')) not null,
    content text not null,
    sentiment numeric,
    triage_level text check (triage_level in ('none', 'low', 'medium', 'high')),
    created_at timestamptz default now()
);
alter table chat_messages enable row level security;

create table if not exists moods (
    id bigserial primary key,
    child_id uuid not null references children(id) on delete cascade,
    mood text not null,
    mood_score int not null,
    note text,
    created_at timestamptz default now()
);
alter table moods enable row level security;

create table if not exists journals (
    id bigserial primary key,
    child_id uuid not null references children(id) on delete cascade,
    text text not null,
    sentiment numeric,
    created_at timestamptz default now()
);
alter table journals enable row level security;

create table if not exists game_events (
    id bigserial primary key,
    child_id uuid not null references children(id) on delete cascade,
    activity text not null,
    delta int default 0,
    created_at timestamptz default now()
);
alter table game_events enable row level security;

create table if not exists sentiment_daily (
    child_id uuid not null references children(id) on delete cascade,
    day date not null,
    avg_sentiment numeric,
    high_risk_count int default 0,
    wellbeing_score int,
    primary key (child_id, day)
);
alter table sentiment_daily enable row level security;
