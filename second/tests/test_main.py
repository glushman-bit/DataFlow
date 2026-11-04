from second import main


def test_main(monkeypatch, tmp_path):
    """Тест главной функции."""

    data_dir = tmp_path / "data"
    csv_path = data_dir / "test.csv"

    records = [{"title": "Покраска деталей"}]

    loaded_paths = []
    shown_records = []

    def fake_load_from_csv(path):
        loaded_paths.append(path)
        return records

    def fake_show_menu(loaded_records):
        shown_records.append(loaded_records)

    monkeypatch.setattr(main, "data_dir", data_dir)
    monkeypatch.setattr(main, "path", csv_path)
    monkeypatch.setattr(main, "load_from_csv", fake_load_from_csv)
    monkeypatch.setattr(main, "show_menu", fake_show_menu)

    main.main()

    assert data_dir.exists()
    assert loaded_paths == [csv_path]
    assert shown_records == [records]

