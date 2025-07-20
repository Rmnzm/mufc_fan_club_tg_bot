from peewee import *
from database.models.base_model import BaseModel  

class MatchDay(BaseModel):
    id = AutoField()
    start_timestamp = DateTimeField()
    opponent_name = CharField()
    match_status = CharField(default='notstarted')
    tournament_name = CharField()
    tournament_name_slug = CharField(null=True)
    opponent_name_slug = CharField(null=True)
    localed_match_day_name = TextField(null=True)
    event_id = CharField(max_length=255, null=True, unique=True)

    class Meta:
        table_name = 'match_day'
        indexes = (
            (('start_timestamp', 'opponent_name_slug', 'tournament_name_slug'), True),
            (('start_timestamp', 'tournament_name_slug', 'opponent_name_slug'), False),
        )

class Place(BaseModel):
    id = AutoField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT now()')])
    place_name = CharField(max_length=255)
    address = CharField(max_length=255)
    description = CharField(max_length=255, null=True)

    class Meta:
        table_name = 'places'

class User(BaseModel):
    id = AutoField()
    username = CharField()
    user_tg_id = BigIntegerField(unique=True)
    user_role = CharField(default='fan')
    description = TextField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    birthday_date = DateTimeField(null=True)
    favorite_player = CharField(null=True)
    fantime_start = CharField(null=True)

    class Meta:
        table_name = 'users'

class WatchDay(BaseModel):
    id = AutoField()
    meeting_date = DateTimeField()
    match_day_id = ForeignKeyField(MatchDay, backref='watch_day')
    place_id = ForeignKeyField(Place, backref='watch_day')
    watch_status = CharField(max_length=255, default='notstarted')

    class Meta:
        table_name = 'watch_day'
        indexes = (
            (('match_day_id',), True), 
        )

class UserRegistration(BaseModel):
    id = AutoField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT now()')])
    user_id = ForeignKeyField(User, backref='user_registrations')
    is_approved = BooleanField(default=False)
    is_canceled = BooleanField(default=False)
    watch_day_id = ForeignKeyField(WatchDay, backref='user_registrations')
    match_day_id = ForeignKeyField(MatchDay, backref='user_registrations')
    place_id = ForeignKeyField(Place, backref='user_registrations')
    is_message_sent = BooleanField(default=False)

    class Meta:
        table_name = 'user_registrations'
        indexes = (
            (('user_id', 'match_day_id'), True), 
        )
