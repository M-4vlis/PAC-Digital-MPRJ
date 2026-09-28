import argparse

from .database import SessionLocal
from .public_snapshot import publish_snapshot, snapshot_payload


def main():
    parser = argparse.ArgumentParser(description="Publica snapshot local do PAC sem transmissão externa.")
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    with SessionLocal() as db:
        print(snapshot_payload(publish_snapshot(db, args.year)))


if __name__ == "__main__":
    main()
