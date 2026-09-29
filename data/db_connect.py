# =====================================================
# Beginner note:
# This file connects Python to the SQLite database file.
# In simple words, it tells Python:
# "Use this database and read its structure so we know
# what tables and columns exist."
#
# Why do we need this?
# Because the AI model does not automatically understand
# the database. It needs a clear description of the schema
# before it can generate a correct SQL query.
# =====================================================

from pathlib import Path

from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# load_dotenv() reads values from a .env file.
# Example: OPENAI_API_KEY=value
load_dotenv()

# Build the database path relative to this file instead of the current working directory.
# This makes the app work no matter where you run it from.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

# Create a database engine.
# This uses the actual database file inside the data/ folder.
engine = create_engine(f"sqlite:///{DB_PATH}")

# inspect(engine) helps us look at the database structure.
# It can detect tables and column names without writing SQL manually.
inspector = inspect(engine)


def get_database_schema():
    """
    This function reads the database and builds a text summary
    of all tables and their columns.

    Example output:
    Table: customers
    Columns:
      - id (INTEGER)
      - name (TEXT)

    This summary is passed to the LLM so it knows what data is available.
    """
    schema_info = ""

    # Get the names of all tables in the database.
    for table_name in inspector.get_table_names():
        schema_info += f"\nTable: {table_name}\n"
        schema_info += "Columns:\n"

        # Get the columns inside each table and include their names and types.
        for column in inspector.get_columns(table_name):
            schema_info += f"  - {column['name']} ({column['type']})\n"

    return schema_info


# This block runs only when this file is executed directly.
# It is just a quick test to print the generated schema.
if __name__ == "__main__":
    print("📊 Database Schema:")
    print(get_database_schema())