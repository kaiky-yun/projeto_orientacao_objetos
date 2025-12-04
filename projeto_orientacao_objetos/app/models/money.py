from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

class Money:

    __slots__ = ('_amount',)

    def __init__(self, amount):
        try:
            value = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        except (InvalidOperation, ValueError) as e:
            raise ValueError("Valor monetário inválido") from e

        self._amount = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def amount(self):
        return self._amount

    def __add__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Operação com Money requer outro Money")
        return Money(self.amount + other.amount)

    def __sub__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Operação com Money requer outro Money")
        return Money(self.amount - other.amount)

    def __neg__(self):
        return Money(-self.amount)

    def __mul__(self, other):
        return Money(self.amount * Decimal(str(other)))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return Money(self.amount / Decimal(str(other)))

    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount

    def __lt__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Comparação com Money requer outro Money")
        return self.amount < other.amount

    def __le__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Comparação com Money requer outro Money")
        return self.amount <= other.amount

    def __gt__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Comparação com Money requer outro Money")
        return self.amount > other.amount

    def __ge__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Comparação com Money requer outro Money")
        return self.amount >= other.amount

    def __repr__(self):
        return f"Money({str(self.amount)})"

    def __str__(self):
        return f"R$ {self.amount:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

    def to_dict(self):
        return {"amount": str(self.amount)}

    @staticmethod
    def from_dict(data):
        return Money(Decimal(data["amount"]))
