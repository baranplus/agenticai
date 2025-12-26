import os
import json
from sqlalchemy import create_engine, MetaData, text, Table, inspect, Column, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from typing import List

from utils.logger import logger

class SQLDatabaseManager:
    """
    A production-ready database manager that:
    - Connects to a database using SQLAlchemy
    - Caches table metadata at startup (reflect or load from cache)
    - Allows querying arbitrary tables with raw SQL
    - Can serialize/deserialize metadata schema for faster startup
    """

    def __init__(self, connection_uri: str, required_tables: List[str], cache_path: str = "schema_cache.json", echo: bool = False):
        self.engine: Engine = create_engine(
            connection_uri,
            echo=echo,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        self.metadata = MetaData()
        self.table_cache = {}
        self.cache_path = cache_path
        self.required_tables = required_tables
        self.table_schemas = {}
        self.initialize_metadata()
        self.load_schemas()

    def initialize_metadata(self):
        """
        Load cached schema metadata if available, otherwise reflect from DB.
        """
        if os.path.exists(self.cache_path):
            logger.info(f"Loading schema metadata from cache: {self.cache_path}")
            self.load_cached_metadata()
        else:
            logger.info("Reflecting schema metadata from database (first run)...")
            self.reflect_and_cache_metadata()

    def reflect_and_cache_metadata(self):
        """Reflect all tables from the database and serialize schema."""
        try:
            self.metadata.reflect(bind=self.engine, only=self.required_tables)
            self.table_cache = self.metadata.tables
            logger.info(f"Reflected and cached {len(self.table_cache)} tables.")
            self.serialize_metadata()
        except SQLAlchemyError as e:
            logger.info("Error reflecting metadata:", e)
            raise

    def serialize_metadata(self):
        """
        Serialize metadata schema to JSON for fast reloading later.
        Only stores table and column names (not data).
        """
        schema_dict = {}
        for table_name, table in self.metadata.tables.items():
            schema_dict[table_name] = [col.name for col in table.columns]

        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Serialized metadata schema to {self.cache_path}")

    def load_cached_metadata(self):
        """
        Load schema metadata from JSON cache and rebuild SQLAlchemy tables.
        """
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                schema_dict = json.load(f)

            for table_name, columns in schema_dict.items():
                self.table_cache[table_name] = Table(table_name, self.metadata)
                for col_name in columns:
                    if col_name not in self.table_cache[table_name].columns:
                        self.table_cache[table_name].append_column(Column(col_name, String))

            logger.info(f"Loaded {len(self.table_cache)} tables from schema cache.")
        except (IOError, json.JSONDecodeError) as e:
            logger.info("Error loading schema cache:", e)
            logger.info("Falling back to reflection...")
            self.reflect_and_cache_metadata()

    def get_table(self, table_name: str) -> Table:
        """Retrieve a table object from cache or reflect it on demand."""
        if table_name in self.table_cache:
            return self.table_cache[table_name]

        logger.info(f"Table '{table_name}' not in cache. Reflecting it...")
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        self.table_cache[table_name] = table
        self.serialize_metadata()
        return table

    def execute_sql(self, sql_query: str, params: dict | None = None):
        """
        Execute an arbitrary SQL query safely.
        Returns all rows as list of dicts if applicable.
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query), params or {})
                if result.returns_rows:
                    return result.mappings().all()
                else:
                    conn.commit()
                    return {"message": "Query executed successfully"}
        except SQLAlchemyError as e:
            logger.info("Database error:", e)
            raise

    def get_table_columns(self, table_name: str):
        """Get a list of columns for a table."""
        inspector = inspect(self.engine)
        return [col["name"] for col in inspector.get_columns(table_name)]

    def check_connection(self) -> bool:
        """Quick connection test."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError:
            raise ConnectionError("Can't connect to sql server instance")
        
    def load_schemas(self):
        """Load schema information for all tables"""
    
        inspector = inspect(self.engine)
        for table_name in self.table_cache.keys():
            columns = inspector.get_columns(table_name)
            schema = f"Table: {table_name}\nColumns:\n"
            for col in columns:
                schema += f"- {col['name']} ({col['type']})\n"
            self.table_schemas[table_name] = schema

    def get_combined_schema(self):
        """Combine all table schemas into one string"""
        return "\n".join(self.table_schemas.values())