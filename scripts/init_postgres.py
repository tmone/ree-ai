#!/usr/bin/env python3
"""
PostgreSQL Auto-Provisioning Script
1. Try to connect to existing PostgreSQL (local or Docker)
2. If fail → Auto-start Docker PostgreSQL
3. Setup database and tables if needed
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed")

import psycopg2


class PostgreSQLProvisioner:
    """Auto-provision PostgreSQL with fallback to Docker"""

    def __init__(self):
        self.pg_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.pg_port = int(os.getenv('POSTGRES_PORT', 5432))
        self.pg_db = os.getenv('POSTGRES_DB', 'ree_ai')
        self.pg_user = os.getenv('POSTGRES_USER', 'ree_ai_user')
        self.pg_pass = os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')
        self.docker_host = os.getenv('DOCKER_POSTGRES_HOST', 'postgres')

    def test_connection(self, host: str, timeout: int = 3) -> bool:
        """Test PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=host,
                port=self.pg_port,
                database='postgres',  # Connect to default DB first
                user=self.pg_user,
                password=self.pg_pass,
                connect_timeout=timeout
            )
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️  Connection to {host}:{self.pg_port} failed: {e}")
            return False

    def start_docker_postgres(self) -> bool:
        """Start PostgreSQL via Docker Compose"""
        print("\n🐳 Starting PostgreSQL Docker container...")

        try:
            # Check if docker-compose exists
            result = subprocess.run(
                ['docker-compose', 'version'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            if result.returncode != 0:
                print("❌ docker-compose not found")
                return False

            # Start PostgreSQL container
            print("🚀 Running: docker-compose up -d postgres")
            result = subprocess.run(
                ['docker-compose', 'up', '-d', 'postgres'],
                capture_output=True,
                text=True,
                cwd=project_root
            )

            if result.returncode != 0:
                print(f"❌ Failed to start Docker PostgreSQL:")
                print(result.stderr)
                return False

            print("✅ Docker PostgreSQL container started")

            # Wait for PostgreSQL to be ready
            print("⏳ Waiting for PostgreSQL to be ready...")
            for i in range(30):
                time.sleep(1)
                if self.test_connection('localhost'):
                    print(f"✅ PostgreSQL ready after {i+1}s")
                    return True
                print(f"   Attempt {i+1}/30...")

            print("❌ PostgreSQL did not become ready in time")
            return False

        except Exception as e:
            print(f"❌ Error starting Docker PostgreSQL: {e}")
            return False

    def ensure_database(self, conn) -> bool:
        """Ensure database exists"""
        try:
            # Check if database exists
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.pg_db,)
            )
            exists = cursor.fetchone()

            if not exists:
                print(f"📊 Creating database '{self.pg_db}'...")
                cursor.execute(f"CREATE DATABASE {self.pg_db} OWNER {self.pg_user}")
                print(f"✅ Database '{self.pg_db}' created")

            cursor.close()
            return True

        except Exception as e:
            print(f"❌ Error ensuring database: {e}")
            return False

    def ensure_tables(self) -> bool:
        """Ensure tables exist"""
        try:
            conn = psycopg2.connect(
                host='localhost' if self.test_connection('localhost') else self.docker_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_pass
            )

            cursor = conn.cursor()

            # Create properties table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    price TEXT,
                    location TEXT,
                    bedrooms INTEGER DEFAULT 0,
                    bathrooms INTEGER DEFAULT 0,
                    area TEXT,
                    description TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    property_type TEXT,
                    confidence FLOAT,
                    is_relevant BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_property_type ON properties(property_type);
                CREATE INDEX IF NOT EXISTS idx_location ON properties(location);
                CREATE INDEX IF NOT EXISTS idx_created_at ON properties(created_at);
            """)

            conn.commit()
            cursor.close()
            conn.close()

            print("✅ Tables ensured")
            return True

        except Exception as e:
            print(f"❌ Error ensuring tables: {e}")
            return False

    def provision(self) -> dict:
        """
        Main provisioning logic:
        1. Try localhost
        2. Try docker host
        3. Start Docker if needed
        4. Ensure database and tables
        """
        print("=" * 70)
        print("🚀 POSTGRESQL AUTO-PROVISIONING")
        print("=" * 70)

        result = {
            'success': False,
            'host': None,
            'port': self.pg_port,
            'database': self.pg_db,
            'user': self.pg_user,
            'method': None
        }

        # Step 1: Try localhost
        print(f"\n1️⃣  Trying localhost:{self.pg_port}...")
        if self.test_connection('localhost'):
            print(f"✅ Found PostgreSQL at localhost:{self.pg_port}")
            result['host'] = 'localhost'
            result['method'] = 'existing_local'
            result['success'] = True

        # Step 2: Try Docker host (if Docker network)
        elif self.docker_host != 'localhost':
            print(f"\n2️⃣  Trying Docker host: {self.docker_host}:{self.pg_port}...")
            if self.test_connection(self.docker_host):
                print(f"✅ Found PostgreSQL at {self.docker_host}:{self.pg_port}")
                result['host'] = self.docker_host
                result['method'] = 'existing_docker'
                result['success'] = True

        # Step 3: Start Docker PostgreSQL
        if not result['success']:
            print(f"\n3️⃣  No PostgreSQL found, starting Docker...")
            if self.start_docker_postgres():
                result['host'] = 'localhost'
                result['method'] = 'new_docker'
                result['success'] = True
            else:
                print("\n❌ FAILED TO PROVISION POSTGRESQL")
                return result

        # Step 4: Ensure database
        print(f"\n4️⃣  Ensuring database '{self.pg_db}'...")
        try:
            conn = psycopg2.connect(
                host=result['host'],
                port=self.pg_port,
                database='postgres',
                user=self.pg_user,
                password=self.pg_pass
            )
            self.ensure_database(conn)
            conn.close()
        except Exception as e:
            print(f"⚠️  Could not ensure database: {e}")

        # Step 5: Ensure tables
        print(f"\n5️⃣  Ensuring tables...")
        self.ensure_tables()

        # Summary
        print("\n" + "=" * 70)
        print("✅ POSTGRESQL PROVISIONING COMPLETE")
        print("=" * 70)
        print(f"📍 Host: {result['host']}")
        print(f"📍 Port: {result['port']}")
        print(f"📍 Database: {result['database']}")
        print(f"📍 User: {result['user']}")
        print(f"📍 Method: {result['method']}")
        print("=" * 70)

        return result


def main():
    """Main entry point"""
    provisioner = PostgreSQLProvisioner()
    result = provisioner.provision()

    if result['success']:
        # Save connection info to .env.postgres for other scripts
        env_file = project_root / '.env.postgres'
        with open(env_file, 'w') as f:
            f.write(f"# Auto-generated PostgreSQL connection\n")
            f.write(f"POSTGRES_HOST={result['host']}\n")
            f.write(f"POSTGRES_PORT={result['port']}\n")
            f.write(f"POSTGRES_DB={result['database']}\n")
            f.write(f"POSTGRES_USER={result['user']}\n")
            f.write(f"# Provisioned via: {result['method']}\n")

        print(f"\n💾 Connection saved to: {env_file}")
        return 0
    else:
        print("\n❌ Provisioning failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
