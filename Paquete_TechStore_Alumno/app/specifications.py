from abc import ABC, abstractmethod
from decimal import Decimal

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, order) -> bool:
        pass

    def __and__(self, other):
        return AndSpec(self, other)

    def __or__(self, other):
        return OrSpec(self, other)

    def __invert__(self):
        return NotSpec(self)


class AndSpec(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order):
        return (
            self.left.is_satisfied_by(order)
            and self.right.is_satisfied_by(order)
        )

class OrSpec(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order):
        return (
            self.left.is_satisfied_by(order)
            or self.right.is_satisfied_by(order)
        )


class NotSpec(Specification):
    def __init__(self, specification):
        self.specification = specification

    def is_satisfied_by(self, order):
        return not self.specification.is_satisfied_by(order)


class MinimumAmountSpec(Specification):
    def __init__(self, minimum_amount):
        self.minimum_amount = minimum_amount

    def is_satisfied_by(self, order):
        return order.total.amount > self.minimum_amount

class VIPCustomerSpec(Specification):
    def is_satisfied_by(self, order):
        return order.customer.is_vip

class MinimumUnitsSpec(Specification):
    def __init__(self, minimum_units):
        self.minimum_units = minimum_units

    def is_satisfied_by(self, order):
        return order.units >= self.minimum_units

class ActivePromotionSpec(Specification):
    def is_satisfied_by(self, order):
        return order.has_promotion

class Discount10Spec(Specification):
    def __init__(self):
        self.rule = (
            MinimumAmountSpec(500)
            & VIPCustomerSpec()
            & MinimumUnitsSpec(4)
            & ~ActivePromotionSpec()
        )

    def is_satisfied_by(self, order):
        return self.rule.is_satisfied_by(order)

class Discount5Spec(Specification):
    def __init__(self):
        self.rule = (
            MinimumAmountSpec(5000)
            & ~ActivePromotionSpec()
        )

    def is_satisfied_by(self, order):
        return self.rule.is_satisfied_by(order)

class DiscountEligibleSpec(Specification):
    def __init__(self):
        self.rule = Discount10Spec() | Discount5Spec()

    def is_satisfied_by(self, order):
        return self.rule.is_satisfied_by(order)

def calculate_discount(order):
    """Devuelve el porcentaje de descuento aplicable al pedido."""
    if Discount10Spec().is_satisfied_by(order):
        return Decimal("0.10")

    if Discount5Spec().is_satisfied_by(order):
        return Decimal("0.05")

    return Decimal("0")


def calculate_discount_amount(order):
    discount_rate = calculate_discount(order)
    return (order.total.amount * discount_rate).quantize(Decimal("0.01"))


def calculate_final_total(order):
    return order.total.amount - calculate_discount_amount(order)
