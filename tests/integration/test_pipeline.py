"""Integration tests for end-to-end data pipeline."""

from src.ingestion.pipeline import IngestionPipeline


def test_pipeline_execution(tmp_path):
    sample_csv = tmp_path / "test_events.csv"
    test_db = tmp_path / "test_analytics.duckdb"

    from src.database.connection import DatabaseManager

    test_db_manager = DatabaseManager(db_path=test_db)

    test_pipeline_instance = IngestionPipeline(
        raw_csv_path=sample_csv,
        db_manager_instance=test_db_manager,
    )

    result = test_pipeline_instance.run(force_regenerate=True, days=1)
    assert result["status"] == "SUCCESS"
    assert result["clean_rows"] > 0
    assert result["quality_report"]["passed_gates"] is True

    test_db_manager.close()
