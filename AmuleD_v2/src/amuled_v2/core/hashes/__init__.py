"""ED2K hash layer: MD4 and ED2K file hashing (PROTOCOL_MATRIX.md section 3).

Re-exports the public hash API so callers import from ``core.hashes`` directly.

src/amuled_v2/core/hashes/__init__.py
Version:     0.1.0
Author:      Soror L.'.L'.
Updated:     2026-09-22

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] Package marker re-exporting MD4, md4_digest, ed2k_hash_data,
      ed2k_hash_file and Ed2kHashResult.
"""

from .ed2k import (
    PARTSIZE,
    Ed2kHashResult,
    Ed2kHasher,
    ed2k_hash_data,
    ed2k_hash_file,
)
from .md4 import MD4, md4_digest

__all__ = [
    "PARTSIZE",
    "MD4",
    "md4_digest",
    "Ed2kHashResult",
    "Ed2kHasher",
    "ed2k_hash_data",
    "ed2k_hash_file",
]
