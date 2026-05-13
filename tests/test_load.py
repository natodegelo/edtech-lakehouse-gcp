import importlib.util
import os
import pytest
from unittest.mock import MagicMock

spec = importlib.util.spec_from_file_location(
    "load_module",
    os.path.join(os.path.dirname(__file__), '..', 'load', 'load.py')
)
load_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(load_module)
get_latest_partition = load_module.get_latest_partition
COLLECTIONS = load_module.COLLECTIONS


class TestGetLatestPartition:

    def test_returns_none_when_no_blobs(self):
        storage_client = MagicMock()
        storage_client.list_blobs.return_value = []
        result = get_latest_partition(storage_client, "users")
        assert result is None

    def test_returns_correct_gcs_uri(self):
        storage_client = MagicMock()
        blob = MagicMock()
        blob.name = "mongodb/users/ingest_date=2024-01-15/ingest_time=020000/part-00000.ndjson"
        storage_client.list_blobs.return_value = [blob]
        result = get_latest_partition(storage_client, "users")
        assert "gs://edtech-raw-dev/mongodb/users/ingest_date=2024-01-15/ingest_time=020000" in result
        assert result.endswith("/*.ndjson")

    def test_crm_contacts_uses_crm_prefix(self):
        storage_client = MagicMock()
        blob = MagicMock()
        blob.name = "crm/contacts/ingest_date=2024-01-15/ingest_time=020000/part-00000.ndjson"
        storage_client.list_blobs.return_value = [blob]
        result = get_latest_partition(storage_client, "crm_contacts")
        assert "crm/contacts" in result

    def test_mongodb_uses_mongodb_prefix(self):
        storage_client = MagicMock()
        blob = MagicMock()
        blob.name = "mongodb/users/ingest_date=2024-01-15/ingest_time=020000/part-00000.ndjson"
        storage_client.list_blobs.return_value = [blob]
        result = get_latest_partition(storage_client, "users")
        assert "mongodb/users" in result

    def test_returns_latest_partition(self):
        storage_client = MagicMock()
        blob1 = MagicMock()
        blob1.name = "mongodb/users/ingest_date=2024-01-14/ingest_time=020000/part-00000.ndjson"
        blob2 = MagicMock()
        blob2.name = "mongodb/users/ingest_date=2024-01-15/ingest_time=020000/part-00000.ndjson"
        storage_client.list_blobs.return_value = [blob1, blob2]
        result = get_latest_partition(storage_client, "users")
        assert "2024-01-15" in result


class TestCollections:

    def test_all_21_collections_present(self):
        assert len(COLLECTIONS) == 21

    def test_crm_contacts_present(self):
        assert "crm_contacts" in COLLECTIONS

    def test_gateway_customers_present(self):
        assert "gateway_customers" in COLLECTIONS

    def test_specialization_graduates_present(self):
        assert "specialization_graduates" in COLLECTIONS

    def test_no_old_names(self):
        assert "hubspot_contacts" not in COLLECTIONS
        assert "customers_vindi" not in COLLECTIONS
        assert "aprovados_especializacao" not in COLLECTIONS
        assert "csacademy_plans" not in COLLECTIONS