"""SQLAlchemy domain models.

The first release keeps model declarations in ``app.main`` to preserve backward
compatibility. New domain models should be placed in this package and imported
before ``Base.metadata.create_all`` or Alembic migrations run.
"""

