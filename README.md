# forward-telegram-chat-web
Access telegram user then forward new message from `A,B,C,D,E` to `F,G,H,I,J`.

## How to run this project
All you have to do is.
1. Open my.telegram.org to get your `API_ID` and `API_HASH`, create [environ](https://raw.githubusercontent.com/Hidayathamir/forward-telegram-chat-web/feature/docker/environ) file and use your `API_ID` `API_HASH`.
2. run image with environment file `environ` and map port `127.0.0.1:6980:6980`.
    ```
    docker run --env-file ./environ -p 127.0.0.1:6980:6980 hidayathamir/forward-telegram-chat-web
    ```
