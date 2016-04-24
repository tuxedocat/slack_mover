#!/usr/bin/env python3

import json
import time
from datetime import datetime
import click
import logging
from typing import Tuple, List, Dict, AnyStr, Any, Callable, Mapping, Iterable, Union, Optional
from slackclient import SlackClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def initialize(token: str = None, token_file: str = None) -> SlackClient:
    """Returns SlackClient for given API-Token"""
    if token:
        apitoken = token
    elif token_file:
        with open(token_file) as f:
            apitoken = f.read().strip()
    else:
        raise ValueError('Specify api-token as argument, or path to text file contains api-token')

    try:
        client = SlackClient(apitoken)
        logger.debug(client.api_call('api.test'))
    except:
        raise
    finally:
        return client


def _get_channel_id(dic: Dict = None, name: str = None) -> Optional[str]:
    """Get id corresponding to channel from given dict
    """
    channels = dic.get('channels', dic.get('groups'))

    for channel in channels:
        if channel.get('name') == name:
            return channel.get('id')
        else:
            pass

    return None


def get_channel_id(client: SlackClient = None, name: str = None) -> Tuple[str, str]:
    """Get channel-id of given chanel name

    Returns
    -------
    Tuple[str, str]
        ('channel-id', 'private' or 'public')

    """
    publics = json.loads(client.api_call('channels.list').decode())
    channel_id = _get_channel_id(publics, name)

    if channel_id:
        return (channel_id, 'public')
    else:
        privates = json.loads(client.api_call('groups.list').decode())
        channel_id = _get_channel_id(privates, name)
        return (channel_id, 'private') if channel_id else (None, None)


def get_all_messages_from_channel(client: SlackClient = None, channel: str = None,
                                  channel_type: str = None, **kwargs) -> List[Dict]:
    """Get messages from given channel, returns as list of messages (dict)
    """
    if channel_type == 'public':
        _api_call = 'channels.history'
    elif channel_type == 'private':
        _api_call = 'groups.history'
    else:
        raise ValueError

    _messages = []
    messages_dict = json.loads(client.api_call(_api_call, channel=channel, count=1000).decode())
    _messages.extend(messages_dict.get('messages'))
    return _messages


def post_message(client: SlackClient = None, msg: Dict = None, to: str = None) -> bool:
    if not to:
        raise ValueError

    def _post_msg(msg):
        _response = client.api_call('chat.postMessage', channel=to,
                                    text=msg.get('text'), attachments=msg.get('attachments'),
                                    as_user=True)
        if isinstance(_response, bytes):
            _response = _response.decode()
        response = json.loads(_response)
        return response

    _org_ts = datetime.fromtimestamp(float(msg.get('ts')))
    org_ts = _org_ts.isoformat()

    _ = _post_msg(msg={'text': ':timer_clock: {}'.format(org_ts)})
    response = _post_msg(msg)

    return response.get('ok')


def copy_messages(channel_from: str = None, channel_to: str = None, token: str = None, token_file: str = None):
    client = initialize(token, token_file)
    id_from, channel_type_from = get_channel_id(client, channel_from)
    id_to, channel_type_to = get_channel_id(client, channel_to)

    msgs = get_all_messages_from_channel(client, id_from, channel_type_from)
    save_messages(msgs, 'archive_channel={}'.format(channel_from))

    for msg in sorted(msgs, key=lambda x: x['ts']):
        post_message(client, msg, id_to)
        time.sleep(0.5)

    return None


def save_messages(messages: List[Dict] = None, file: str = None) -> None:
    """Save list of message (dict) as a json file

    Raises
    ------
    OSError, IOError
    """
    with open(file + '.json', 'w') as f:
        json.dump(messages, f)


@click.group()
def cli():
    pass


@cli.command(help='CHANNEL: Name of channel to create local archive')
@click.argument('channel')
@click.option('--token', type=str, default=None)
def archive(channel, token):
    client = initialize(token)
    encoded_id, channel_type = get_channel_id(client, channel)
    messages = get_all_messages_from_channel(client, encoded_id, channel_type)
    save_messages(messages, 'archive_channel={}'.format(channel))
    click.echo('Done')


@cli.command()
@click.argument('channel_from')
@click.argument('channel_to')
@click.option('--token', type=str, default=None)
def mirror(channel_from, channel_to, token):
    copy_messages(channel_from, channel_to, token)
    click.echo('Done')


if __name__ == '__main__':
    cli()
