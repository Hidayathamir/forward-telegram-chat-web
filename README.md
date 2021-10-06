# forward-telegram-chat-web
Access telegram user then forward new message from `A,B,C,D,E` to `F,G,H,I,J`.

## How to run this project
1. Open my.telegram.org to get your API_ID and API_HASH then use it in `environ`.
2. run image with environment file `environ` and map port `127.0.0.1:6980:6980`.
    ```
    docker run --env-file environ -p 127.0.0.1:6980:6980 hidayathamir/forward-telegram-chat-web
    ```
