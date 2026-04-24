"""Feature manifest — re-exported from attune_help.manifest.

All types and functions now live in attune-help so that both
attune-author and attune-ai can depend on the same implementation.
This module is a thin shim kept for backward compatibility of any
direct ``from attune_author.manifest import ...`` imports.
"""

from __future__ import annotations

from attune_help.manifest import (
    Feature,
    FeatureManifest,
    Manifest,
    is_safe_feature_name,
    load_manifest,
    match_files_to_features,
    resolve_topic,
    save_manifest,
    slugify,
)

# Private constant bootstrap.py depends on.
_MANIFEST_VERSION = 1

__all__ = [
    "Feature",
    "FeatureManifest",
    "Manifest",
    "_MANIFEST_VERSION",
    "is_safe_feature_name",
    "load_manifest",
    "match_files_to_features",
    "resolve_topic",
    "save_manifest",
    "slugify",
]
