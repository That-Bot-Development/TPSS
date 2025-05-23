import discord

class DurationParseError(Exception):
    """Thrown when the specified duration cannot be parsed from user input."""
    pass

class DurationOutOfBoundsError(Exception):
    """Thrown when the specified duration is out of bounds for the given context."""
    pass

class NotFoundError(Exception):
    """Thrown when the requested data cannot be found from the source."""
    pass

class PermissionError(Exception):
    """Thrown when the user does not have the required permissions to perform an action."""

    def __init__(self, staff:discord.Member, member:discord.Member, pun_type:str):
        super().__init__(f"{staff.display_name} attempted to issue a {pun_type} on {member.display_name}.")