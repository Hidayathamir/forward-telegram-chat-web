from telethon import TelegramClient
from os import environ
from json import dump
from my_module import print_chat_id


def write_chat_id():
    # Remember to use your own values from my.telegram.org!
    API_ID = int(environ['API_ID'])
    API_HASH = environ['API_HASH']
    SESSION_NAME = 'development'
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    FILE_NAME = 'noise/chat_id_all.json'

    async def main():
        chat_id = {}

        async for dialog in client.iter_dialogs():
            chat_id[dialog.id] = dialog.name

        with open(FILE_NAME, 'w', encoding='utf-8') as file:
            dump(chat_id, file)

    with client:
        client.loop.run_until_complete(main())

    print_chat_id(FILE_NAME)


if __name__ == '__main__':
    write_chat_id()
