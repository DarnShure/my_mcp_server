import sqlite3
import hashlib
from typing import Optional, List, Dict, Any
from pathlib import Path

class Index:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path))
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Table for documents
        c.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                name TEXT,
                hash TEXT
            )
        """)
        # Table for nodes
        c.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                node_id TEXT,
                embedding BLOB,
                metadata TEXT,
                FOREIGN KEY(doc_id) REFERENCES documents(id)
            )
        """)
        conn.commit()
        conn.close()

    def _hash_file(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def index_doc(self, file_path: str, nodes: Optional[List[Dict[str, Any]]] = None):
        """Indexes a document and optionally its nodes."""
        file_path = Path(file_path)
        doc_name = file_path.name
        doc_hash = self._hash_file(str(file_path))
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Insert or ignore document
        c.execute("""
            INSERT OR IGNORE INTO documents (path, name, hash) VALUES (?, ?, ?)
        """, (str(file_path), doc_name, doc_hash))
        # Get doc_id
        c.execute("SELECT id FROM documents WHERE path = ?", (str(file_path),))
        doc_id = c.fetchone()[0]
        # Insert nodes if provided
        if nodes:
            for node in nodes:
                c.execute("""
                    INSERT INTO nodes (doc_id, node_id, embedding, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    doc_id,
                    node.get('node_id'),
                    node.get('embedding'),
                    str(node.get('metadata'))
                ))
        conn.commit()
        conn.close()

    def get_documents(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT path, name, hash FROM documents")
        docs = [{'path': row[0], 'name': row[1], 'hash': row[2]} for row in c.fetchall()]
        conn.close()
        return docs

    def get_nodes(self, doc_path: str) -> List[Dict[str, Any]]:
        doc_path = str(Path(doc_path))
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id FROM documents WHERE path = ?", (doc_path,))
        doc = c.fetchone()
        if not doc:
            conn.close()
            return []
        doc_id = doc[0]
        c.execute("SELECT node_id, embedding, metadata FROM nodes WHERE doc_id = ?", (doc_id,))
        nodes = [
            {'node_id': row[0], 'embedding': row[1], 'metadata': row[2]}
            for row in c.fetchall()
        ]
        conn.close()
        return nodes
