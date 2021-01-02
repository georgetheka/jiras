drop table if exists issue cascade;
create table issue
(
    id            serial primary key,
    ingested_at   timestamp without time zone not null default current_timestamp,

    key           varchar(16)                 not null unique not null,
    project       varchar(64)                 not null,
    type          varchar(64)                 not null,
    status        varchar(64)                 not null,
    created       timestamp without time zone not null,
    creator       varchar(64)                 not null,
    creator_id    varchar(16)                 not null,
    reporter      varchar(64)                 not null,
    reporter_id   varchar(16)                 not null,
    summary       varchar(512)                not null,
    assignee      varchar(64),
    assignee_id   varchar(16),
    updated       timestamp without time zone,
    resolved      timestamp without time zone,
    resolution    varchar(64),
    due_date      timestamp without time zone,
    description   varchar,
    labels        varchar(64)[],
    components    varchar(64)[],
    links         jsonb,
    custom_fields jsonb
);

drop table if exists event_log cascade;
create table event_log
(
    id          bigserial primary key,
    ingested_at timestamp without time zone not null default current_timestamp,
    issue_key   varchar(16) references issue (key),
    field       varchar(32)                 not null,
    reporter    varchar(64),
    reporter_id varchar(16),
    assignee    varchar(64),
    assignee_id varchar(16),
    created     timestamp without time zone,
    status      varchar(64),
    resolution  varchar(64)
);
create index ix_event_log_issue_key on event_log (issue_key);

drop table if exists time_in_status cascade;
create table time_in_status
(
    id          bigserial primary key,
    ingested_at timestamp without time zone not null default current_timestamp,
    issue_key   varchar(16) references issue (key),
    status      varchar(64),
    days        numeric
);
create index ix_time_in_status_issue_key on time_in_status (issue_key);

drop table if exists time_per_assignee cascade;
create table time_per_assignee
(
    id          bigserial primary key,
    ingested_at timestamp without time zone not null default current_timestamp,
    issue_key   varchar(16) references issue (key),
    assignee    varchar(64),
    days        numeric
);
create index ix_time_per_assignee_issue_key on time_per_assignee (issue_key);

drop table if exists timeline cascade;
create table timeline
(
    id          bigserial primary key,
    ingested_at timestamp without time zone not null default current_timestamp,
    issue_key   varchar(16) references issue (key),
    d           date,
    status      varchar(64)[],
    assignee    varchar(64)[]
);
create index ix_timeline_issue_key on timeline (issue_key);
