"""
Utility script to seed the application's database from CSV files.

Usage:
  # Locally (uses sqlite):
  python backend/seed_db.py

  # On Render (in service shell) - ensure DATABASE_URL is set in environment:
  python backend/seed_db.py

Notes:
  - This script will NOT drop existing tables when using a remote DB (DATABASE_URL).
  - If you want to force a reset, run the app's reset_database function explicitly (careful — this will drop data).
"""

import sys
from pathlib import Path

# Ensure package imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import init_database, seed_database_if_empty


def main():
    print("🔌 Starting database seed script")
    app = init_database()

    did_seed = seed_database_if_empty(app)

    if did_seed:
        print("✅ Seeding completed — data loaded into database")
        return 0
    else:
        print("ℹ️  No seeding needed — database already has data")
        return 0


if __name__ == '__main__':
    sys.exit(main())
