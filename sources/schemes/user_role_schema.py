from tools.enums import UserRoleEnum
from pydantic import BaseModel


class UserRoleSchema(BaseModel):
    user_role: UserRoleEnum
