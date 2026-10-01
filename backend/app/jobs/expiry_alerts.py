from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session


def expiring_batches(session: Session, batch_model, *, within_days: int = 90):
    """Return in-stock batches expiring on or before the configured horizon."""
    horizon = date.today() + timedelta(days=within_days)
    statement = (
        select(batch_model)
        .where(batch_model.qty > 0, batch_model.expiry_date <= horizon)
        .order_by(batch_model.expiry_date)
    )
    return list(session.scalars(statement).all())

