import pytest
import uvicorn


def test_cli_starts_api(monkeypatch: pytest.MonkeyPatch) -> None:
    from dental_clinic.cli import main

    run_options: dict[str, object] = {}

    def fake_run(app: str, host: str, port: int) -> None:
        run_options.update(app=app, host=host, port=port)

    monkeypatch.setattr(uvicorn, "run", fake_run)

    main()

    assert run_options == {
        "app": "dental_clinic.main:app",
        "host": "127.0.0.1",
        "port": 8000,
    }
