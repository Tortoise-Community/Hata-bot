# team-maple

Team Maple bot.

## Requirements

At least Python 3.8 is required.

All required libraries are listed in `requirements.txt`

## Configuration

> At least two clients must be provided

Done via enviroment variables, also through a `.env` file

Copy the `.env-example` to `.env` and fill in the values accordingly

Additionally, one can provide the same information as `dict`s to to the `CLIENT_INFO` list in `env.py`

> Enviroment variables take precedence over `CLIENT_INFO` from `env.py`

There are very few configurable values that don't directly apply to an invidividual client:

- `CLIENT_PREFIX`
  - The default prefix to give to all clients that don't have one directly provided

***

Each client can has four configurable values:

- `ID`
  - ID of the client user
- `TOKEN`
  - Discord API bot token
- `PREFIX`
  - The prefix for this client
  - If not provided, defaults to the default prefix
- `POTATO_CHANNEL_ID`
  - ID of the channel the bot can play Hot Potato in
  - Is optional, can be left absent

### Examples

> Both of these examples represent identical configurations

#### .env

```bash
CLIENT_PREFIX=m.

CLIENT_IDS=12345,67890
CLIENT_TOKENS=abcdefghi,jklmnopqr
CLIENT_PREFIXES=abcdef,
POTATO_CHANNEL_IDS=,67890
```

#### env.py

```python
PREFIX = 'm.'

CLIENT_INFO: List[ClientInfoDict] = [{
  'ID': 12345,
  'TOKEN': 'abcdefghi',
  'PREFIX': 'abcdef',
}, {
  'ID': 67890,
  'TOKEN': 'jklmnopqr',
  'POTATO_CHANNEL_ID': 67890
}]
```

## Running

The bot can be started by executing `main.py`, for example:

```bash
python3.8 main.py
```

If everything is configured correctly, you'll see something like this:

```shell
Attemping to create 2 MapleClients...
Connecting...

        <Client name='FirstClient#1234', id=12345>
Prefix        : abcdef
Potato Channel: None

        <Client name='SecondClient#5678', id=67890>
Prefix        : m.
Potato Channel: <ChannelText id=67890, name='second-channel'>

All clients logged in
```

***

Otherwise, there are various errors that can appear:

- `No clients found in enviroment variables or env.py`
  - No client informatino was loaded either from `env.py`, or via enviroment variables
  - At the very minimum, one client token and ID is required
- `Number of Client IDs and Tokens must be equal`
  - Client information was loaded, but there's been a mismatch between the number of IDs and tokens

## Extensions

### Hot Potato

Allows for playing of Hot Potato between all the attached clients

#### Commands

- `potato [guild=current] [human_only=false]`
  - Spawns a hot potato
  - If guild is not provided, spawns it in the current guild
  - A truthy value can be provided to make it so only humans can play
- `toss`
  - Tosses a potato from the current channel to another one

#### Walkthrough

While all clients can toss the potato if visible, only those provided with potato channel IDs can participate - so if there are not at least two clients with potato IDs, the game cannot be played.

> Only one hot potato can be active at a time

In the channel of an active hot potato, you can run `.toss` to throw the hot potato to another potato channel

> If other clients can see the active hot potato channel, they too will attempt to run `.toss` in time

Once the potato explodes, the game is over!

### Misc

Contains various one-off commands that don't deserve their own extension

#### Commands

- `cleartext`
  - Deletes all non-pinned messages in the current channel
  - Only usable by Owner
- `ping`
  - Outputs a `Pong` message with the client(s) latency in `ms`

#### Walkthrough

For only the first client, it will attempt to convert the message content to a color, and if successful display said color.

Colors can be provided in various formats:

- `0xRRGGBB`
  - `0xdaa520`
- `#RRGGBB`
  - `#daa520`
- `#RGB`
  - `#da2`
- [HTML name](https://drafts.csswg.org/css-color-4/#named-colors)
  - `goldenrod`
- `rgb(R, G, B)`
  - `rgb(218, 165, 32)`
- `rgba(R, G, B, A)`
  - `rgba(218, 165, 32, 255)`
- `hsl(H, S%, L%)`
  - `hsl(43, 74.4%, 49%)`
- `hsv(H, S, V)`
  - `hsv(43, 85.3%, 85.5%)`

### Number Guessing

Allows for playing of a number guessing game - one user thinks of another, while another guesses, and the initial user responds if the guessed number is too high, too low, or correct!

#### Commands

- `guess_number [lowest=1] [highest=10]`
  - Start a number guessing game
  - The random number is generated between `lowest` and `highest`

#### Walkthrough

> If other clients can see the number-guessing prompt, they will attempt to play the game too

Users can play this game with directly with clients in the same channel by stating `I'm thinking of a number between 1 and 10` - with `1` and `10` being any number they want - and responding with `hith` or `low` depending on the guessed number

When the number is correctly guessed, the user respond with a message containing `guessed` to tell the bot it's been guessed!

### Knock Knock

Allows for the telling of knock-knock jokes

#### Commands

- `knock_knock [human_only=false]`
  - Starts telling a random knock knock joke
  - A truthy value can be provided to make it so only humans can play

#### Walkthrough

> If other clients can see the `Knock Knock` text, they will respond accordingly

Players can also tell Knock Knock jokes directly to any visible clients by saying `Knock Knock`, then the setup phrase, and finally the punchline.

### Hangman

Allows playing Hangman with users or bots

#### Commands

- `hangman [human_only=false] [guessing_word=random]`
  - Prompts to start a game of hangman
  - A truthy value can be provided to make it so only humans can play
  - If no word is provided, randomly use one from the wordlist

#### Walkthrough

> If other clients can see the hangman prompt, they will try to play

While a game is active, the player can enter single letters to guess - depending on the correctness, the letter will be revealed or they will lose a life

***

Dictionary of words to choose from is sourced from:

- https://raw.githubusercontent.com/michaeldickens/Hangman/master/wordlist.txt
- https://raw.githubusercontent.com/Tom25/Hangman/master/wordlist.txt
- https://raw.githubusercontent.com/Xethron/Hangman/master/words.txt

### Fun

Various fun features

#### Commands

- `emb [user=author]`
  - Takes a users profile picture and embosses it
  - If no user is provided, use the command executor
- `talk [signal]`
  - Have the clients talk to eachother like chatbots
  - In order to stop, `stop', 'shutup', 'shut` must be provided as `signal`
