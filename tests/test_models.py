import sys
import os
import pytest
from pydantic import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from models import EnginePayload

def test_engine_payload_valid():
    payload = EnginePayload(event_type="UNIT_TEST", description="Test unitario superato.")
    assert payload.event_type == "UNIT_TEST"
    assert payload.description == "Test unitario superato."

def test_engine_payload_invalid():
    with pytest.raises(ValidationError):
        EnginePayload(event_type="INVALID_TEST")