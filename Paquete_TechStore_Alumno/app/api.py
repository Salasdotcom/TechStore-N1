
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cargar_csv import load_fixture
from app.domain import InvalidOrderData, InvalidOrderTransition
from app.specifications import (
    calculate_discount,
    calculate_discount_amount,
    calculate_final_total,
)

app = FastAPI(
    title="TechStore API",
    description="API para gestionar pedidos de TechStore",
    version="1.0.0",
)

orders = load_fixture()


class TrackingRequest(BaseModel):
    tracking_number: str


class CancellationRequest(BaseModel):
    reason: str


def obtener_o_error(pedido_id: str):
    order = orders.get(pedido_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado",
        )

    return order


def representar_pedido(order):
    return {
        "id": order.id,
        "cliente_id": order.customer.id,
        "estado": order.status.value,
        "unidades": order.units,
        "total": str(order.total.amount),
        "tiene_promocion": order.has_promotion,
    }


def ejecutar_operacion(order, operacion, *args):
    try:
        operacion(*args)
    except InvalidOrderData as error:
        raise HTTPException(status_code=400, detail=str(error))
    except InvalidOrderTransition as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "mensaje": "Operación realizada correctamente",
        "pedido": representar_pedido(order),
        "eventos": [event.name for event in order.events],
    }


@app.get("/")
def home():
    return {"mensaje": "API de TechStore funcionando"}


@app.get("/pedidos")
def listar_pedidos():
    return [representar_pedido(order) for order in orders.values()]


@app.get("/pedidos/{pedido_id}")
def obtener_pedido(pedido_id: str):
    return representar_pedido(obtener_o_error(pedido_id))


@app.get("/pedidos/{pedido_id}/descuento")
def obtener_descuento(pedido_id: str):
    order = obtener_o_error(pedido_id)

    descuento = calculate_discount(order)

    return {
        "pedido_id": order.id,
        "total_original": str(order.total.amount),
        "descuento_porcentaje": str(descuento * 100),
        "monto_descuento": str(calculate_discount_amount(order)),
        "total_final": str(calculate_final_total(order)),
    }


@app.post("/pedidos/{pedido_id}/confirmar")
def confirmar_pedido(pedido_id: str):
    order = obtener_o_error(pedido_id)
    return ejecutar_operacion(order, order.confirm)


@app.post("/pedidos/{pedido_id}/enviar")
def enviar_pedido(pedido_id: str, datos: TrackingRequest):
    order = obtener_o_error(pedido_id)
    return ejecutar_operacion(order, order.ship, datos.tracking_number)


@app.post("/pedidos/{pedido_id}/cancelar")
def cancelar_pedido(pedido_id: str, datos: CancellationRequest):
    order = obtener_o_error(pedido_id)
    return ejecutar_operacion(order, order.cancel, datos.reason)


@app.post("/pedidos/{pedido_id}/entregar")
def entregar_pedido(pedido_id: str):
    order = obtener_o_error(pedido_id)
    return ejecutar_operacion(order, order.deliver)


@app.post("/pedidos/{pedido_id}/devolver")
def devolver_pedido(pedido_id: str):
    order = obtener_o_error(pedido_id)
    return ejecutar_operacion(order, order.return_order)
