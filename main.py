# region Import
from os import environ
from logging import Formatter, basicConfig, getLogger, INFO, ERROR
from datetime import datetime
from pytz import timezone, utc
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import InputPeerUser
from telethon.tl.patched import Message
from noise.my_module import read_chat_id
# endregion


# region Enable Logging
def gmt8_time(*args):
    utc_dt = utc.localize(datetime.utcnow())
    asia = timezone('Asia/Makassar')
    converted = utc_dt.astimezone(asia)
    return converted.timetuple()


basicConfig(
    # filename='log.txt', filemode='w',
    datefmt="%Y-%m-%d %H:%M:%S", level=ERROR,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format='%(levelname)s - %(message)s',
)
Formatter.converter = gmt8_time
LOGGER = getLogger(__name__)
LOGGER.setLevel(INFO)
print('\n')
LOGGER.info('Log aktif, Hello Sir.')
# endregion

# region My Constanta
# ~ Use your own values from my.telegram.org
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
SESSION_NAME = 'development'
# ~ My things
CHAT_ID_SENDER = read_chat_id('noise/chat_id_senders.json')
CHAT_ID_RECEIVERS = read_chat_id('noise/chat_id_receivers.json')
# endregion

# region The Party
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
LOGGER.info('Start client')
client.start()


@client.on(NewMessage(incoming=True, chats=CHAT_ID_SENDER))
async def main(event: NewMessage.Event):
    for chat_id_receiver in CHAT_ID_RECEIVERS:
        try:
            receiver = await client.get_input_entity(chat_id_receiver)
            logsuc(chat_id_receiver)
            await forward(receiver, event.message)
        except ValueError:
            logerr(chat_id_receiver)
# endregion


# region All Function
async def forward(receiver: InputPeerUser, msg: Message):
    await client.send_message(receiver, msg)


def logsuc(chat_id_receiver):
    LOGGER.info(
        f'Got receiver ({chat_id_receiver}), forwarding message Sir.'
    )


def logerr(chat_id_receiver):
    LOGGER.error(
        'Sorry Sir, I don not think you have any chat with chat_id '
        f'"{chat_id_receiver}". I suggest you to run '
        'write_chat_id.py to show your history chat_id.'
    )
# endregion


# region Run
client.run_until_disconnected()
LOGGER.info('Stop client')
# endregion
