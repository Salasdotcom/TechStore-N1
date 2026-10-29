
import pytest
from decimal import Decimal

from cargar_csv import load_fixture
from app.specifications import (
    Discount10Spec,
    Discount5Spec,
    DiscountEligibleSpec,
    calculate_discount,
    calculate_discount_amount,
    calculate_final_total,
)

from app.domain import (
    Customer,
    InvalidOrderData,
    InvalidOrderTransition,
    Money,
    Order,
    OrderItem,
    OrderItemLimitExceeded,
    OrderStatus,
)


def test_discount_10_percent():
    orders = load_fixture()
    order = orders["O001"]

    assert Discount10Spec().is_satisfied_by(order)
    assert calculate_discount(order) == Decimal("0.10")
    assert calculate_discount_amount(order) == Decimal("210.00")
    assert calculate_final_total(order) == Decimal("1890.00")


def test_discount_5_percent():
    orders = load_fixture()
    order = orders["O006"]

    assert Discount5Spec().is_satisfied_by(order)
    assert calculate_discount(order) == Decimal("0.05")
    assert calculate_discount_amount(order) == Decimal("900.00")
    assert calculate_final_total(order) == Decimal("17100.00")


def test_active_promotion_blocks_discount():
    orders = load_fixture()
    order = orders["O005"]

    assert not DiscountEligibleSpec().is_satisfied_by(order)
    assert calculate_discount(order) == Decimal("0")


def test_amount_equal_to_500_gets_no_discount():
    orders = load_fixture()
    order = orders["O010"]

    assert order.total.amount == Decimal("500.00")
    assert calculate_discount(order) == Decimal("0")
    assert calculate_final_total(order) == Decimal("500.00")


def test_non_vip_customer_does_not_get_10_percent():
    orders = load_fixture()
    order = orders["O002"]

    assert not Discount10Spec().is_satisfied_by(order)
    assert calculate_discount(order) == Decimal("0")


def test_vip_order_with_fewer_than_four_units_gets_no_10_percent():
    orders = load_fixture()
    order = orders["O011"]

    assert order.customer.is_vip
    assert order.units == 3
    assert not Discount10Spec().is_satisfied_by(order)
    assert calculate_discount(order) == Decimal("0")


def test_order_confirmation_and_shipping():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")
    item = OrderItem(
        sku="SKU_TEST",
        quantity=2,
        unit_price=Money(Decimal("100.00")),
    )

    order.add_item(item)

    assert order.status == OrderStatus.DRAFT

    order.confirm()
    assert order.status == OrderStatus.CONFIRMED

    order.ship("GUIA123")
    assert order.status == OrderStatus.SHIPPED

def test_cannot_ship_order_before_confirmation():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    with pytest.raises(InvalidOrderTransition):
        order.ship("GUIA123")


def test_cannot_confirm_empty_order():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    with pytest.raises(InvalidOrderData):
        order.confirm()


def test_cannot_confirm_order_for_inactive_customer():
    customer = Customer(id="C_TEST", is_vip=False, active=False)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    with pytest.raises(InvalidOrderData):
        order.confirm()


def test_order_cannot_exceed_20_units():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=20,
            unit_price=Money(Decimal("100.00")),
        )
    )

    assert order.units == 20

    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(
            OrderItem(
                sku="SKU_EXTRA",
                quantity=1,
                unit_price=Money(Decimal("50.00")),
            )
        )

    assert order.units == 20


def test_cannot_add_item_after_confirmation():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()

    with pytest.raises(InvalidOrderTransition):
        order.add_item(
            OrderItem(
                sku="SKU_EXTRA",
                quantity=1,
                unit_price=Money(Decimal("50.00")),
            )
        )

    assert order.units == 1
    assert order.status == OrderStatus.CONFIRMED


def test_cannot_confirm_order_twice():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()

    with pytest.raises(InvalidOrderTransition):
        order.confirm()

    assert order.status == OrderStatus.CONFIRMED


def test_cannot_cancel_order_before_confirmation():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    with pytest.raises(InvalidOrderTransition):
        order.cancel("El cliente cambió de opinión")

    assert order.status == OrderStatus.DRAFT


def test_cannot_ship_order_without_tracking_number():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()

    with pytest.raises(InvalidOrderData):
        order.ship("")

    assert order.status == OrderStatus.CONFIRMED


def test_cannot_cancel_order_after_shipping():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")

    with pytest.raises(InvalidOrderTransition):
        order.cancel("El cliente cambió de opinión")

    assert order.status == OrderStatus.SHIPPED


def test_can_return_shipped_order():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")
    order.return_order()

    assert order.status == OrderStatus.RETURNED
    assert order.events[-1].name == "OrderReturned"


def test_can_deliver_shipped_order():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")
    order.deliver()

    assert order.status == OrderStatus.DELIVERED
    assert order.events[-1].name == "OrderDelivered"


def test_order_records_events_in_correct_order():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")

    assert len(order.events) == 2
    assert order.events[0].name == "OrderConfirmed"
    assert order.events[1].name == "OrderShipped"
    assert all(event.order_id == "O_TEST" for event in order.events)

    
def test_cannot_deliver_returned_order():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")
    order.return_order()

    with pytest.raises(InvalidOrderTransition):
        order.deliver()

    assert order.status == OrderStatus.RETURNED


def test_cannot_return_delivered_order():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")
    order.deliver()

    with pytest.raises(InvalidOrderTransition):
        order.return_order()

    assert order.status == OrderStatus.DELIVERED


def test_return_event_contains_correct_order_id():
    customer = Customer(id="C_TEST", is_vip=False, active=True)
    order = Order(customer=customer, id="O_TEST")

    order.add_item(
        OrderItem(
            sku="SKU_TEST",
            quantity=1,
            unit_price=Money(Decimal("100.00")),
        )
    )

    order.confirm()
    order.ship("GUIA123")
    order.return_order()

    event = order.events[-1]

    assert event.name == "OrderReturned"
    assert event.order_id == "O_TEST"
