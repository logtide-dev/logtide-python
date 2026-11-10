"""Fork safety: a client created before fork() must keep working in the child."""

import os
import threading

import pytest

from logtide_sdk import ClientOptions, LogTideClient
from logtide_sdk.models import LogEntry


def _client(**kwargs) -> LogTideClient:
    return LogTideClient(ClientOptions(api_url="http://localhost:8080", api_key="k", **kwargs))


def test_pid_change_reinitializes_process_state(monkeypatch):
    client = _client(flush_interval=60_000)
    client.log(LogEntry(service="svc", level="info", message="from parent"))
    old_session = client._session
    old_lock = client._buffer_lock
    old_timer = client._flush_timer

    sent: list[list[LogEntry]] = []
    monkeypatch.setattr(client, "_send_logs", lambda entries: sent.append(entries))
    child_pid = client._pid + 1
    monkeypatch.setattr(os, "getpid", lambda: child_pid)

    client.log(LogEntry(service="svc", level="info", message="from child"))

    assert client._session is not old_session
    assert client._buffer_lock is not old_lock
    assert client._flush_timer is not old_timer
    assert client._flush_timer is not None
    assert client._flush_timer.is_alive()
    # the parent's buffered entry is not re-sent by the child
    assert [e.message for e in client._buffer] == ["from child"]

    client.flush()
    assert [e.message for e in sent[0]] == ["from child"]

    monkeypatch.undo()
    client.close()


def test_reinit_is_noop_in_same_process():
    client = _client(flush_interval=0)
    client.log(LogEntry(service="svc", level="info", message="kept"))
    session = client._session

    client._reinit_after_fork()

    assert client._session is session
    assert [e.message for e in client._buffer] == ["kept"]
    client._buffer.clear()
    client.close()


def test_closed_client_does_not_restart_timer_after_fork(monkeypatch):
    client = _client(flush_interval=60_000)
    client.close()
    child_pid = client._pid + 1
    monkeypatch.setattr(os, "getpid", lambda: child_pid)

    client._check_pid()

    assert client._flush_timer is None


@pytest.mark.skipif(not hasattr(os, "fork"), reason="requires os.fork (POSIX)")
@pytest.mark.filterwarnings("ignore:This process .* is multi-threaded:DeprecationWarning")
def test_real_fork_with_lock_held_by_another_thread():
    client = _client(flush_interval=60_000)
    client.log(LogEntry(service="svc", level="info", message="from parent"))

    # Simulate a parent thread holding the buffer lock at fork time: without
    # the at-fork reset, the child would deadlock on its first log() call.
    acquired = threading.Event()
    release = threading.Event()

    def hold_lock() -> None:
        with client._buffer_lock:
            acquired.set()
            release.wait(5)

    holder = threading.Thread(target=hold_lock)
    holder.start()
    acquired.wait(5)

    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        code = 1
        try:
            sent: list[str] = []
            client._send_logs = lambda entries: sent.extend(e.message for e in entries)
            done = threading.Event()

            def work() -> None:
                client.log(LogEntry(service="svc", level="info", message="from child"))
                client.flush()
                done.set()

            threading.Thread(target=work, daemon=True).start()
            if done.wait(5) and sent == ["from child"]:
                code = 0
            os.write(write_fd, ",".join(sent).encode() or b"<none>")
        finally:
            os._exit(code)

    os.close(write_fd)
    release.set()
    holder.join()
    _, status = os.waitpid(pid, 0)
    child_output = os.read(read_fd, 1024).decode()
    os.close(read_fd)

    assert os.waitstatus_to_exitcode(status) == 0, f"child sent: {child_output}"
    # the parent still owns (and will send) its own entry
    assert [e.message for e in client._buffer] == ["from parent"]
    client._buffer.clear()
    client.close()
