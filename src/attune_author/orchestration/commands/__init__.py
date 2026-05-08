"""Command implementations registered with the orchestration runtime.

Importing a submodule (``rag``, ``author``, ``help``) calls
:func:`attune_author.orchestration.register` for each spec it owns.
The package-level docstring stays the registry of where commands
live; the registry itself is :mod:`attune_author.orchestration.registry`.
"""
