'''Contains all classes that hold properties for the various ticket types.'''

ADMIN_PING = 578356923611611146
MOD_PING = 624816689393041425
MISC_PING = 987189009656733696


class ReportMember:
    '''Properties for Report Member ticket type.'''
    SELECT_DATA = ["Report a Member","📄","Report a member of That Place."]
    TICKET_DATA = [MOD_PING, "member report"]


class StateQuestionConcern:
    '''Properties for State Question/Concern ticket type.'''

    SELECT_DATA = ["State a Question or Concern","❓","State a question or concern regarding the server."]
    TICKET_DATA = [MOD_PING, "question or concern"]


class SuggestPoll:
    '''Properties for Suggest Poll ticket type.'''

    SELECT_DATA = ["Suggest a Poll","🗳️","Suggest an idea for a server poll to the staff team."]
    TICKET_DATA = [MISC_PING, "poll suggestion"]


class ReportMod:
    '''Properties for Report Mod ticket type.'''

    SELECT_DATA = ["Report a Mod","<:MOD:888622194752622622>","Report a moderator. Only admins can see this."]
    TICKET_DATA = [ADMIN_PING, "moderator report"]


class ReportEventManager:
    '''Properties for Report Event Manager ticket type.'''

    SELECT_DATA = ["Report an Event Manager","<:EVENTMGR:888634722052358145>","Report an event manager. Only admins can see this."]
    TICKET_DATA = [ADMIN_PING, "Event Manager report"]


class Other:
    '''Properties for Other ticket type.'''

    SELECT_DATA = ["Other","<a:battery:624411754801397791>","Contact staff for anything else."]
    TICKET_DATA = [MISC_PING, "mod mail"]