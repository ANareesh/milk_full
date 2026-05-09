"""Add missing columns to products table directly."""
import sys
sys.path.insert(0, r'c:\Users\arena\OneDrive\Desktop\ASN-Dairy-Farm\ASN-Dairy-Farm\backend')

from app.core.database import engine
from sqlalchemy import text

# SQL to add missing columns
sql_statements = [
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS discount_percentage FLOAT DEFAULT 0;",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS offer_price FLOAT DEFAULT NULL;",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS offer_description VARCHAR(255) DEFAULT NULL;",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS min_quantity_for_offer FLOAT DEFAULT 1;",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS max_quantity_per_order FLOAT DEFAULT NULL;",
]

try:
    with engine.connect() as conn:
        for sql in sql_statements:
            print(f"Executing: {sql}")
            conn.execute(text(sql))
        conn.commit()
    print("✓ All columns added successfully!")
except Exception as e:
    print(f"✗ Error adding columns: {e}")
    sys.exit(1)
