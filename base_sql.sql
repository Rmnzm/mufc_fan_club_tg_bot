-- table contains match day calendar
create table match_day
(
    id                     bigserial
        constraint match_day_pk_2
            primary key,
    start_timestamp        timestamp                                       not null,
    opponent_name          varchar                                         not null,
    match_status           varchar default 'notstarted'::character varying not null,
    tournament_name        varchar                                         not null,
    tournament_name_slug   varchar,
    opponent_name_slug     varchar,
    localed_match_day_name text,
    event_id               varchar(255),
    constraint match_day_pk
        unique (start_timestamp, opponent_name_slug, tournament_name_slug)
);

alter table match_day
    owner to postgres;

create index match_day_opponent_time_tournament_index
    on match_day (start_timestamp, tournament_name_slug, opponent_name_slug);

create unique index unique_event_id_index
    on match_day (event_id);

-- table contains base meeting places info
create table places
(
    id          serial
        primary key,
    created_at  timestamp default now() not null,
    place_name  varchar(255)            not null,
    address     varchar(255)            not null,
    description varchar(255)
);

alter table places
    owner to postgres;

-- table contains base user info
create table users
(
    id              bigserial
        constraint users_pk
            primary key,
    username        varchar                                  not null,
    user_tg_id      bigint                                   not null,
    user_role       varchar default 'fan'::character varying not null,
    description     text,
    first_name      varchar,
    last_name       varchar,
    birthday_date   date,
    fantime_start   varchar(255),
    favorite_player varchar(255)
);

alter table users
    owner to postgres;

create unique index users_user_tg_id_unique
    on users (user_tg_id);

-- table contains user registrations on meetings
create table user_registrations
(
    id              serial
        primary key,
    created_at      timestamp default now() not null,
    user_id         integer                 not null
        references users (),
    is_approved     boolean   default false not null,
    is_canceled     boolean   default false not null,
    watch_day_id    integer                 not null
        references watch_day,
    match_day_id    integer                 not null
        references match_day,
    place_id        integer                 not null
        references places,
    is_message_sent boolean   default false not null
);

alter table user_registrations
    owner to postgres;

create unique index user_registrations_user_match_unique
    on user_registrations (user_id, match_day_id);

-- table contains registered meetings
create table watch_day
(
    id           bigserial
        constraint watch_day_pk
            primary key,
    meeting_date timestamp not null,
    match_day_id integer   not null
        constraint match_day_id_unique
            unique
        constraint watch_day_match_day_id_fk
            references match_day,
    place_id     integer   not null
        constraint watch_day_place_id_fk
            references places,
    watch_status varchar(255) default 'notstarted'::character varying
);

alter table watch_day
    owner to postgres;



