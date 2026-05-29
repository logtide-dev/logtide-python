def test_global_imports() -> None:
    from logtide_sdk import middleware  # noqa: F401


# could do enable/disable inside the test if not installed (idk why)
def test_fastapi() -> None:
    from logtide_sdk.middleware import LogTideFastAPIMiddleware

    assert LogTideFastAPIMiddleware is not None


def test_flask() -> None:
    from logtide_sdk.middleware import LogTideFlaskMiddleware

    assert LogTideFlaskMiddleware is not None


def test_starlette() -> None:
    from logtide_sdk.middleware import LogTideStarletteMiddleware

    assert LogTideStarletteMiddleware is not None


def test_django() -> None:
    from logtide_sdk.middleware import LogTideDjangoMiddleware

    assert LogTideDjangoMiddleware is not None
