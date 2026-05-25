"""
PROJ-01 Tests — Phase 2: Automated validation for core logic.
5 valid JSON requests + 5 malformed JSON requests.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Health check ─────────────────────────────────────────────
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── 5 Valid JSON requests ───────────────────────────────────
def test_valid_simple_object():
    r = client.post("/json/format", json={"raw": '{"name":"Alice","age":30}'})
    assert r.json()["success"] is True
    assert "name" in r.json()["data"]


def test_valid_nested_object():
    r = client.post("/json/format", json={"raw": '{"user":{"name":"Bob","roles":["admin","user"]}}'})
    assert r.json()["success"] is True


def test_valid_array():
    r = client.post("/json/format", json={"raw": '[1,2,3,{"key":"value"}]'})
    assert r.json()["success"] is True


def test_valid_parse_metadata():
    r = client.post("/json/parse", json={"raw": '{"a":1,"b":2}'})
    data = r.json()
    assert data["success"] is True
    assert data["data"]["top_level_keys"] == 2


def test_valid_empty_object():
    r = client.post("/json/format", json={"raw": "{}"})
    assert r.json()["success"] is True


# ── 5 Malformed JSON requests ───────────────────────────────
def test_malformed_trailing_comma():
    r = client.post("/json/format", json={"raw": '{"name":"Alice",}'})
    data = r.json()
    assert data["success"] is False
    assert data["error_line"] is not None


def test_malformed_missing_quote():
    r = client.post("/json/format", json={"raw": '{"name:Alice}'})
    data = r.json()
    assert data["success"] is False
    assert data["error_line"] is not None


def test_malformed_extra_comma():
    r = client.post("/json/format", json={"raw": '{"name":"Alice"::"Bob"}'})
    data = r.json()
    assert data["success"] is False


def test_malformed_single_quotes():
    r = client.post("/json/format", json={"raw": "{'name':'Alice'}"})
    data = r.json()
    assert data["success"] is False


def test_malformed_plain_text():
    r = client.post("/json/format", json={"raw": "not json at all"})
    data = r.json()
    assert data["success"] is False
    assert data["error_line"] is not None


# ── URL encode/decode ────────────────────────────────────────
def test_url_roundtrip():
    original = "hello world & test=1"
    r1 = client.post("/url/encode", json={"url": original})
    assert r1.json()["success"] is True
    encoded = r1.json()["data"]
    r2 = client.post("/url/decode", json={"url": encoded})
    assert r2.json()["data"] == original
