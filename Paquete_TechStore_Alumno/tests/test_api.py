
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["mensaje"] == "API de TechStore funcionando"


def test_listar_pedidos():
    response = client.get("/pedidos")

    assert response.status_code == 200
    assert len(response.json()) == 16


def test_obtener_pedido_existente():
    response = client.get("/pedidos/O001")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == "O001"
    assert data["cliente_id"] == "C001"
    assert data["unidades"] == 4
    assert data["total"] == "2100.00"


def test_obtener_pedido_inexistente():
    response = client.get("/pedidos/O999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido no encontrado"


def test_descuento_10_por_ciento():
    response = client.get("/pedidos/O001/descuento")

    assert response.status_code == 200

    data = response.json()
    assert data["descuento_porcentaje"] == "10.00"
    assert data["monto_descuento"] == "210.00"
    assert data["total_final"] == "1890.00"


def test_descuento_5_por_ciento():
    response = client.get("/pedidos/O006/descuento")

    assert response.status_code == 200

    data = response.json()
    assert data["descuento_porcentaje"] == "5.00"
    assert data["monto_descuento"] == "900.00"
    assert data["total_final"] == "17100.00"


def test_pedido_con_promocion_sin_descuento():
    response = client.get("/pedidos/O005/descuento")

    assert response.status_code == 200

    data = response.json()
    assert data["descuento_porcentaje"] == "0"
    assert data["monto_descuento"] == "0.00"
    assert data["total_final"] == "2100.00"


def test_descuento_pedido_inexistente():
    response = client.get("/pedidos/O999/descuento")

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido no encontrado"
