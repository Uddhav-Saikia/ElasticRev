"""Seed the application's database from CSV files.

This is a safe, idempotent script that will only load data if the database is empty.
Run locally or in the Render service shell (ensure DATABASE_URL is set in Render).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import init_database, seed_database_if_empty


def main():
    print("🔌 Starting database seeding")
    app = init_database()
    seeded = seed_database_if_empty(app)
    if seeded:
        print("✅ Database seeded successfully")
    else:
        print("ℹ️  Database already contains data; skipping seeding")


if __name__ == '__main__':
    main()
