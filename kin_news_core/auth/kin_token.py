from kin_news_core.exceptions import AuthenticationFailedError


def decode_kin_token(header: str) -> str:
    split_token = header.split()

    if len(split_token) != 2:
        raise AuthenticationFailedError("Invalid token format!")

    return split_token[1]
