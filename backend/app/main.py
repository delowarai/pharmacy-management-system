from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pharmacy.db")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-me")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
password_hash = PasswordHash.recommended()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(String(30), default="sales")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Medicine(Base):
    __tablename__ = "medicines"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    generic_name: Mapped[str] = mapped_column(String(160), default="")
    category: Mapped[str] = mapped_column(String(80), default="General")
    manufacturer: Mapped[str] = mapped_column(String(120), default="")
    strength: Mapped[str] = mapped_column(String(60), default="")
    dosage_form: Mapped[str] = mapped_column(String(60), default="Tablet")
    unit: Mapped[str] = mapped_column(String(30), default="pcs")
    barcode: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    reorder_level: Mapped[int] = mapped_column(default=10)
    active: Mapped[bool] = mapped_column(default=True)
    batches: Mapped[list[Batch]] = relationship(back_populates="medicine")


class Batch(Base):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(primary_key=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"), index=True)
    batch_no: Mapped[str] = mapped_column(String(80))
    expiry_date: Mapped[date] = mapped_column(Date)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    qty: Mapped[int] = mapped_column(default=0)
    medicine: Mapped[Medicine] = relationship(back_populates="batches")


class Party(Base):
    __tablename__ = "parties"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)  # customer/supplier
    name: Mapped[str] = mapped_column(String(140), index=True)
    phone: Mapped[str] = mapped_column(String(40), default="")
    address: Mapped[str] = mapped_column(String(250), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)  # sale/purchase
    invoice_no: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    party_id: Mapped[int | None] = mapped_column(ForeignKey("parties.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    due: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    items: Mapped[list[TransactionItem]] = relationship(cascade="all, delete-orphan")


class TransactionItem(Base):
    __tablename__ = "transaction_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"))
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
    qty: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(80))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    note: Mapped[str] = mapped_column(String(250), default="")
    date: Mapped[date] = mapped_column(Date, default=date.today)


class Audit(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    module: Mapped[str] = mapped_column(String(60))
    record_id: Mapped[str] = mapped_column(String(60), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MedicineIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    generic_name: str = ""
    category: str = "General"
    manufacturer: str = ""
    strength: str = ""
    dosage_form: str = "Tablet"
    unit: str = "pcs"
    barcode: str | None = None
    reorder_level: int = Field(default=10, ge=0)


class MedicineOut(MedicineIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    active: bool
    stock: int = 0


class PartyIn(BaseModel):
    name: str
    phone: str = ""
    address: str = ""
    email: EmailStr | str = ""


class BatchIn(BaseModel):
    medicine_id: int
    batch_no: str
    expiry_date: date
    purchase_price: Decimal = Field(ge=0)
    sale_price: Decimal = Field(ge=0)
    qty: int = Field(default=0, ge=0)


class ItemIn(BaseModel):
    medicine_id: int
    batch_id: int | None = None
    qty: int = Field(gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)


class TxIn(BaseModel):
    party_id: int | None = None
    invoice_no: str | None = None
    items: list[ItemIn] = Field(min_length=1)
    discount: Decimal = Field(default=0, ge=0)
    paid: Decimal = Field(default=0, ge=0)
    payment_method: str = "cash"


class ExpenseIn(BaseModel):
    category: str
    amount: Decimal = Field(gt=0)
    payment_method: str = "cash"
    note: str = ""
    date: date = Field(default_factory=date.today)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Db = Annotated[Session, Depends(db_session)]


def current_user(token: Annotated[str, Depends(oauth2)], db: Db) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.get(User, int(payload["sub"]))
    except Exception:
        user = None
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Invalid or expired login")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def audit(db: Session, user: User, action: str, module: str, record_id: int | str = ""):
    db.add(Audit(user_id=user.id, action=action, module=module, record_id=str(record_id)))


app = FastAPI(title="Pharmacy Management API", version="1.0.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username == "admin")):
            db.add(User(name="Administrator", username="admin", email="admin@example.com", password_hash=password_hash.hash("Admin@123"), role="admin"))
            db.commit()


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc)}


@app.post("/api/auth/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Db):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not password_hash.verify(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password")
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    token = jwt.encode({"sub": str(user.id), "role": user.role, "exp": exp}, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "name": user.name, "role": user.role}}


@app.get("/api/auth/me")
def me(user: CurrentUser):
    return {"id": user.id, "name": user.name, "username": user.username, "role": user.role}


@app.get("/api/medicines")
def medicines(db: Db, user: CurrentUser, q: str = ""):
    rows = db.scalars(select(Medicine).where(Medicine.active, Medicine.name.ilike(f"%{q}%")).order_by(Medicine.name)).all()
    return [{**MedicineOut.model_validate(m).model_dump(), "stock": sum(b.qty for b in m.batches), "sale_price": min((b.sale_price for b in m.batches if b.qty > 0 and b.expiry_date >= date.today()), default=0)} for m in rows]


@app.post("/api/medicines", response_model=MedicineOut)
def create_medicine(data: MedicineIn, db: Db, user: CurrentUser):
    m = Medicine(**data.model_dump())
    db.add(m); db.flush(); audit(db, user, "create", "medicine", m.id); db.commit(); db.refresh(m)
    return MedicineOut.model_validate(m)


@app.put("/api/medicines/{medicine_id}", response_model=MedicineOut)
def update_medicine(medicine_id: int, data: MedicineIn, db: Db, user: CurrentUser):
    m = db.get(Medicine, medicine_id)
    if not m: raise HTTPException(404, "Medicine not found")
    for k, v in data.model_dump().items(): setattr(m, k, v)
    audit(db, user, "update", "medicine", m.id); db.commit(); db.refresh(m)
    return MedicineOut.model_validate(m)


@app.get("/api/inventory")
def inventory(db: Db, user: CurrentUser, expiring_days: int = 90):
    limit = date.today() + timedelta(days=expiring_days)
    rows = db.execute(select(Batch, Medicine).join(Medicine).order_by(Batch.expiry_date)).all()
    return [{"id": b.id, "medicine_id": m.id, "medicine": m.name, "batch_no": b.batch_no, "expiry_date": b.expiry_date, "purchase_price": b.purchase_price, "sale_price": b.sale_price, "qty": b.qty, "expired": b.expiry_date < date.today(), "near_expiry": date.today() <= b.expiry_date <= limit} for b, m in rows]


@app.post("/api/inventory/adjust")
def adjust(batch_id: int, qty_change: int, reason: str, db: Db, user: CurrentUser):
    if user.role not in ("admin", "manager", "pharmacist"): raise HTTPException(403, "Permission denied")
    b = db.get(Batch, batch_id)
    if not b or b.qty + qty_change < 0: raise HTTPException(400, "Invalid batch or quantity")
    b.qty += qty_change; audit(db, user, f"adjust {qty_change}: {reason}", "inventory", b.id); db.commit()
    return {"ok": True, "qty": b.qty}


@app.get("/api/{kind}")
def parties(kind: str, db: Db, user: CurrentUser):
    if kind not in ("customers", "suppliers"): raise HTTPException(404)
    singular = kind[:-1]
    return db.scalars(select(Party).where(Party.kind == singular).order_by(Party.name)).all()


@app.post("/api/{kind}")
def create_party(kind: str, data: PartyIn, db: Db, user: CurrentUser):
    if kind not in ("customers", "suppliers"): raise HTTPException(404)
    p = Party(kind=kind[:-1], **data.model_dump()); db.add(p); db.flush(); audit(db, user, "create", kind[:-1], p.id); db.commit(); db.refresh(p)
    return p


def make_tx(kind: str, data: TxIn, db: Session, user: User):
    invoice = data.invoice_no or f"{kind[:1].upper()}{datetime.now():%Y%m%d%H%M%S%f}"
    tx = Transaction(kind=kind, invoice_no=invoice, party_id=data.party_id, user_id=user.id, subtotal=0, discount=data.discount, total=0, paid=data.paid, due=0, payment_method=data.payment_method)
    db.add(tx); db.flush(); subtotal = Decimal("0")
    for item in data.items:
        if kind == "purchase":
            if item.batch_id:
                batch = db.get(Batch, item.batch_id)
                if not batch or batch.medicine_id != item.medicine_id: raise HTTPException(400, "Invalid batch")
                batch.qty += item.qty
            else:
                raise HTTPException(400, "Create a batch first via /api/batches")
            price = item.unit_price if item.unit_price is not None else batch.purchase_price
            chosen = [(batch, item.qty)]
        else:
            need = item.qty; chosen = []
            query = select(Batch).where(Batch.medicine_id == item.medicine_id, Batch.qty > 0, Batch.expiry_date >= date.today()).order_by(Batch.expiry_date).with_for_update()
            batches = [db.get(Batch, item.batch_id)] if item.batch_id else db.scalars(query).all()
            for batch in batches:
                if not batch or batch.qty <= 0: continue
                take = min(need, batch.qty); chosen.append((batch, take)); need -= take
                if need == 0: break
            if need: raise HTTPException(400, f"Insufficient stock for medicine {item.medicine_id}")
            price = item.unit_price if item.unit_price is not None else chosen[0][0].sale_price
        for batch, qty in chosen:
            if kind == "sale": batch.qty -= qty
            line_total = Decimal(qty) * Decimal(price)
            db.add(TransactionItem(transaction_id=tx.id, medicine_id=item.medicine_id, batch_id=batch.id, qty=qty, unit_price=price, total=line_total))
            subtotal += line_total
    tx.subtotal = subtotal; tx.total = max(Decimal("0"), subtotal - data.discount); tx.paid = min(data.paid, tx.total); tx.due = tx.total - tx.paid
    if data.party_id and tx.due:
        party = db.get(Party, data.party_id)
        if not party or party.kind != ("customer" if kind == "sale" else "supplier"): raise HTTPException(400, "Invalid party")
        party.balance += tx.due
    audit(db, user, "create", kind, tx.id); db.commit(); db.refresh(tx)
    return {"id": tx.id, "invoice_no": tx.invoice_no, "subtotal": tx.subtotal, "discount": tx.discount, "total": tx.total, "paid": tx.paid, "due": tx.due, "created_at": tx.created_at}


@app.post("/api/batches")
def create_batch(data: BatchIn, db: Db, user: CurrentUser):
    if not db.get(Medicine, data.medicine_id): raise HTTPException(404, "Medicine not found")
    b = Batch(**data.model_dump()); db.add(b); db.flush(); audit(db, user, "create", "batch", b.id); db.commit(); db.refresh(b)
    return b


@app.post("/api/sales")
def create_sale(data: TxIn, db: Db, user: CurrentUser): return make_tx("sale", data, db, user)


@app.post("/api/purchases")
def create_purchase(data: TxIn, db: Db, user: CurrentUser): return make_tx("purchase", data, db, user)


@app.get("/api/transactions")
def transactions(db: Db, user: CurrentUser, kind: str | None = None, limit: int = Query(100, le=500)):
    stmt = select(Transaction).order_by(Transaction.created_at.desc()).limit(limit)
    if kind: stmt = stmt.where(Transaction.kind == kind)
    return db.scalars(stmt).all()


@app.post("/api/expenses")
def add_expense(data: ExpenseIn, db: Db, user: CurrentUser):
    e = Expense(**data.model_dump()); db.add(e); db.flush(); audit(db, user, "create", "expense", e.id); db.commit(); db.refresh(e); return e


@app.get("/api/expenses")
def expenses(db: Db, user: CurrentUser): return db.scalars(select(Expense).order_by(Expense.date.desc())).all()


@app.get("/api/dashboard")
def dashboard(db: Db, user: CurrentUser):
    start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
    sales = db.scalar(select(func.coalesce(func.sum(Transaction.total), 0)).where(Transaction.kind == "sale", Transaction.created_at >= start))
    purchases = db.scalar(select(func.coalesce(func.sum(Transaction.total), 0)).where(Transaction.kind == "purchase", Transaction.created_at >= start))
    stock_value = db.scalar(select(func.coalesce(func.sum(Batch.qty * Batch.purchase_price), 0)))
    low = db.scalar(select(func.count()).select_from(Medicine).where(Medicine.reorder_level >= select(func.coalesce(func.sum(Batch.qty), 0)).where(Batch.medicine_id == Medicine.id).scalar_subquery()))
    expiry = db.scalar(select(func.count()).select_from(Batch).where(Batch.qty > 0, Batch.expiry_date <= date.today() + timedelta(days=90)))
    receivable = db.scalar(select(func.coalesce(func.sum(Party.balance), 0)).where(Party.kind == "customer"))
    payable = db.scalar(select(func.coalesce(func.sum(Party.balance), 0)).where(Party.kind == "supplier"))
    return {"today_sales": sales, "today_purchases": purchases, "stock_value": stock_value, "low_stock": low, "near_expiry": expiry, "receivable": receivable, "payable": payable}


@app.get("/api/reports/profit")
def profit(db: Db, user: CurrentUser, date_from: date, date_to: date):
    start = datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc); end = datetime.combine(date_to + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    revenue = db.scalar(select(func.coalesce(func.sum(Transaction.total), 0)).where(Transaction.kind == "sale", Transaction.created_at >= start, Transaction.created_at < end))
    cost = db.scalar(select(func.coalesce(func.sum(TransactionItem.qty * Batch.purchase_price), 0)).join(Transaction).join(Batch, Batch.id == TransactionItem.batch_id).where(Transaction.kind == "sale", Transaction.created_at >= start, Transaction.created_at < end))
    expenses = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.date >= date_from, Expense.date <= date_to))
    return {"revenue": revenue, "cost": cost, "expenses": expenses, "gross_profit": revenue - cost, "net_profit": revenue - cost - expenses}
