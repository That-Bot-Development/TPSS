import discord
from discord import app_commands

from modules.util.embed_maker import *
from modules.util.exceptions import NotFoundError

from datetime import *
from mysql.connector import Error as sql_error

class StaffNotes(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="notes", description="View staff notes on a user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The user to view notes on.")
    async def notes(self, interactions: discord.Interaction, user:discord.User):
        try:
            notes = self.get_notes(user.id)
        except Exception as e:
            await self.create_note_err(interactions,"list notes",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"Notes: {self.truncate_string(user.display_name)}",
            message= notes if notes else "*No notes found.*"
        ).create())
    
    
    @app_commands.command(name="addnote", description="Adds a staff note on a user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The user to add the note to.", note="The note.")
    async def addnote(self, interactions: discord.Interaction, user:discord.User, note:str):
        try:
            with self.sql.get_connection() as connection:

                self.sql.execute_query("""
                    INSERT INTO UserNotes (UserID, Note, IssuedByID) 
                    VALUES (%s,%s,%s)
                """,(user.id,note,interactions.user.id),connection=connection,handle_except=False)

        except Exception as e:
            self.create_note_err(interactions,"add note",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> Note Added",
            message=f"**Added to {user.display_name}**: {note}"
        ).create())

    @app_commands.command(name="removenote", description="Removes a staff note on a user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The user to remove the note from.", id="The Note # to remove.")
    async def removenote(self, interactions: discord.Interaction, user:discord.User, id:app_commands.Range[int, 1, 999]):
        try:
            with self.sql.get_connection() as connection:

                result = self.sql.execute_query("""
                    SELECT * FROM UserNotes
                    WHERE UserID = %s
                    ORDER BY IssuedAt DESC
                    LIMIT 1 OFFSET %s
                """,(user.id,id-1),connection=connection,handle_except=False)

                if result and len(result) > 0:
                    note_id = result[0]["NoteID"]

                    self.sql.execute_query("""
                        DELETE FROM UserNotes
                        WHERE NoteID = %s
                    """, (note_id,), connection=connection, handle_except=False)
                else:
                    raise NotFoundError(f"Could not find note #{id} for {user.display_name}.")                    

        except Exception as e:
            await self.create_note_err(interactions,"remove note",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> Note Removed",
            message=f"**Removed from {user.display_name}**: {result[0]["Note"]}"
        ).create())

    @app_commands.command(name="editnote", description="Edits a staff note on a user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The user to edit the note on.", id="The Note # to edit.", note="The updated note.")
    async def editnote(self, interactions: discord.Interaction, user:discord.User, id:app_commands.Range[int, 1, 999], note:str):
        try:
            with self.sql.get_connection() as connection:

                result = self.sql.execute_query("""
                    SELECT * FROM UserNotes
                    WHERE UserID = %s
                    ORDER BY IssuedAt DESC
                    LIMIT 1 OFFSET %s
                """,(user.id,id-1),connection=connection,handle_except=False)

                if result and len(result) > 0:
                    note_id = result[0]["NoteID"]

                    self.sql.execute_query("""
                        UPDATE UserNotes
                        SET Note = %s
                        WHERE NoteID = %s
                    """, (note, note_id), connection=connection, handle_except=False)
                else:
                    raise NotFoundError(f"Could not find note #{id} for {user.display_name}.")                    

        except Exception as e:
            await self.create_note_err(interactions,"edit note",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> Note Edited",
            message=f"**Edited on {user.display_name}**: {note}"
        ).create())

    def get_notes(self, user_id:int) -> str:
        with self.sql.get_connection() as connection:
            results = self.sql.execute_query("""
                SELECT Note FROM UserNotes WHERE UserID = %s ORDER BY IssuedAt DESC
            """,(user_id,),connection=connection,handle_except=False)
        
        if results:
            message = ""
            noteId = 1

            lines = []
            for row in results:
                lines.append(f"**#{noteId}** - {row['Note']}")
                noteId += 1
            message = "\n\n".join(lines)
        else:
            return None

        return message
        
    async def create_note_err(self, interactions:discord.Interaction, action:str, e:Exception):
        if isinstance(e, sql_error):
            message = "Unable to reach the database.\n\nIf the issue persists, contact an admin."
        elif isinstance(e, NotFoundError):
            message = str(e)
        else:
            message = "This action could not be completed.\nPlease ensure you have the required permissions.\n\nIf the issue persists, contact an admin."

        print(f"Exception occured in '{action}' operation: {e}")
        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            message=message,
            error=True
        ).create(),ephemeral=True,delete_after=20)