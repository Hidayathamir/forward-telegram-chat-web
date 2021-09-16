# forward-telegram-chat-web
With this project, you can access telegram user then forward message from `A,B,C,D,E` to `F,G,H,I,J`.

## How to run this project
1. Download then open the project folder, and install requirement.
```
pip3 install -r requirements.txt
```

2. Open my.telegram.org to get your API_ID and API_HASH then use it in `environ.yaml`

3. Run project.
```
python3 main.py
```
![host-and-port](./README_assets/host-and-port.png)

4. Open that link.
![input-phone](./README_assets/input-phone.png)

5. Input your phone number. then click `send login code`. Telegram will sent login code to your telegram account.
![input-code](./README_assets/input-code.png)

6. Input your login code, then click `login`.
![settings](./README_assets/settings.png)

7. Chose senders and receivers. then click `start`.
![start](./README_assets/start.png)