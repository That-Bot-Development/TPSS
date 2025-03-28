# How to Set Up A Copy of That Bot
This guide will walk you through the steps to set up your own instance of That Bot. Follow the instructions carefully to configure your Discord Bot Token and SQL database connection.

## 1. Setting Up the API Token
The bot requires your **Discord Bot Token** to interact with the Discord API. To get your token, follow these steps:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application, or select an existing one.
3. In the application settings, go to the "Bot" tab.
4. Under the "TOKEN" section, click "Copy" to get your bot token.

### Create a 'private' Directory
To keep your sensitive information safe, create a `private` directory where all the configuration files will reside.

1. Navigate to your bot's directory.
2. Inside the bot's directory, create a new directory called `private`.

### Create the Token File
Within the `private` directory, create a new file called `token.txt`.

1. Open `token.txt` with any text editor.
2. Paste your **Discord Bot Token** into the file and save it.

Your `private/token.txt` file should simply include your bots token as seen below:

`YOUR_DISCORD_BOT_TOKEN`

## 2. Setting Up SQL Connection Config
Next, you'll need to configure the bot to connect to your SQL database. The bot will require details like your database host, username, password, and database name.

### Create a `sql_configuration.json` File

In the same `private` directory, create a new file called `sql_configuration.json`.

1. Open `sql_configuration.json` with any text editor.
2. Copy and paste the following JSON format into the file:

```json
{
    "db_host": "",
    "db_user": "",
    "db_password": "", 
    "db_name": ""
}
```
3. Fill in each field with the correct credentials & information.

**If you do not wish to use SQL, do not include a `sql_configuration.json` file. This will disable all SQL functionality within the bot.**
- Systems that access the database will still function, but data cannot be stored or retrived.

## 3. Setting Up Database Schema

For information on the SQL schemas used by That Bot, see [TBD].
