import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from ingest import validate_record, add_metadata, INGEST_STRATEGY


class TestValidateRecord:

    def test_valid_user(self):
        record = {"userId": "123", "email": "test@test.com", "createdAt": "2024-01-01"}
        is_valid, reason = validate_record(record, "users")
        assert is_valid is True
        assert reason == ""

    def test_missing_required_field(self):
        record = {"userId": "123", "createdAt": "2024-01-01"}  # missing email
        is_valid, reason = validate_record(record, "users")
        assert is_valid is False
        assert "email" in reason

    def test_null_required_field(self):
        record = {"userId": "123", "email": None, "createdAt": "2024-01-01"}
        is_valid, reason = validate_record(record, "users")
        assert is_valid is False

    def test_unknown_collection(self):
        record = {"any_field": "value"}
        is_valid, reason = validate_record(record, "unknown_collection")
        assert is_valid is True

    def test_valid_scores(self):
        record = {"scoreId": "abc", "userId": "123", "score": 10}
        is_valid, reason = validate_record(record, "scores")
        assert is_valid is True

    def test_valid_crm_contacts(self):
        record = {"hubspot_id": "999", "email": "test@test.com"}
        is_valid, reason = validate_record(record, "crm_contacts")
        assert is_valid is True


class TestAddMetadata:

    def test_metadata_fields_added(self):
        record = {"userId": "123"}
        result = add_metadata(record, "users", "2024-01-15", "020000")
        assert "_ingest_timestamp" in result
        assert result["_ingest_date"] == "2024-01-15"
        assert result["_ingest_time"] == "020000"
        assert result["_source"] == "mongodb"
        assert result["_collection"] == "users"

    def test_ingest_strategy_added(self):
        record = {"userId": "123"}
        result = add_metadata(record, "audittraffics", "2024-01-15", "020000")
        assert result["_ingest_strategy"] == "append"

    def test_snapshot_strategy(self):
        record = {"userId": "123"}
        result = add_metadata(record, "users", "2024-01-15", "020000")
        assert result["_ingest_strategy"] == "snapshot"

    def test_scd2_strategy(self):
        record = {"userId": "123"}
        result = add_metadata(record, "userplans", "2024-01-15", "020000")
        assert result["_ingest_strategy"] == "scd2"

    def test_original_fields_preserved(self):
        record = {"userId": "123", "email": "test@test.com"}
        result = add_metadata(record, "users", "2024-01-15", "020000")
        assert result["userId"] == "123"
        assert result["email"] == "test@test.com"


class TestIngestStrategy:

    def test_all_collections_have_strategy(self):
        from ingest import SCHEMA_REQUIRED_FIELDS
        for collection in SCHEMA_REQUIRED_FIELDS:
            assert collection in INGEST_STRATEGY, f"{collection} missing from INGEST_STRATEGY"

    def test_valid_strategies(self):
        valid = {"snapshot", "append", "scd2", "merge", "checkpoint"}
        for collection, strategy in INGEST_STRATEGY.items():
            assert strategy in valid, f"{collection} has invalid strategy: {strategy}"