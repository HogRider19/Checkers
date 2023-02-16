from json import dumps

import pytest

from checkers.enums import ClientMessageType as ClientType
from checkers.websockets import serialize_client_message


@pytest.mark.parametrize('message, type', [
    (dumps({'type': "0", 'message': "1234"}), ClientType.GetMyFigureType),
    (dumps({'type': "1", 'message': "1234"}), ClientType.GetBoard),
    (dumps({'type': "2", 'message': "1234"}), ClientType.MakeMove),
    (dumps({'type': "wj", 'message': "1234"}), None),
    (dumps({'type': "100", 'message': "1234"}), None),
    (dumps({'message': "1234"}), None),
])
def test_client_message_type(message: str, type: ClientType):
    msg = serialize_client_message(message)
    if msg is None:
        assert msg == type
    else:
        assert msg.get('type') == type