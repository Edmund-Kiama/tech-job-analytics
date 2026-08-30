from data_pipeline.storage.raw import save_raw_payload


def test_save_raw_payload(tmp_path, monkeypatch):
    payload = {
        "results": [
            {
                "id": "test-1",
                "title": "Test Job",
            }
        ],
        "count": 1,
    }

    monkeypatch.setattr(
        "data_pipeline.storage.raw.BRONZE_DIR",
        tmp_path,
    )

    file_path = save_raw_payload(payload)

    assert file_path.exists()

    assert file_path.read_text(encoding="utf-8")
