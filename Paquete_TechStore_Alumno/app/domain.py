
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone


class DomainException(Exception):
    pass


class InvalidOrderData(DomainException):
    pass


class InvalidOrderTransition(DomainException):
    pass


class OrderItemLimitExceeded(DomainException):
    pass


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self):
        if not self.amount.is_finite() or self.amount < 0:
            raise InvalidOrderData("Monto inválido")

    def add(self, other):
        if self.currency != other.currency:
            raise InvalidOrderData("Monedas distintas")
        return Money(self.amount + other.amount, self.currency)

@dataclass(frozen=True)
class Customer:
    id: str
    is_vip: bool = False
    active: bool = True


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if not self.sku.strip() or self.quantity <= 0:
            raise InvalidOrderData("Artículo inválido")

    @property
    def subtotal(self):
        return Money(self.unit_price.amount * self.quantity)


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


@dataclass
class Order:
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = field(default_factory=list)
    events: list = field(default_factory=list)    
    @property
    def units(self):
        return sum(item.quantity for item in self.items)

    @property
    def total(self):
        amount = sum(
            (item.subtotal.amount for item in self.items),
            Decimal("0")
        )
        return Money(amount)

    
    def add_item(self, item: OrderItem):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition(
                "Solo se pueden modificar pedidos en DRAFT"
            )

        if self.units + item.quantity > 20:
            raise OrderItemLimitExceeded(
                "El pedido no puede superar 20 unidades"
            )

        if item.unit_price.currency != "MXN":
            raise InvalidOrderData(
                "La moneda del artículo debe ser MXN"
            )

        self.items.append(item)

    
    def confirm(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition(
                "Solo se pueden confirmar pedidos en DRAFT"
            )

        if not self.items:
            raise InvalidOrderData(
                "No se puede confirmar un pedido vacío"
            )

        if not self.customer.active:
            raise InvalidOrderData(
                "No se puede confirmar un pedido de un cliente inactivo"
            )

        self.status = OrderStatus.CONFIRMED
        self.events.append(
            DomainEvent("OrderConfirmed", self.id)
        )


    def ship(self, tracking_number: str):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition(
                "Solo se pueden enviar pedidos CONFIRMED"
            )

        if not tracking_number.strip():
            raise InvalidOrderData(
                "El número de guía es obligatorio"
            )

        self.status = OrderStatus.SHIPPED
        self.events.append(
            DomainEvent("OrderShipped", self.id)
        )

    
    def cancel(self, reason: str):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition(
                "Solo se pueden cancelar pedidos CONFIRMED"
            )

        if not reason.strip():
            raise InvalidOrderData(
                "El motivo de cancelación es obligatorio"
            )

        self.status = OrderStatus.CANCELLED
        self.events.append(
            DomainEvent("OrderCancelled", self.id)
        )

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition(
                "Solo se pueden entregar pedidos SHIPPED"
            )

        self.status = OrderStatus.DELIVERED
        self.events.append(
            DomainEvent("OrderDelivered", self.id)
        )

    def return_order(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition(
                "Solo se pueden devolver pedidos SHIPPED"
            )

        self.status = OrderStatus.RETURNED
        self.events.append(
            DomainEvent("OrderReturned", self.id)
        )
        
@dataclass(frozen=True)
class DomainEvent:
    name: str
    order_id: str
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )





