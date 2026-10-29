
from decimal import Decimal
import csv
from pathlib import Path

from cargar_csv import load_fixture
from app.domain import (
    OrderItem,
    Money,
    InvalidOrderData,
    InvalidOrderTransition,
    OrderItemLimitExceeded,
)
from app.specifications import (
    calculate_discount,
    calculate_discount_amount,
    calculate_final_total,
)


def mostrar_inicio(order):
    print(f"Estado inicial: {order.status.value}")
    print(f"Unidades: {order.units}")
    print(f"Total: ${order.total.amount} MXN")


def mostrar_final(order):
    print(f"Estado final: {order.status.value}")
    print(
        "Eventos:",
        [event.name for event in order.events]
        if order.events
        else "Ninguno",
    )


def ejecutar_descuento(order_id):
    order = load_fixture()[order_id]
    print(f"\nPedido: {order.id}")
    mostrar_inicio(order)
    print(f"Descuento: {calculate_discount(order) * 100}%")
    print(f"Monto descontado: ${calculate_discount_amount(order)} MXN")
    print(f"Total final: ${calculate_final_total(order)} MXN")
    mostrar_final(order)


def ejecutar_escenario(numero, descripcion, funcion):
    print("\n" + "=" * 55)
    print(f"E{numero:02d} - {descripcion}")
    print("=" * 55)
    funcion()


def generar_bitacora():
    filas = [
        {
            "caso": "E01",
            "estado_inicial": "DRAFT",
            "operacion": "Calcular descuento de O001",
            "resultado_real": "Descuento del 10%; total final $1890 MXN",
            "explicacion": "Cumple las condiciones para el descuento del 10%.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E02",
            "estado_inicial": "DRAFT",
            "operacion": "Calcular descuento de O002",
            "resultado_real": "Sin descuento; total final $1050 MXN",
            "explicacion": "No cumple las condiciones de descuento.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E03",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar O003",
            "resultado_real": "Operación rechazada",
            "explicacion": "El cliente está inactivo.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E04",
            "estado_inicial": "DRAFT",
            "operacion": "Calcular descuento de O005",
            "resultado_real": "Sin descuento",
            "explicacion": "La promoción activa impide aplicar el descuento.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E05",
            "estado_inicial": "DRAFT",
            "operacion": "Calcular descuento de O006",
            "resultado_real": "Descuento del 5%; total final $17100 MXN",
            "explicacion": "El pedido cumple la regla del 5%.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E06",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar O007",
            "resultado_real": "Operación rechazada",
            "explicacion": "No se permite confirmar un pedido vacío.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E07",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar O008 con 20 unidades",
            "resultado_real": "Confirmación exitosa",
            "explicacion": "El límite de 20 unidades está permitido.",
            "eventos": "OrderConfirmed",
        },
        {
            "caso": "E08",
            "estado_inicial": "DRAFT",
            "operacion": "Agregar 2 unidades a O009, que ya tiene 19",
            "resultado_real": "Operación rechazada; conserva 19 unidades",
            "explicacion": "La operación excedería el límite de 20 unidades.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E09",
            "estado_inicial": "DRAFT",
            "operacion": "Calcular descuento de O010",
            "resultado_real": "Sin descuento; total $500 MXN",
            "explicacion": "El total debe ser mayor que $500 para cumplir la regla.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E10",
            "estado_inicial": "DRAFT",
            "operacion": "Calcular descuento de O011",
            "resultado_real": "Sin descuento",
            "explicacion": "El pedido tiene solo 3 unidades.",
            "eventos": "Ninguno",
        },
        {
            "caso": "E11",
            "estado_inicial": "DRAFT",
            "operacion": "Enviar O012 sin guía",
            "resultado_real": "Envío rechazado; estado CONFIRMED",
            "explicacion": "Se requiere una guía de seguimiento para enviar.",
            "eventos": "OrderConfirmed",
        },
        {
            "caso": "E12",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar O013 dos veces",
            "resultado_real": "La segunda confirmación fue rechazada",
            "explicacion": "No se permite confirmar un pedido ya confirmado.",
            "eventos": "OrderConfirmed",
        },
        {
            "caso": "E13",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar, enviar y cancelar O014",
            "resultado_real": "Cancelación rechazada; estado SHIPPED",
            "explicacion": "No se permite cancelar un pedido ya enviado.",
            "eventos": "OrderConfirmed, OrderShipped",
        },
        {
            "caso": "E14",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar, enviar y devolver O015",
            "resultado_real": "Devolución exitosa; estado RETURNED",
            "explicacion": "La devolución es válida después del envío.",
            "eventos": "OrderConfirmed, OrderShipped, OrderReturned",
        },
        {
            "caso": "E15",
            "estado_inicial": "DRAFT",
            "operacion": "Confirmar, enviar y entregar O016",
            "resultado_real": "Entrega exitosa; estado DELIVERED",
            "explicacion": "La transición a entregado se completó correctamente.",
            "eventos": "OrderConfirmed, OrderShipped, OrderDelivered",
        },
    ]

    ruta = Path(__file__).resolve().parent / "bitacora_escenarios.csv"

    with ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
        columnas = [
            "caso",
            "estado_inicial",
            "operacion",
            "resultado_real",
            "explicacion",
            "eventos",
        ]
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"\nBitácora generada correctamente: {ruta}")


# E01: descuento del 10 %
def caso_e01():
    ejecutar_descuento("O001")


# E02: pedido sin descuento
def caso_e02():
    ejecutar_descuento("O002")


# E03: cliente inactivo; confirmar debe fallar
def caso_e03():
    order = load_fixture()["O003"]
    mostrar_inicio(order)

    try:
        order.confirm()
        print("ERROR: se permitió confirmar el pedido")
    except InvalidOrderData as error:
        print("Rechazo esperado:", error)

    mostrar_final(order)


# E04: promoción activa; no debe aplicar descuento
def caso_e04():
    ejecutar_descuento("O005")


# E05: descuento del 5 %
def caso_e05():
    ejecutar_descuento("O006")


# E06: no se puede confirmar un pedido vacío
def caso_e06():
    order = load_fixture()["O007"]
    mostrar_inicio(order)

    try:
        order.confirm()
        print("ERROR: se permitió confirmar el pedido")
    except InvalidOrderData as error:
        print("Rechazo esperado:", error)

    mostrar_final(order)


# E07: se permiten exactamente 20 unidades
def caso_e07():
    order = load_fixture()["O008"]
    mostrar_inicio(order)

    try:
        order.confirm()
        print("Confirmación exitosa")
    except (InvalidOrderData, InvalidOrderTransition) as error:
        print("ERROR inesperado:", error)

    mostrar_final(order)


# E08: agregar 2 unidades a un pedido de 19
def caso_e08():
    order = load_fixture()["O009"]
    mostrar_inicio(order)

    try:
        order.add_item(
            OrderItem("SKU003", 2, Money(Decimal("120")))
        )
        print("ERROR: se permitió superar el límite")
    except OrderItemLimitExceeded as error:
        print("Rechazo esperado:", error)

    print("Unidades finales:", order.units)
    mostrar_final(order)


# E09: total exactamente igual a $500; sin descuento
def caso_e09():
    ejecutar_descuento("O010")


# E10: solo 3 unidades; no cumple el mínimo de 4
def caso_e10():
    ejecutar_descuento("O011")


# E11: la guía es obligatoria para enviar
def caso_e11():
    order = load_fixture()["O012"]
    mostrar_inicio(order)

    order.confirm()
    print("Después de confirmar:", order.status.value)

    try:
        order.ship("")
        print("ERROR: se permitió enviar sin guía")
    except InvalidOrderData as error:
        print("Rechazo esperado:", error)

    mostrar_final(order)


# E12: no se puede confirmar dos veces
def caso_e12():
    order = load_fixture()["O013"]
    mostrar_inicio(order)

    order.confirm()
    print("Primera confirmación:", order.status.value)

    try:
        order.confirm()
        print("ERROR: se permitió confirmar por segunda vez")
    except InvalidOrderTransition as error:
        print("Rechazo esperado:", error)

    mostrar_final(order)


# E13: no se puede cancelar después de enviar
def caso_e13():
    order = load_fixture()["O014"]
    mostrar_inicio(order)

    order.confirm()
    order.ship("GUIA123")
    print("Después del envío:", order.status.value)

    try:
        order.cancel("Cancelación solicitada")
        print("ERROR: se permitió cancelar después del envío")
    except InvalidOrderTransition as error:
        print("Rechazo esperado:", error)

    mostrar_final(order)


# E14: devolución válida desde SHIPPED
def caso_e14():
    order = load_fixture()["O015"]
    mostrar_inicio(order)

    order.confirm()
    order.ship("GUIA015")
    print("Antes de devolver:", order.status.value)

    order.return_order()

    mostrar_final(order)


# E15: entrega válida desde SHIPPED
def caso_e15():
    order = load_fixture()["O016"]
    mostrar_inicio(order)

    order.confirm()
    order.ship("GUIA016")
    print("Antes de entregar:", order.status.value)

    order.deliver()

    mostrar_final(order)



if __name__ == "__main__":
    escenarios = [
        (1, "Descuento del 10 %", caso_e01),
        (2, "Pedido sin descuento", caso_e02),
        (3, "Rechazo por cliente inactivo", caso_e03),
        (4, "Promoción activa", caso_e04),
        (5, "Descuento del 5 %", caso_e05),
        (6, "Pedido vacío", caso_e06),
        (7, "Límite de 20 unidades permitido", caso_e07),
        (8, "Exceso del límite de unidades", caso_e08),
        (9, "Total exactamente de $500", caso_e09),
        (10, "Solo 3 unidades", caso_e10),
        (11, "Guía obligatoria para enviar", caso_e11),
        (12, "No se puede confirmar dos veces", caso_e12),
        (13, "No se puede cancelar después de enviar", caso_e13),
        (14, "Devolución válida", caso_e14),
        (15, "Entrega válida", caso_e15),
        
    ]

    for numero, descripcion, funcion in escenarios:
        ejecutar_escenario(numero, descripcion, funcion)
        
    generar_bitacora()