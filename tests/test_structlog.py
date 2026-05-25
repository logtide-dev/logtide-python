from typing import Any
from unittest.mock import ANY, MagicMock

import pytest
from freezegun import freeze_time

from logtide_sdk.client import LogTideClient
from logtide_sdk.enums import LogLevel
from logtide_sdk.models import LogEntry
from logtide_sdk.structlog import LogTideProcessor

# here i used freeze_time from freezegun, since time is auto fetched.
# and no logic in processor to include the time.


@freeze_time()
def test_calls_empty_event_dict() -> None:
    mock_client = MagicMock(spec=LogTideClient)

    processor = LogTideProcessor(client=mock_client, service="fragapi")
    event_dict = {}

    processor(ANY, ANY, event_dict=event_dict)

    mock_client.log.assert_called_once_with(
        entry=LogEntry(
            service="fragapi", level=LogLevel.INFO, message="structlog event", metadata={}
        )
    )


@pytest.mark.parametrize(
    "invalid_exc_info", ["Just random String", ("tuple", "THISISNOTERROR", "objects"), 1337]
)
def test_raises_if_exc_info_but_unknown_type(invalid_exc_info: Any) -> None:
    mock_client = MagicMock(spec=LogTideClient)

    processor = LogTideProcessor(client=mock_client, service="fragapi")
    event_dict = {"exc_info": invalid_exc_info}

    with pytest.raises(TypeError):
        processor(ANY, ANY, event_dict=event_dict)

    mock_client.log.assert_not_called()


@freeze_time()
def test_does_not_include_basic_fields_in_metadata() -> None:
    mock_client = MagicMock(spec=LogTideClient)

    processor = LogTideProcessor(client=mock_client, service="tumbleweed")
    event_dict = {
        "level": "DEBUG",
        "event": "My custom event text",
        "valid_metadata": True,
        "other": 25.25,
    }

    processor(ANY, ANY, event_dict=event_dict)

    mock_client.log.assert_called_once_with(
        entry=LogEntry(
            service="tumbleweed",
            level=LogLevel.DEBUG,
            message="My custom event text",
            metadata={"valid_metadata": True, "other": 25.25},
        )
    )


@freeze_time()
def test_maps_structlog_warning_to_warn() -> None:
    mock_client = MagicMock(spec=LogTideClient)

    processor = LogTideProcessor(client=mock_client, service="servicename")
    event_dict = {
        "level": "WARNING",
        "event": "log message",
    }

    processor(ANY, ANY, event_dict=event_dict)

    mock_client.log.assert_called_once_with(
        entry=LogEntry(
            service="servicename",
            level=LogLevel.WARN,
            message="log message",
            metadata={},
        )
    )
