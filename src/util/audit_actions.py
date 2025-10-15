from enum import Enum

class AuditActions(Enum):
    ADD_WORD = 1
    EDIT_WORD = 2
    REMOVE_WORD = 3
    BAN_USER = 4
    UNBAN_USER = 5
    