#!/usr/bin/env python3
"""
Run Master Data Migrations
Executes SQL migration files for master data tables and seeds initial data
"""
import asyncio
import asyncpg
import sys
from pathlib import Path
from shared.config import settings
from shared.utils.logger import logger, LogEmoji


async def run_migration(conn: asyncpg.Connection, migration_file: Path):
    """Run a single migration file"""
    try:
        logger.info(f"{LogEmoji.INFO} Running migration: {migration_file.name}")

        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        await conn.execute(sql)

        logger.info(f"{LogEmoji.SUCCESS} Migration completed: {migration_file.name}")
        return True

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Migration failed: {migration_file.name}")
        logger.error(f"{LogEmoji.ERROR} Error: {e}")
        return False


async def run_seed(conn: asyncpg.Connection, seed_file: Path):
    """Run a single seed file"""
    try:
        logger.info(f"{LogEmoji.INFO} Running seed: {seed_file.name}")

        with open(seed_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        await conn.execute(sql)

        logger.info(f"{LogEmoji.SUCCESS} Seed completed: {seed_file.name}")
        return True

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Seed failed: {seed_file.name}")
        logger.error(f"{LogEmoji.ERROR} Error: {e}")
        return False


async def main():
    """Main migration runner"""
    logger.info(f"{LogEmoji.ROCKET} Starting Master Data Migrations")

    # Get project root
    project_root = Path(__file__).parent.parent

    # Migration and seed directories
    migrations_dir = project_root / "database" / "migrations"
    seeds_dir = project_root / "database" / "seeds"

    # Check directories exist
    if not migrations_dir.exists():
        logger.error(f"{LogEmoji.ERROR} Migrations directory not found: {migrations_dir}")
        sys.exit(1)

    if not seeds_dir.exists():
        logger.error(f"{LogEmoji.ERROR} Seeds directory not found: {seeds_dir}")
        sys.exit(1)

    # Connect to PostgreSQL
    try:
        logger.info(f"{LogEmoji.INFO} Connecting to PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")

        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )

        logger.info(f"{LogEmoji.SUCCESS} Connected to PostgreSQL")

    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

    try:
        # Run migrations (only 006_create_master_data.sql)
        master_data_migration = migrations_dir / "006_create_master_data.sql"

        if master_data_migration.exists():
            logger.info(f"{LogEmoji.AI} Running master data migration...")
            success = await run_migration(conn, master_data_migration)

            if not success:
                logger.error(f"{LogEmoji.ERROR} Master data migration failed!")
                sys.exit(1)
        else:
            logger.warning(f"{LogEmoji.WARNING} Master data migration not found: {master_data_migration}")

        # Run seeds
        seed_files = sorted(seeds_dir.glob("*.sql"))

        if not seed_files:
            logger.warning(f"{LogEmoji.WARNING} No seed files found in {seeds_dir}")
        else:
            logger.info(f"{LogEmoji.AI} Found {len(seed_files)} seed files")

            for seed_file in seed_files:
                success = await run_seed(conn, seed_file)

                if not success:
                    logger.error(f"{LogEmoji.ERROR} Seed failed: {seed_file.name}")
                    # Continue with other seeds even if one fails
                    continue

        logger.info(f"{LogEmoji.SUCCESS} All migrations and seeds completed!")

        # Verify data
        logger.info(f"{LogEmoji.INFO} Verifying master data...")

        district_count = await conn.fetchval("SELECT COUNT(*) FROM master_districts")
        property_type_count = await conn.fetchval("SELECT COUNT(*) FROM master_property_types")
        amenity_count = await conn.fetchval("SELECT COUNT(*) FROM master_amenities")

        logger.info(f"{LogEmoji.SUCCESS} Districts: {district_count}")
        logger.info(f"{LogEmoji.SUCCESS} Property Types: {property_type_count}")
        logger.info(f"{LogEmoji.SUCCESS} Amenities: {amenity_count}")

    finally:
        await conn.close()
        logger.info(f"{LogEmoji.INFO} Disconnected from PostgreSQL")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(f"{LogEmoji.INFO} Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Migration failed with error: {e}")
        sys.exit(1)
