# team-maple

Team Maple bot.

## Requirements

Listed in `requirements.txt`

## Configuration

Done via enviroment variables, also through a `.env` file

Copy the `.env-example` to `.env` and fill in the values accordingly

Additionally, one can provide the same information as `dict`s to to the `CLIENT_INFO` list in `env.py`

Info for the async-cleverbot, api- https://pypi.org/project/async-cleverbot/

> Enviroment variables take precedence over `CLIENT_INFO`

## Extensions

### Hot Potato

Allows for playing of Hot Potato between all the attached clients

The hot potato can only appear in the given `POTATO_CHANNEL_IDS` for each client

Run `.potato` to spawn one in the current guild, or provide a guild after `.potato` to spawn one in that guild

> Only one hot potato can be active at a time

In the channel of an active hot potato, you can run `.toss` to throw the hot potato to another potato channel

> If other clients can see the active hot potato channel, they too will attempt to run `.toss` in time

Once the potato explodes, the game is over!

### Misc

The `.cleartext` command will clear all the messages in the current channel

### Number Guessing

Allows for playing of the Number Guessing game, in which one person states they're thinking of a number between two other numbers, and the other player(s) have to guess it.

When the other player guesses incorrectly, the first player responds if the guess was too high or too low.

***

Users can play this game with bots by stating `I'm thinking of a number between 1 and 10` - with `1` and `10` being any number they want - and responding with `high` or `low` depending on the guessed number

When the number is guessed, then respond with `guessed` to tell the bot it's been guessed!

***

To have the bot play as player 1, the `.guess_number` command exists, which can optionally take the `lowest` and `highest` numbers that are possible - for example, `.guess_number -50 50`

> Any other bots that can see the channel will also attempt to guess the number

### Fun

The `.talk` command can be used to toggle the chatting between the first 2 bots in the .env by `.talk start` (to start) and `.talk stop` (to stop)

***

The `.emboss` command can be used to emboss a user's pfp, if user not provided then embosses the the author's pfp, followed by a few responses from the other bot