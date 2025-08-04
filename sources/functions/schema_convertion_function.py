from schemes.scheme import (
    UsersSchema,
    MatchDaySchema,
    WatchDaySchema,
    NearestMeetingsSchema,
    PlacesSchema,
    UserRegistrationSchema,
    InvitationContextSchema,
    UserRegistrationTableSchema,
)


class SchemaConvertionFunction:
    @staticmethod
    def convert_users_info(users):
        return [UsersSchema(**user) for user in users]

    @staticmethod
    def convert_match_day_info(match_days):
        return [MatchDaySchema(**match_day) for match_day in match_days]

    @staticmethod
    def convert_watch_day_info(watch_days):
        return [WatchDaySchema(**watch_day) for watch_day in watch_days]

    @staticmethod
    def convert_nearest_meetings(nearest_meetings):
        return [
            NearestMeetingsSchema(**nearest_meeting)
            for nearest_meeting in nearest_meetings
        ]

    @staticmethod
    def convert_places(places):
        return [PlacesSchema(**place) for place in places]

    @staticmethod
    def convert_users_registration(users):
        return [UserRegistrationSchema(**user) for user in users]

    @staticmethod
    def convert_invitations_context(invitations):
        return [InvitationContextSchema(**context) for context in invitations]

    @staticmethod
    def convert_registration_table(registrations):
        return [
            UserRegistrationTableSchema(**registration)
            for registration in registrations
        ]

    @staticmethod
    def convert_model_to_dict(model):
        return model.model_dump()
