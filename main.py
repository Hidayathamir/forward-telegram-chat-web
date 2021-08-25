from os import environ
from logging import Formatter, basicConfig, getLogger, INFO
from datetime import datetime
from pytz import timezone, utc
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser
from telethon.tl.patched import Message


# ~ Enable Logging
def gmt8_time(*args):
    utc_dt = utc.localize(datetime.utcnow())
    asia = timezone('Asia/Makassar')
    converted = utc_dt.astimezone(asia)
    return converted.timetuple()


basicConfig(
    # filename='log.txt', filemode='w',
    datefmt="%Y-%m-%d %H:%M:%S",  level=INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='%(message)s',
)
LOGGER = getLogger(__name__)
Formatter.converter = gmt8_time
LOGGER.info('Log aktif, Hello Sir.')

# ~ My Constanta
# Use your own values from my.telegram.org
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
SESSION_NAME = 'development'

USERNAME_SENDER = 'proto_1bot'
USERNAME_RECEIVER = 'proto_2bot'


# ~ Start Here
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
LOGGER.info('Start client')
client.start()


@client.on(events.NewMessage(incoming=True, chats=USERNAME_SENDER))
async def main(event: events.newmessage.NewMessage.Event):
    await client.get_dialogs()
    try:
        receiver = await client.get_input_entity(USERNAME_RECEIVER)
        LOGGER.info(
            f'Got receiver ({USERNAME_RECEIVER}), forwarding message Sir.'
        )
        await forward(receiver, event.message)
    except ValueError as e:
        LOGGER.error(
            f'Sorry Sir, I can not get any user with "{USERNAME_RECEIVER}" as their '
            f'username.'
        )


async def forward(receiver: InputPeerUser, msg: Message):
    await client.send_message(receiver, msg)


client.run_until_disconnected()
LOGGER.info('Stop client')
