from decimal import Decimal, ROUND_HALF_UP

MONEY_PLACES = Decimal("0.01")


def money(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def invoice_total(subtotal: Decimal, discount: Decimal = Decimal("0")) -> Decimal:
    return max(Decimal("0.00"), money(subtotal) - money(discount))


def due_amount(total: Decimal, paid: Decimal = Decimal("0")) -> Decimal:
    return max(Decimal("0.00"), money(total) - min(money(paid), money(total)))

