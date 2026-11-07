"""Create invite links for the collection site (spec 2.8 "Invites"). Prem's machine only.

    uv run python -m ml.collect.make_invites 5 --url https://strainless-collect-xxxx.run.app
    uv run python -m ml.collect.make_invites 1 --local --url http://localhost:5000   # dev store
    uv run python -m ml.collect.make_invites --revoke s007

Each new singer gets a random URL-safe token (24 random bytes) and the next
sequential id (s001, s002, ...). An id is never reused: the next number is one
past the highest id found anywhere in the store (invites, sessions, consent,
takes) or in that store's invites file, so deleting an invite object or
losing the file can't bring an old id back. Only the token's SHA-256 is
stored, at invites/<hash>.json = {singer_id, created_at, revoked}.

Each store has its own invites file (singer_id,link), and the two never mix:
- the real bucket (COLLECT_BUCKET) -> data/invites.csv
- a local store (--local, or no bucket set) -> invites.csv inside that store's
  folder, by default data/collect_dev/invites.csv
Both are under data/ (gitignored, never committed). Email each recruit their
link from data/invites.csv and keep the email -> singer_id mapping in the
private recruiting sheet, never here.

The bucket comes from COLLECT_BUCKET in .env; Prem's gcloud application-default
credentials are used (gcloud auth application-default login).
"""

from __future__ import annotations

import argparse
import csv
import re
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.collect.session import token_hash
from ml.collect.storage import ROOT, Conflict, LocalStore, Store, create_json, get_json, put_json, store_from_env

INVITES_CSV = ROOT / "data" / "invites.csv"  # real invites (bucket) only
LOCAL_INVITES_NAME = "invites.csv"  # local invites: inside the LocalStore's folder
TOKEN_BYTES = 24  # spec: at least 16
_SID = re.compile(r"^s(\d+)$")
# Store folders keyed by singer_id: sessions/<sid>.json, consent/<sid>.json, takes/<sid>/...
_SID_FOLDERS = ("sessions/", "consent/", "takes/")


def _invites(store: Store) -> list[tuple[str, dict]]:
    out = []
    for path in store.list("invites/"):
        got = get_json(store, path)
        if got:
            out.append((path, got[0]))
    return out


def invites_csv_for(store: Store) -> Path:
    """The invites file that belongs to this store (never shared between stores)."""
    if isinstance(store, LocalStore):
        return store.root / LOCAL_INVITES_NAME
    return INVITES_CSV


def _csv_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [row.get("singer_id", "") or "" for row in csv.DictReader(f)]


def used_ids(store: Store, out_csv: Path) -> set[str]:
    """Every singer_id already in the store or in its invites file."""
    ids = {inv.get("singer_id", "") for _, inv in _invites(store)}
    for folder in _SID_FOLDERS:
        for path in store.list(folder):
            ids.add(path[len(folder):].split("/", 1)[0].removesuffix(".json"))
    ids.update(_csv_ids(out_csv))
    return {i for i in ids if _SID.match(i)}


def next_number(store: Store, out_csv: Path | None = None) -> int:
    """One past the highest singer number ever used, so no id repeats."""
    used = used_ids(store, out_csv or invites_csv_for(store))
    return max((int(_SID.match(i).group(1)) for i in used), default=0) + 1


def make_invites(store: Store, n: int, base_url: str, out_csv: Path | None = None,
                 now: datetime | None = None) -> list[tuple[str, str]]:
    """Create n invites; append (singer_id, link) rows to the store's invites file and return them.

    out_csv defaults to invites_csv_for(store); passing another path is for tests.
    """
    out_csv = out_csv or invites_csv_for(store)
    now = now or datetime.now(UTC)
    base = base_url.rstrip("/")
    num = next_number(store, out_csv)
    rows = []
    for _ in range(n):
        while True:
            sid = f"s{num:03d}"
            token = secrets.token_urlsafe(TOKEN_BYTES)
            try:
                create_json(store, f"invites/{token_hash(token)}.json",
                            {"singer_id": sid, "created_at": now.isoformat(timespec="seconds"), "revoked": False})
                break
            except Conflict:  # same hash: practically impossible, just draw again
                continue
        rows.append((sid, f"{base}/s/{token}"))
        num += 1
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    new_file = not out_csv.exists()
    with out_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["singer_id", "link"])
        w.writerows(rows)
    return rows


def revoke(store: Store, singer_id: str) -> int:
    """Mark every invite of singer_id revoked. Returns how many were changed."""
    count = 0
    for path, inv in _invites(store):
        if inv.get("singer_id") == singer_id and not inv.get("revoked"):
            inv["revoked"] = True
            put_json(store, path, inv)
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("n", type=int, nargs="?", help="number of new invites")
    ap.add_argument("--url", help="base URL of the collection site")
    ap.add_argument("--local", action="store_true", help="use the local dev store (data/collect_dev)")
    ap.add_argument("--revoke", metavar="SINGER_ID", help="revoke this singer's invite instead")
    a = ap.parse_args(argv)
    store = store_from_env(local=a.local)
    if a.revoke:
        k = revoke(store, a.revoke)
        print(f"revoked {k} invite(s) for {a.revoke}")
        return 0 if k else 1
    if not a.n or a.n < 1 or not a.url:
        ap.error("give N >= 1 and --url (or --revoke SINGER_ID)")
    out = invites_csv_for(store)
    rows = make_invites(store, a.n, a.url, out)
    print(f"created {len(rows)} invite(s): {rows[0][0]}..{rows[-1][0]}; links appended to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
