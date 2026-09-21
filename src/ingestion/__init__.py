"""Ingestion package."""

from src.ingestion.data_generator import generate_operational_dataset
from src.ingestion.pipeline import IngestionPipeline, pipeline

__all__ = ["IngestionPipeline", "generate_operational_dataset", "pipeline"]
