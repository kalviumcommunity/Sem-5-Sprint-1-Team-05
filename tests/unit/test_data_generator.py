"""Unit tests for deterministic synthetic event generation."""

from src.ingestion.data_generator import generate_operational_dataset


def test_seeded_generation_is_reproducible_and_unique():
    first = generate_operational_dataset(days=1, random_seed=7)
    second = generate_operational_dataset(days=1, random_seed=7)

    assert first.equals(second)
    assert first["request_id"].is_unique
