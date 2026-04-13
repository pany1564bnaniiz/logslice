"""Tests for logslice.transform module."""

import pytest

from logslice.transform import (
    TransformError,
    add_field,
    apply_transforms,
    drop_fields,
    keep_fields,
    rename_field,
)


# --- rename_field ---

def test_rename_field_basic():
    record = {"level": "info", "msg": "hello"}
    result = rename_field(record, "msg", "message")
    assert result == {"level": "info", "message": "hello"}


def test_rename_field_does_not_mutate_original():
    record = {"a": 1}
    rename_field(record, "a", "b")
    assert "a" in record


def test_rename_field_missing_key_raises():
    with pytest.raises(TransformError, match="not found"):
        rename_field({"a": 1}, "z", "b")


def test_rename_field_empty_new_key_raises():
    with pytest.raises(TransformError):
        rename_field({"a": 1}, "a", "")


# --- drop_fields ---

def test_drop_fields_removes_listed_keys():
    record = {"a": 1, "b": 2, "c": 3}
    result = drop_fields(record, ["a", "c"])
    assert result == {"b": 2}


def test_drop_fields_empty_list_returns_copy():
    record = {"a": 1}
    result = drop_fields(record, [])
    assert result == {"a": 1}
    assert result is not record


def test_drop_fields_nonexistent_key_is_ignored():
    record = {"a": 1}
    result = drop_fields(record, ["z"])
    assert result == {"a": 1}


# --- keep_fields ---

def test_keep_fields_retains_only_listed():
    record = {"a": 1, "b": 2, "c": 3}
    result = keep_fields(record, ["a", "c"])
    assert result == {"a": 1, "c": 3}


def test_keep_fields_empty_list_raises():
    with pytest.raises(TransformError):
        keep_fields({"a": 1}, [])


def test_keep_fields_missing_keys_omitted():
    record = {"a": 1}
    result = keep_fields(record, ["a", "z"])
    assert result == {"a": 1}


# --- add_field ---

def test_add_field_inserts_new_key():
    result = add_field({"a": 1}, "b", 42)
    assert result["b"] == 42


def test_add_field_existing_key_raises_without_overwrite():
    with pytest.raises(TransformError, match="already exists"):
        add_field({"a": 1}, "a", 99)


def test_add_field_existing_key_overwrite_allowed():
    result = add_field({"a": 1}, "a", 99, overwrite=True)
    assert result["a"] == 99


def test_add_field_empty_key_raises():
    with pytest.raises(TransformError):
        add_field({}, "", "val")


# --- apply_transforms ---

def test_apply_transforms_rename():
    record = {"msg": "hi"}
    result = apply_transforms(record, [{"op": "rename", "from": "msg", "to": "message"}])
    assert "message" in result and "msg" not in result


def test_apply_transforms_drop():
    record = {"a": 1, "b": 2}
    result = apply_transforms(record, [{"op": "drop", "fields": ["b"]}])
    assert result == {"a": 1}


def test_apply_transforms_keep():
    record = {"a": 1, "b": 2, "c": 3}
    result = apply_transforms(record, [{"op": "keep", "fields": ["a"]}])
    assert result == {"a": 1}


def test_apply_transforms_add():
    result = apply_transforms({"a": 1}, [{"op": "add", "key": "env", "value": "prod"}])
    assert result["env"] == "prod"


def test_apply_transforms_chained():
    record = {"level": "info", "msg": "ok", "secret": "x"}
    transforms = [
        {"op": "drop", "fields": ["secret"]},
        {"op": "rename", "from": "msg", "to": "message"},
    ]
    result = apply_transforms(record, transforms)
    assert result == {"level": "info", "message": "ok"}


def test_apply_transforms_unknown_op_raises():
    with pytest.raises(TransformError, match="Unknown transform op"):
        apply_transforms({"a": 1}, [{"op": "explode"}])
