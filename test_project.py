import pytest
from unittest.mock import patch, mock_open
from project import *
import json
import os


@patch("requests.post")
def test_check_service_status(mock_post):
    mock_post.return_value.text = "{}"  # The API returns "{}" when online
    assert UtilityFunctions.check_service_status() == "{}"


@patch("requests.post")
def test_check_service_credits(mock_post):
    mock_post.return_value.text = '{"dailyCreditsRemaining": 100}'
    credits = UtilityFunctions.check_service_credits()
    assert credits == 100


def test_programState():
    state = ProgramState()
    assert state.favorites == []
    assert state.total_balance == 0
    assert state.total_assets == {}
    assert state.coins_list == []
    assert state.populated_list == []
    assert state.deposit_history == []
    assert state.withdraw_history == []
    assert state.bought_history == []
    assert state.sold_history == []
    assert state.grand_total == 0


def test_save_state():
    state = ProgramState()
    state.total_balance = 100

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        state.save_state()

    mock_file.assert_called_once_with("state.json", "w")

    written_data = "".join(
        call_args[0][0] for call_args in mock_file().write.call_args_list
    )

    assert written_data == json.dumps(state.__dict__)


def test_load_state():
    mock_data = {
        "favorites": ["BTC", "ETH"],
        "total_balance": 200,
        "total_assets": {},
        "coins_list": [],
        "populated_list": [],
        "deposit_history": [],
        "withdraw_history": [],
        "bought_history": [],
        "sold_history": [],
        "grand_total": 0,
    }

    mock_file = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", mock_file):
        state = ProgramState()
        state.load_state()

    assert state.favorites == ["BTC", "ETH"]
    assert state.total_balance == 200
    assert state.total_assets == {}
    assert state.coins_list == []
    assert state.populated_list == []
    assert state.deposit_history == []
    assert state.withdraw_history == []
    assert state.bought_history == []
    assert state.sold_history == []
    assert state.grand_total == 0


def test_reset_state():
    state = ProgramState()
    state.total_balance = 100
    state.favorites = ["BTC"]

    ProgramState.reset_state(state)

    assert state.total_balance == 0
    assert state.favorites == []
