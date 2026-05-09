"""Run Alembic migration."""
import os
import sys

os.chdir(r'c:\Users\arena\OneDrive\Desktop\ASN-Dairy-Farm\ASN-Dairy-Farm\backend')
sys.path.insert(0, '.')

from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic/alembic.ini")

# Load settings to get database URL
from app.core.config import get_settings
settings = get_settings()
alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

try:
    command.upgrade(alembic_cfg, "head")
    print("Migration completed successfully!")
except Exception as e:
    print(f"Migration failed: {e}")
    sys.exit(1)
