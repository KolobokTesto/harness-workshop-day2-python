import json


def log_response(response):
    line = {
        "tools": [
            f"{call['tool']} (помилка)" if call["isError"] else call["tool"]
            for call in response["toolCalls"]
        ],
        "totalTokens": response["usage"]["totalTokens"],
    }
    print(json.dumps(line, ensure_ascii=False))
