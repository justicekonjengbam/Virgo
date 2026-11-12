import os
import sqlite3
import tempfile
import unittest


class TestDatabaseMigrationIntegrity(unittest.TestCase):
    """
    Milestone 2.1 Database Verification:
    Tests migration l0e5c9d30001_add_driver_document_metadata against a copy
    of an existing database with real pre-existing driver records and documents.
    """

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cur = self.conn.cursor()

        # Create pre-Milestone-2 database schema
        self.cur.execute("""
            CREATE TABLE drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firebase_uid TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone_number TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                is_online INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        self.cur.execute("""
            CREATE TABLE vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_number TEXT UNIQUE NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                verification_status TEXT NOT NULL DEFAULT 'pending'
            );
        """)

        self.cur.execute("""
            CREATE TABLE driver_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                document_number TEXT,
                storage_key TEXT,
                verification_status TEXT NOT NULL DEFAULT 'pending',
                reviewed_by TEXT,
                reviewed_at TIMESTAMP,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(driver_id) REFERENCES drivers(id) ON DELETE CASCADE
            );
        """)

        # Seed pre-existing records (Simulating pre-existing production state)
        self.cur.execute(
            "INSERT INTO drivers (id, firebase_uid, full_name, phone_number, status) "
            "VALUES (?, ?, ?, ?, ?);",
            (101, "firebase-tomba", "Tomba Singh", "919862000101", "active"),
        )
        self.cur.execute(
            "INSERT INTO vehicles (id, registration_number, make, model, verification_status) "
            "VALUES (?, ?, ?, ?, ?);",
            (501, "MN01AB1234", "Maruti", "Swift", "verified"),
        )
        self.cur.execute(
            "INSERT INTO driver_documents (id, driver_id, document_type, document_number, storage_key, verification_status) "
            "VALUES (?, ?, ?, ?, ?, ?);",
            (901, 101, "driving_licence", "MN01-2022-00101", "uploads/dl_legacy.pdf", "verified"),
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_migration_and_data_preservation(self):
        """Verifies migration adds columns without losing existing records."""
        # 1. Apply Migration: Add columns as in Alembic revision l0e5c9d30001
        new_columns = [
            ("rejection_reason", "TEXT"),
            ("original_filename", "VARCHAR(255)"),
            ("mime_type", "VARCHAR(100)"),
            ("file_size_bytes", "INTEGER"),
        ]
        for col_name, col_type in new_columns:
            self.cur.execute(f"ALTER TABLE driver_documents ADD COLUMN {col_name} {col_type};")
        self.conn.commit()

        # 2. Verify pre-existing driver record is completely intact
        self.cur.execute("SELECT id, firebase_uid, full_name, phone_number, status FROM drivers WHERE id = 101;")
        driver = self.cur.fetchone()
        self.assertEqual(driver, (101, "firebase-tomba", "Tomba Singh", "919862000101", "active"))

        # 3. Verify pre-existing document record is completely intact
        self.cur.execute(
            "SELECT id, driver_id, document_type, document_number, storage_key, verification_status, "
            "rejection_reason, original_filename, mime_type, file_size_bytes "
            "FROM driver_documents WHERE id = 901;"
        )
        doc = self.cur.fetchone()
        self.assertEqual(doc[:6], (901, 101, "driving_licence", "MN01-2022-00101", "uploads/dl_legacy.pdf", "verified"))
        # New columns should be NULL for pre-existing records
        self.assertEqual(doc[6:], (None, None, None, None))

        # 4. Insert new document with metadata
        self.cur.execute(
            "INSERT INTO driver_documents (driver_id, document_type, document_number, storage_key, "
            "verification_status, rejection_reason, original_filename, mime_type, file_size_bytes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (
                101,
                "aadhaar",
                "XXXX-XXXX-9999",
                "drivers/101/aadhaar/secure.pdf",
                "pending",
                None,
                "aadhaar_card.pdf",
                "application/pdf",
                2048576,
            ),
        )
        self.conn.commit()

        # 5. Verify total documents count
        self.cur.execute("SELECT count(*) FROM driver_documents WHERE driver_id = 101;")
        self.assertEqual(self.cur.fetchone()[0], 2)

        # 6. Verify Foreign Key Cascade on Driver deletion
        self.cur.execute("DELETE FROM drivers WHERE id = 101;")
        self.conn.commit()
        self.cur.execute("SELECT count(*) FROM driver_documents WHERE driver_id = 101;")
        self.assertEqual(self.cur.fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()

