"""Tests for DeepSeek balance parsing."""

from __future__ import annotations

import decimal
from decimal import Decimal

import pytest

from memory_distiller.llm.deepseek_client import DeepSeekClient


class TestParseBalance:
    def test_parse_valid_balance(self) -> None:
        client = DeepSeekClient.__new__(DeepSeekClient)
        data = {
            "is_available": True,
            "balance_infos": [
                {
                    "currency": "USD",
                    "total_balance": "10.50",
                    "granted_balance": "5.00",
                    "topped_up_balance": "5.50",
                }
            ],
        }
        balance = client._parse_balance(data)
        assert balance.is_available is True
        assert len(balance.balance_infos) == 1
        assert balance.balance_infos[0].currency == "USD"
        assert balance.balance_infos[0].total_balance == Decimal("10.50")

    def test_parse_multiple_currencies(self) -> None:
        client = DeepSeekClient.__new__(DeepSeekClient)
        data = {
            "is_available": True,
            "balance_infos": [
                {
                    "currency": "USD",
                    "total_balance": "10.50",
                    "granted_balance": "5.00",
                    "topped_up_balance": "5.50",
                },
                {
                    "currency": "CNY",
                    "total_balance": "100.00",
                    "granted_balance": "50.00",
                    "topped_up_balance": "50.00",
                },
            ],
        }
        balance = client._parse_balance(data)
        assert len(balance.balance_infos) == 2
        assert balance.balance_infos[1].currency == "CNY"

    def test_parse_missing_balance_infos_returns_empty(self) -> None:
        """Missing balance_infos returns empty list, not error."""
        client = DeepSeekClient.__new__(DeepSeekClient)
        data = {"is_available": True}
        balance = client._parse_balance(data)
        assert balance.is_available is True
        assert len(balance.balance_infos) == 0

    def test_parse_invalid_number_propogates(self) -> None:
        """Invalid number in balance raises the underlying error."""
        client = DeepSeekClient.__new__(DeepSeekClient)
        data = {
            "is_available": True,
            "balance_infos": [
                {
                    "currency": "USD",
                    "total_balance": "not-a-number",
                    "granted_balance": "5.00",
                    "topped_up_balance": "5.50",
                }
            ],
        }

        with pytest.raises(decimal.InvalidOperation):
            client._parse_balance(data)
