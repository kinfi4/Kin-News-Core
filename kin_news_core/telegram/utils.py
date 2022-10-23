from string import Template


def compose_channel_link(channel_name: str) -> str:
    link_template = Template('https://t.me/${channel_name}')

    return link_template.substitute(channel_name=channel_name)


def compose_message_link(channel_name: str, message_id: int) -> str:
    link_template = Template('https://t.me/${channel_name}/${message_id}')

    return link_template.substitute(channel_name=channel_name, message_id=message_id)


def compose_participants_count(participants_number: int) -> str:
    if participants_number < 10_000:
        return str(participants_number)

    if participants_number < 1_000_000:
        return f'{participants_number // 1000}K'

    return f'{round(participants_number / 1_000_000, 1)}M'
