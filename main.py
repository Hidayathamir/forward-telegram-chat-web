from os.path import dirname, abspath, join
from yaml import safe_load
from logging import Formatter, basicConfig, getLogger, INFO
from typing import Union, List, Dict
from datetime import datetime
from pytz import timezone, utc
from hypercorn.asyncio import serve
from hypercorn.config import Config
from quart.wrappers.response import Response
from werkzeug.datastructures import MultiDict
from quart import Quart, redirect, render_template, flash, url_for, request
from telethon import TelegramClient
from telethon.events import newmessage
from telethon.events import NewMessage
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    FloodWaitError,
)
from telethon.tl.types import Channel, Chat, User


# region Constants
DIRNAME_LOCATION = dirname(abspath(__file__))


def get_environ() -> Dict[str, str]:
    yaml_location = join(DIRNAME_LOCATION, "environ.yaml")
    with open(yaml_location, "r", encoding="utf-8") as yaml_file:
        environ = safe_load(yaml_file)
    return environ


environ = get_environ()


# my.telegram.com
API_ID = int(environ["API_ID"])
API_HASH = environ["API_HASH"]

# Telethon client
SESSION = join(DIRNAME_LOCATION, environ["SESSION"])
client = TelegramClient(SESSION, API_ID, API_HASH)

# Quart app
app = Quart(__name__)
app.secret_key = environ["SECRET_KEY"]

# Hypercorn (ASGI)
HYPERCORN_CONFIG = Config.from_mapping({"bind": environ["HOST:PORT"]})

# General constants
CHAT_ID_SENDERS: List[int] = []
CHAT_ID_RECEIVERS: List[int] = []

ROUTE_INDEX = "/"
ROUTE_LOGIN_PHONE = "/login/phone/"
ROUTE_LOGIN_CODE = "/login/code/"
ROUTE_LOGOUT = "/logout/"
ROUTE_SETTINGS = "/settings/"
ROUTE_START = "/settings/start/"
ROUTE_STOP = "/settings/stop/"

TEMPLATE_LOGIN_CODE = "login_code.html"
TEMPLATE_LOGIN_PHONE = "login_phone.html"
TEMPLATE_SETTINGS = "settings.html"
TEMPLATE_START = "start.html"

FORM_NAME_PHONE = "phone"
FORM_NAME_CODE = ["first", "second", "third", "fourth", "fifth"]
FORM_NAME_NEW_SENDERS = "new_senders"
FORM_NAME_NEW_RECEIVERS = "new_receivers"
# endregion


# region Enable Logging
def gmt8_time(*args):
    utc_dt = utc.localize(datetime.utcnow())
    asia = timezone("Asia/Makassar")
    converted = utc_dt.astimezone(asia)
    return converted.timetuple()


basicConfig(
    filename=join(DIRNAME_LOCATION, f"{SESSION}.log"),
    filemode="w",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
Formatter.converter = gmt8_time
LOGGER = getLogger(__name__)
LOGGER.setLevel(INFO)
LOGGER.info("The log is active, Hello Sir.")
# endregion


# region Third Function
async def main() -> None:
    await serve(app, HYPERCORN_CONFIG)


@app.before_serving
async def startup() -> None:
    """Connect the client before we start serving with Quart"""
    await client.connect()


@app.after_serving
async def cleanup() -> None:
    """After we're done serving (near shutdown), clean up the client"""
    await client.disconnect()


async def get_name_or_title(entity: Union[Channel, User, Chat]) -> str:
    """Return name or title from entity"""
    name = ""
    try:
        name = combine_first_name_and_last_name(
            entity.first_name, entity.last_name
        )
    except AttributeError:
        name = entity.title
    return name


async def forward(event: newmessage.NewMessage.Event) -> None:
    """
    Iterate CHAT_ID_RECEIVERS, then get_entity,
    then log, then send_message that we got from sender.
    if receiver not found in get_entity, then log.
    """
    chat = await event.get_chat()
    sender_name = await get_name_or_title(chat)

    for chat_id_receiver in CHAT_ID_RECEIVERS:
        try:
            receiver = await client.get_entity(chat_id_receiver)
            receiver_name = await get_name_or_title(receiver)
            LOGGER.info(f"Forward from {sender_name} to {receiver_name}.")
            await client.send_message(receiver, event.message)
        except ValueError as e:
            LOGGER.info(f"receiver not found, {repr(e)}.")


def combine_first_name_and_last_name(
    fn: Union[str, None], ln: Union[str, None]
) -> str:
    """Combine first name with last name then strip space"""
    fn = "" if (fn is None) else fn
    ln = "" if (ln is None) else ln
    return f"{fn} {ln}".strip()


def new_message_from_senders() -> NewMessage:
    """Got new message from senders"""
    return NewMessage(
        incoming=True,
        chats=CHAT_ID_SENDERS,
    )


async def get_detail_me() -> str:
    me = await client.get_me()
    name = await get_name_or_title(me)
    un = "nousername" if me.username is None else me.username
    pn = "nophone" if me.phone is None else me.phone
    return f"{name} (@{un}) (+{pn})"


# endregion


# region Second Function
def client_is_connected():
    """
    if client is connected: run func
    else: connect client then redirect ROUTE_LOGIN_PHONE
    """

    def wrapper(func):
        async def wrapped(*args):
            global client
            if client.is_connected():
                return await func(*args)
            client = TelegramClient(SESSION, API_ID, API_HASH)
            await client.connect()
            return redirect(url_for("login_phone"))

        return wrapped

    return wrapper


def client_is_login():
    """
    if client is login: run func
    else: redirect to ROUTE_LOGIN_PHONE
    """

    def wrapper(func):
        async def wrapped(*args):
            if await client.is_user_authorized():
                return await func(*args)
            return redirect(url_for("login_phone"))

        return wrapped

    return wrapper


def client_is_not_login():
    """
    if client is not login: run func
    else: redirect ROUTE_SETTINGS
    """

    def wrapper(func):
        async def wrapped(*args):
            if not await client.is_user_authorized():
                return await func(*args)
            return redirect(url_for("settings"))

        return wrapped

    return wrapper


def is_client_have_event_handlers() -> bool:
    """Return boolean whether client have event handlers or not"""
    if len(client.list_event_handlers()) != 0:
        return True
    return False


def client_have_event_handlers():
    """
    if client have event handlers: run func
    else: redirect ROUTE_SETTINGS
    """

    def wrapper(func):
        async def wrapped(*args):
            if is_client_have_event_handlers():
                return await func(*args)
            return redirect(url_for("settings"))

        return wrapped

    return wrapper


def client_have_not_event_handlers():
    """
    if client have not event handlers: run func
    else: redirect ROUTE_START
    """

    def wrapper(func):
        async def wrapped(*args):
            if not is_client_have_event_handlers():
                return await func(*args)
            return redirect(url_for("start"))

        return wrapped

    return wrapper


def change_senders(new_senders: List[int]) -> None:
    """Change global variable CHAT_ID_SENDERS to new_senders"""
    global CHAT_ID_SENDERS
    CHAT_ID_SENDERS = new_senders


def change_receivers(new_receivers: List[int]) -> None:
    """Change global variable CHAT_ID_RECEIVERS to new_receivers"""
    global CHAT_ID_RECEIVERS
    CHAT_ID_RECEIVERS = new_receivers


async def get_senders_name() -> List[str]:
    """
    Iterate CHAT_ID_SENDERS, then get_entity,
    if found then combine first name and last name, then append to senders list,
    then return senders list, if not found in get_entity then log.
    """
    senders: List[str] = []
    for chat_id_sender in CHAT_ID_SENDERS:
        try:
            sender = await client.get_entity(chat_id_sender)
            sender_name = await get_name_or_title(sender)
            senders.append(sender_name)
        except ValueError as e:
            LOGGER.error(f"Sender not found, {repr(e)}.")
    return senders


async def get_receivers_name() -> List[str]:
    """
    Iterate CHAT_ID_RECEIVERS, then get_entity,
    if found then combine first name and last name, then append to receivers list,
    then return receivers list, if not found in get_entity then log.
    """
    receivers: List[str] = []
    for chat_id_receiver in CHAT_ID_RECEIVERS:
        try:
            receiver = await client.get_entity(chat_id_receiver)
            receiver_name = await get_name_or_title(receiver)
            receivers.append(receiver_name)
        except ValueError as e:
            LOGGER.error(f"receiver not found, {repr(e)}.")
    return receivers


def remove_all_event_handlers() -> None:
    """
    Iterate through all list event handlers then
    remove it
    """
    LOGGER.info("Remove all event handlers.")
    for callback, _ in client.list_event_handlers():
        client.remove_event_handler(callback)


def add_event_forward() -> None:
    """Add event handler if we got new message from senders"""
    LOGGER.info("Add event forward.")
    client.add_event_handler(
        forward,
        new_message_from_senders(),
    )


def is_form_code_valid(form: MultiDict) -> bool:
    """Return boolean whether form code is valid or not"""
    is_valid = True
    for form_name in FORM_NAME_CODE:
        if form_name not in form:
            is_valid = False
            break
    return is_valid


def get_code_from_form(form: MultiDict) -> str:
    """Get code from form"""
    code = ""
    for i in FORM_NAME_CODE:
        code += form[i]
    return code


def is_form_phone_valid(form: MultiDict) -> bool:
    """Return boolean whether form phone is valid or not"""
    return FORM_NAME_PHONE in form


def get_phone_from_form(form: MultiDict) -> str:
    """Get code from form"""
    return "+62" + form[FORM_NAME_PHONE]


def get_list_from_form(form: MultiDict, who: str) -> List[int]:
    """Get list from form according to who"""
    get_who = form.getlist(who)
    return [int(i) for i in get_who]


async def get_chat_id() -> Dict[int, str]:
    """Iterate dialogs to get dialog id and dialog name"""
    chat_id: Dict[int, str] = {}
    async for dialog in client.iter_dialogs():
        chat_id[dialog.id] = dialog.name
    return chat_id


async def try_send_code_request(phone_num: str) -> Union[str, Response]:
    """
    Try to send code request to phone_num then redirect to ROUTE_LOGIN_CODE,
    if typeerror or phone number invalid or too many request
    then show error.
    """
    try:
        await client.send_code_request(phone_num)
    except TypeError as e:
        LOGGER.error(f"error code: a1, {repr(e)}.")
        return f"error code: a1, {repr(e)}."
    except PhoneNumberInvalidError as e:
        LOGGER.error(f"error code: a2, {repr(e)}.")
        return f"error code: a2, {repr(e)}."
    except FloodWaitError as e:
        LOGGER.error(f"error code: a3, {repr(e)}.")
        return "Too many code requests, wait a minute."
    LOGGER.info(f"{phone_num} ask code request.")
    return redirect(url_for("login_code"))


async def try_sign_in(code: str) -> Union[str, Response]:
    """
    Try to sign in, then log, then redirect to ROUTE_SETTINGS
    if password needed, show error
    if wrong code, redirect to ROUTE_LOGIN_CODE with message
    if have not enter phone number, redirect to ROUTE_LOGIN_PHONE with message
    """
    try:
        await client.sign_in(code=code)
    except SessionPasswordNeededError as e:
        LOGGER.error(f"error code: b1, {repr(e)}.")
        return f"error code: b1, {repr(e)}."
    except PhoneCodeInvalidError as e:
        LOGGER.error(f"error code: b2, {repr(e)}.")
        await flash("Wrong code.")
        return redirect(url_for("login_code"))  # wrong code
    except ValueError as e:
        LOGGER.error(f"error code: b3, {repr(e)}.")
        await flash("Please enter your phone number.")
        return redirect(url_for("login_phone"))  # Haven't entered phone number
    detail_me = await get_detail_me()
    LOGGER.info(f"Client sign in. {detail_me}.")
    return redirect(url_for("settings"))


async def log_out() -> None:
    """Log user out"""
    detail_me = await get_detail_me()
    LOGGER.info(f"Client log out. {detail_me}.")
    await client.log_out()


# endregion


# region Main Function
@app.route(ROUTE_INDEX, endpoint="index")
async def index() -> Response:
    return redirect(url_for("settings"))


@app.route(ROUTE_LOGIN_PHONE, methods=["GET", "POST"], endpoint="login_phone")
@client_is_connected()
@client_is_not_login()
async def login_phone() -> Union[str, Response]:
    if request.method == "GET":
        return await render_template(
            TEMPLATE_LOGIN_PHONE,
            FORM_NAME_PHONE=FORM_NAME_PHONE,
        )
    if request.method == "POST":
        form = await request.form
        if is_form_phone_valid(form):
            phone_num = get_phone_from_form(form)
            return await try_send_code_request(phone_num)
        return "Phone num not found in form."
    return "Method Not Allowed."


@app.route(ROUTE_LOGIN_CODE, methods=["GET", "POST"], endpoint="login_code")
@client_is_connected()
@client_is_not_login()
async def login_code() -> Union[str, Response]:
    if request.method == "GET":
        return await render_template(
            TEMPLATE_LOGIN_CODE,
            FORM_NAME_CODE=FORM_NAME_CODE,
        )
    if request.method == "POST":
        form = await request.form
        if is_form_code_valid(form):
            code = get_code_from_form(form)
            return await try_sign_in(code)
        return "Form not valid."
    return "Method Not Allowed."


@app.route(ROUTE_LOGOUT, endpoint="logout")
@client_is_connected()
@client_is_login()
async def logout() -> Response:
    await log_out()
    return redirect(url_for("login_phone"))


@app.route(ROUTE_SETTINGS, endpoint="settings")
@client_is_connected()
@client_is_login()
@client_have_not_event_handlers()
async def settings() -> str:
    chat_id = await get_chat_id()
    return await render_template(
        TEMPLATE_SETTINGS,
        chat_id=chat_id,
        FORM_NAME_NEW_SENDERS=FORM_NAME_NEW_SENDERS,
        FORM_NAME_NEW_RECEIVERS=FORM_NAME_NEW_RECEIVERS,
    )


@app.route(ROUTE_START, methods=["GET", "POST"], endpoint="start")
@client_is_connected()
@client_is_login()
async def start() -> Union[Response, str]:
    if request.method == "GET":
        if not is_client_have_event_handlers():
            return redirect(url_for("settings"))

    if request.method == "POST":
        form = await request.form
        new_senders = get_list_from_form(form, FORM_NAME_NEW_SENDERS)
        new_receivers = get_list_from_form(form, FORM_NAME_NEW_RECEIVERS)
        change_senders(new_senders)
        change_receivers(new_receivers)
        remove_all_event_handlers()
        add_event_forward()

    data: Dict[str, List[str]] = {}
    data["senders"] = await get_senders_name()
    data["receivers"] = await get_receivers_name()
    return await render_template(TEMPLATE_START, data=data)


@app.route(ROUTE_STOP, endpoint="stop")
@client_is_connected()
@client_is_login()
@client_have_event_handlers()
async def stop() -> Response:
    remove_all_event_handlers()
    return redirect(url_for("settings"))


# endregion


if __name__ == "__main__":
    client.loop.run_until_complete(main())
