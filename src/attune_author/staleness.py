"""Staleness detection — re-exported from attune_help.staleness.

All staleness types and functions now live in attune-help so that
both attune-author and attune-ai can depend on the same
implementation. This module is a thin shim kept for backward
compatibility of any direct ``from attune_author.staleness import ...``
imports.
"""

from __future__ import annotations

from attune_help.staleness import (
    DocStaleness,
    FeatureStaleness,
    StalenessReport,
    _read_frontmatter_value,
    build_doc_footer,
    check_staleness,
    compute_semantic_hash,
    compute_source_hash,
    parse_doc_footer,
)

__all__ = [
    "DocStaleness",
    "FeatureStaleness",
    "StalenessReport",
    "_read_frontmatter_value",
    "build_doc_footer",
    "check_staleness",
    "compute_semantic_hash",
    "compute_source_hash",
    "parse_doc_footer",
]
