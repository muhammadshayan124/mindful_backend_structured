create index if not exists idx_parents_user on parents(user_id);
create index if not exists idx_children_user on children(user_id);
create index if not exists idx_children_parent on children(parent_id);
create index if not exists idx_chat_child_time on chat_messages(child_id, created_at desc);
create index if not exists idx_moods_child_time on moods(child_id, created_at desc);
create index if not exists idx_journals_child_time on journals(child_id, created_at desc);
create index if not exists idx_games_child_time on game_events(child_id, created_at desc);
create index if not exists idx_daily_child_day on sentiment_daily(child_id, day);
