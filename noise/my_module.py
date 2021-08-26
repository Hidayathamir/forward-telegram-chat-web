from json import load


def read_chat_id(file_path: str):
    with open(file_path) as file:
        data = load(file)

    return data


def print_chat_id(file_path: str):
    data = read_chat_id(file_path)

    for i in data:
        print(i, ':', data[i])
