# TechStore

API REST para gestionar pedidos de una tienda tecnológica. El proyecto implementa reglas de negocio para calcular descuentos, controlar las transiciones de estado de los pedidos y registrar eventos de dominio.

## Características

- Carga de datos de prueba desde archivos CSV.
- Consulta de pedidos y sus detalles.
- Cálculo de descuentos y totales finales.
- Gestión del ciclo de vida de los pedidos:
  - Confirmación.
  - Envío con número de seguimiento.
  - Cancelación con motivo.
  - Entrega.
  - Devolución.
- Validación de reglas de negocio y transiciones de estado.
- Registro de eventos después de operaciones válidas.
- API REST desarrollada con FastAPI.
- Documentación interactiva mediante Swagger UI.
- Pruebas automatizadas con `pytest`.

## Tecnologías

- Python
- FastAPI
- Uvicorn
- Pydantic
- pytest

## Requisitos previos

- Python instalado.
- Una terminal de PowerShell (Windows) o una terminal compatible.
- El repositorio descargado o clonado en tu equipo.

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Paquete_TechStore_Alumno
```

Sustituye `<URL_DEL_REPOSITORIO>` por la dirección real del repositorio en GitHub.

### 2. Crear un entorno virtual

Windows PowerShell:

```powershell
python -m venv .venv
```

### 3. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución del script, puedes permitirla solo para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Después, vuelve a activar el entorno virtual.

### 4. Instalar dependencias

Si el proyecto incluye un archivo `requirements.txt`, ejecuta:

```powershell
python -m pip install -r requirements.txt
```

Si todavía no existe ese archivo, instala las dependencias utilizadas por el proyecto:

```powershell
python -m pip install fastapi uvicorn pytest httpx
```

## Uso

Ejecuta los comandos desde la carpeta raíz del proyecto, donde se encuentran `app`, `tests` y `cargar_csv.py`.

### Cargar los datos CSV

```powershell
python cargar_csv.py
```

### Iniciar la API

```powershell
python -m uvicorn app.api:app --reload
```

Cuando el servidor se inicie, abre estas direcciones en el navegador:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Página principal:** http://127.0.0.1:8000/
- **Lista de pedidos:** http://127.0.0.1:8000/pedidos

Para detener el servidor, pulsa `Ctrl + C` en la terminal donde se está ejecutando.

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Comprueba que la API está funcionando. |
| `GET` | `/pedidos` | Obtiene la lista de pedidos. |
| `GET` | `/pedidos/{pedido_id}` | Consulta un pedido por su identificador. |
| `GET` | `/pedidos/{pedido_id}/descuento` | Consulta el descuento y el total final de un pedido. |
| `POST` | `/pedidos/{pedido_id}/confirmar` | Confirma un pedido válido. |
| `POST` | `/pedidos/{pedido_id}/enviar` | Envía un pedido con número de seguimiento. |
| `POST` | `/pedidos/{pedido_id}/cancelar` | Cancela un pedido con un motivo. |
| `POST` | `/pedidos/{pedido_id}/entregar` | Registra la entrega de un pedido. |
| `POST` | `/pedidos/{pedido_id}/devolver` | Registra la devolución de un pedido. |

`{pedido_id}` representa el identificador real del pedido, por ejemplo, `O001`.

### Códigos HTTP relevantes

- **200 OK:** la solicitud se procesó correctamente.
- **400 Bad Request:** la solicitud incumple una validación definida por la aplicación.
- **404 Not Found:** el pedido solicitado no existe.
- **409 Conflict:** la operación no es válida para el estado actual del pedido.
- **422 Unprocessable Entity:** los datos de entrada no cumplen el esquema esperado por la API.

## Reglas de descuentos

Las reglas se encuentran en `app/specifications.py`.

- **Descuento del 10 %:** requiere que el cliente sea VIP, que el total sea superior a 500 MXN, que el pedido contenga al menos cuatro unidades y que no exista una promoción activa.
- **Descuento del 5 %:** requiere que el total sea superior a 5,000 MXN y que no exista una promoción activa.
- Si hay una promoción activa, no se aplica ninguno de estos descuentos.
- El límite es estricto: un total exactamente igual a 500 MXN no cumple la condición `> 500`.
- La regla del 10 % tiene prioridad cuando corresponde aplicarla.

## Pruebas automatizadas

Desde la raíz del proyecto y con el entorno virtual activo, ejecuta:

```powershell
python -m pytest -v
```

La suite verificada durante el desarrollo contiene **30 pruebas**: 22 relacionadas con el dominio y 8 relacionadas con la API. En la verificación realizada, las 30 pruebas pasaron correctamente.

## Estructura del proyecto

```text
Paquete_TechStore_Alumno/
├── app/
│   ├── api.py
│   ├── domain.py
│   └── specifications.py
├── tests/
│   ├── test_api.py
│   └── test_domain.py
├── cargar_csv.py
├── ejecutar_escenarios.py
├── bitacora_escenarios.csv
├── .venv/
└── README.md
```

Esta estructura representa los archivos principales identificados durante el desarrollo. Los archivos CSV de entrada pueden estar ubicados en otras carpetas del proyecto según la configuración del programa.

**Nota:** no subas la carpeta `.venv` a GitHub. Debe permanecer local; el entorno se puede recrear siguiendo las instrucciones de instalación.

## Conceptos aplicados

- **Separación de responsabilidades:** la API, el dominio y las reglas de negocio están organizados por separado.
- **`Decimal`:** se utiliza para operaciones monetarias que requieren precisión decimal.
- **Specifications:** encapsulan condiciones de negocio, como los requisitos para aplicar descuentos.
- **Transiciones de estado:** controlan qué operaciones se permiten durante el ciclo de vida de un pedido.
- **Eventos de dominio:** registran las operaciones que se completaron válidamente.
- **Pruebas automatizadas:** ayudan a verificar el comportamiento esperado y a detectar regresiones.

## Objetivo académico

El proyecto permite practicar el diseño de un dominio de pedidos, la aplicación de reglas de negocio, la creación de una API REST, la validación de solicitudes y la automatización de pruebas con Python.

## Autor

Proyecto académico desarrollado como ejercicio de programación y diseño de software.
