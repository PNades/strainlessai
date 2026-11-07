"""Prem's collection tools: make_invites -> report -> pull, against a LocalStore."""

from __future__ import annotations

import csv
from datetime import UTC, datetime, timedelta

from ml.collect import make_invites, pull, report
from ml.collect import session as S
from ml.collect.session import token_hash
from ml.collect.storage import LocalStore, get_json, put_json

T0 = datetime(2026, 11, 20, 14, 0, tzinfo=UTC)
PROFILE = {"voice_type": "tenor", "sex": "M", "device": "phone", "mic": "built-in"}


def test_make_invites(tmp_path):
    store = LocalStore(tmp_path / "b")
    out = tmp_path / "invites.csv"
    rows = make_invites.make_invites(store, 3, "https://collect.example/", out, now=T0)
    assert [r[0] for r in rows] == ["s001", "s002", "s003"]
    rows2 = make_invites.make_invites(store, 2, "https://collect.example", out, now=T0)
    assert [r[0] for r in rows2] == ["s004", "s005"]

    with out.open(encoding="utf-8") as f:
        lines = list(csv.reader(f))
    assert lines[0] == ["singer_id", "link"] and len(lines) == 6
    for sid, link in lines[1:]:
        assert link.startswith("https://collect.example/s/")
        token = link.rsplit("/", 1)[1]
        assert len(token) >= 22  # >= 16 random bytes, url-safe base64
        inv = get_json(store, f"invites/{token_hash(token)}.json")[0]
        assert inv == {"singer_id": sid, "created_at": T0.isoformat(timespec="seconds"), "revoked": False}
        # The token itself is never stored.
        assert all(token.encode() not in store.get_bytes(p)[0] for p in store.list(""))

    assert make_invites.revoke(store, "s002") == 1
    assert make_invites.revoke(store, "s999") == 0
    revoked = [get_json(store, p)[0] for p in store.list("invites/")]
    assert [i["singer_id"] for i in revoked if i["revoked"]] == ["s002"]


def _ids(rows):
    return [sid for sid, _ in rows]


def test_invite_ids_keep_counting_up(tmp_path):
    """Nothing is reset between rounds; every new id is past every id used before."""
    store = LocalStore(tmp_path / "dev")
    url = "http://localhost:8080"
    rounds = [make_invites.make_invites(store, 2, url, now=T0), make_invites.make_invites(store, 3, url, now=T0)]
    assert _ids(rounds[0]) == ["s001", "s002"] and _ids(rounds[1]) == ["s003", "s004", "s005"]

    # The store loses s005's invite object: the invites file still remembers it.
    (path,) = [p for p, inv in make_invites._invites(store) if inv["singer_id"] == "s005"]
    store.delete(path)
    rounds.append(make_invites.make_invites(store, 1, url, now=T0))
    assert _ids(rounds[-1]) == ["s006"]

    # The invites file is lost: the store still remembers s001-s004 and s006.
    make_invites.invites_csv_for(store).unlink()
    rounds.append(make_invites.make_invites(store, 1, url, now=T0))
    assert _ids(rounds[-1]) == ["s007"]

    # A singer with a session, consent and takes but no invite object (e.g. deleted by hand).
    put_json(store, "sessions/s009.json", {"singer_id": "s009"})
    put_json(store, "consent/s010.json", {"name": "x"})
    store.put_bytes("takes/s011/abc123.wav", b"RIFF", "audio/wav")
    rounds.append(make_invites.make_invites(store, 2, url, now=T0))
    assert _ids(rounds[-1]) == ["s012", "s013"]

    nums = [int(sid[1:]) for r in rounds for sid in _ids(r)]
    assert nums == sorted(nums) and len(nums) == len(set(nums))


class _Bucket:
    """Stands in for GCSStore: same interface, but not a LocalStore."""

    def __init__(self, root):
        self._s = LocalStore(root)

    def __getattr__(self, name):
        return getattr(self._s, name)


def test_local_and_real_invites_never_share_a_file(tmp_path, monkeypatch):
    real_csv = tmp_path / "data" / "invites.csv"
    monkeypatch.setattr(make_invites, "INVITES_CSV", real_csv)
    dev = tmp_path / "data" / "collect_dev"
    assert make_invites.invites_csv_for(LocalStore(dev)) == dev / "invites.csv"
    assert make_invites.invites_csv_for(_Bucket(tmp_path / "bucket")) == real_csv

    # --local writes only to the dev store's own file, even when .env sets COLLECT_BUCKET.
    monkeypatch.setenv("COLLECT_BUCKET", "not-used-by-local")
    monkeypatch.setenv("COLLECT_LOCAL_DIR", str(dev))
    assert make_invites.main(["2", "--local", "--url", "http://localhost:8080"]) == 0
    with (dev / "invites.csv").open(encoding="utf-8") as f:
        assert [r[0] for r in csv.reader(f)] == ["singer_id", "s001", "s002"]
    assert not real_csv.exists()

    # A real invite goes to data/invites.csv and counts from that store, not the dev one.
    rows = make_invites.make_invites(_Bucket(tmp_path / "bucket"), 1, "https://collect.example", now=T0)
    assert _ids(rows) == ["s001"]
    with real_csv.open(encoding="utf-8") as f:
        assert [r[0] for r in csv.reader(f)] == ["singer_id", "s001"]
    with (dev / "invites.csv").open(encoding="utf-8") as f:
        assert len(list(csv.reader(f))) == 3


def _session(store, sid, n_accepted, submit=False):
    s = S.new_session(sid, T0)
    S.set_consent(s, "consent-v1", T0)
    S.set_profile(s, PROFILE, T0)
    S.set_mic_check(s, True, [], T0)
    for n in range(1, n_accepted + 1):
        clip = f"c{sid}{n:02d}xxx"
        S.accept_take(s, n, clip, [], T0)
        store.put_bytes(f"takes/{sid}/{clip}.wav", b"RIFF" + bytes([n]), "audio/wav")
        put_json(store, f"takes/{sid}/{clip}.json", {"clip_id": clip, "singer_id": sid, "slot": n})
    if submit:
        S.submit(s, "ABCDEFGH" if sid == "s001" else "HGFEDCBA", T0)
    put_json(store, f"sessions/{sid}.json", s)
    return s


def test_report_and_pull(tmp_path):
    store = LocalStore(tmp_path / "b")
    make_invites.make_invites(store, 4, "https://c.example", tmp_path / "i.csv", now=T0)
    _session(store, "s001", 16, submit=True)
    _session(store, "s002", 7)
    # an orphan take (crash between upload and session write) and a submitted session
    store.put_bytes("takes/s001/corphan.wav", b"x", "audio/wav")
    make_invites.revoke(store, "s004")

    rs = {r["singer_id"]: r for r in report.rows(store, now=T0 + timedelta(days=1))}
    assert rs["s001"]["status"] == "submitted" and rs["s001"]["code"] == "ABCDEFGH" and rs["s001"]["accepted"] == 16
    assert rs["s002"]["status"] == "open" and rs["s002"]["accepted"] == 7 and rs["s002"]["code"] == ""
    assert rs["s003"]["status"] == "not started" and rs["s003"]["link"] == "ok"
    assert rs["s004"]["link"] == "revoked"
    assert report.rows(store, now=T0 + timedelta(days=31))[2]["link"] == "expired"
    text = report.format_rows(list(rs.values()))
    assert "ABCDEFGH" in text and "1 submitted" in text

    raw = tmp_path / "raw"
    c = pull.pull(store, raw)
    assert c == {"sessions": 1, "written": 32, "unchanged": 0, "missing": 0, "skipped_open": 1}
    names = sorted(p.name for p in raw.iterdir())
    assert len(names) == 32 and all(n.startswith("cs001") for n in names)  # nothing from the open session
    assert "corphan.wav" not in names
    c = pull.pull(store, raw)
    assert c["written"] == 0 and c["unchanged"] == 32
