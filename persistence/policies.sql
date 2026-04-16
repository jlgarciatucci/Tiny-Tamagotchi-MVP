alter table pets enable row level security;
alter table pet_events enable row level security;

drop policy if exists "Allow anonymous read of active pet" on pets;
drop policy if exists "Allow anonymous insert of active pet" on pets;
drop policy if exists "Allow anonymous update of active pet" on pets;
drop policy if exists "Allow anonymous read of pet events" on pet_events;
drop policy if exists "Allow anonymous insert of pet events" on pet_events;

create policy "Allow anonymous read of active pet"
on pets
for select
to anon
using (id = 'active-pet');

create policy "Allow anonymous insert of active pet"
on pets
for insert
to anon
with check (id = 'active-pet');

create policy "Allow anonymous update of active pet"
on pets
for update
to anon
using (id = 'active-pet')
with check (id = 'active-pet');

create policy "Allow anonymous read of pet events"
on pet_events
for select
to anon
using (pet_id = 'active-pet');

create policy "Allow anonymous insert of pet events"
on pet_events
for insert
to anon
with check (pet_id = 'active-pet');
