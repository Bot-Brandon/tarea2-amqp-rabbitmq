# Tarea 2: AMQP con RabbitMQ

**Integrantes:** Brandon Caravante y Nicolás Hermosillas.  
**Grupo:** 16.  
**Asignatura:** Taller de Redes y Servicios, 2026-2.

## Informe y video

- [Informe final en PDF](informe/t2_BrandonC_NicolasH.pdf).
- [Video de demostración en YouTube](https://youtu.be/W-tfNfFb-kM).

[![Ver demostración de AMQP con RabbitMQ](https://img.youtube.com/vi/W-tfNfFb-kM/hqdefault.jpg)](https://youtu.be/W-tfNfFb-kM)

## Objetivo y componentes

Implementar una comunicación AMQP 0-9-1 entre un servidor RabbitMQ y una aplicación cliente Python/Pika, ambos en contenedores Linux, y estudiar el tráfico generado.

- Servidor: `rabbitmq:4.4.0-management`.
- Cliente: Python 3.12 con Pika 1.3.2.
- Capturador: tcpdump dentro del contenedor cliente, interfaz eth0.
- Puerto del protocolo: TCP 5672 en la red de Compose, sin TLS.
- Panel web: <http://localhost:15672>, publicado solo en loopback.
- Credenciales de demostración: usuario `taller`, contraseña `taller-local-2026`.

La aplicación cliente publica y obtiene mensajes bajo demanda mediante Basic.Get. El broker administra las colas y sus entregas. El tráfico del panel HTTP es distinto del tráfico AMQP analizado.

## Estructura

```text
compose.yaml          Servicios y configuración de red
cliente/              Dockerfile, dependencias, pruebas y capturador
scripts/ejecutar.ps1   Ejecutor de las pruebas desde PowerShell
evidencias/           Capturas PCAP, JSON, registros e imágenes
informe/              PDF final
```

## Requisitos

Docker Desktop con motor Linux funcionando y Docker Compose disponible. En Windows, PowerShell para el script. Wireshark para inspeccionar las capturas. La primera construcción requiere Internet.

## Ejecutar desde la carpeta raíz del repositorio

Con Docker Desktop abierto:

```powershell
docker compose up -d --wait rabbitmq
docker compose build cliente
docker compose ps
```

El servidor debe aparecer `healthy`. Para ejecutar y capturar cada prueba:

```powershell
docker compose run --rm cliente P01
docker compose run --rm cliente P02
docker compose run --rm cliente P03
```

Para las tres pruebas en una sola captura, con registros e identificación de imágenes:

```powershell
& .\scripts\ejecutar.ps1
```

Las nuevas ejecuciones escriben en `evidencias` y reemplazan los archivos del mismo nombre. Conservar una copia de las evidencias originales antes de repetir las pruebas. El contenedor cliente sale y se elimina al terminar; el servidor sigue activo.

Para detenerlo:

```powershell
docker compose stop
```

## Pruebas

| Prueba | Operación y comprobación |
|---|---|
| P01 | Publicar tres mensajes, obtenerlos, comprobar contenido y orden, confirmar y verificar cola vacía. |
| P02 | Rechazar con requeue=True, obtener nuevamente con redelivered=True y confirmar. |
| P03 | Consultar pasivamente una cola previamente eliminada, verificar código 404 y conexión todavía abierta. |

Las pruebas usan colas exclusivas con nombres generados por el servidor. Estas colas se eliminan al finalizar su conexión; no se borran colas ajenas.

## Evidencias y análisis

`evidencias/todas.pcap` contiene la captura original del 6 de noviembre de 2026, con 121 paquetes, analizada en el informe. Los JSON y PCAP individuales guardados en este paquete corresponden a la repetición del 8 de noviembre. Las capturas gráficas están en `evidencias/capturas`.

El video puede mostrar otra ejecución posterior de las mismas pruebas; la parte de Wireshark analiza el archivo original. Los números de trama del informe corresponden únicamente a `todas.pcap`.

Filtros para esa captura en Wireshark:

```text
amqp
frame.number >= 20 && frame.number <= 45 && amqp
frame.number == 81 || frame.number == 84
frame.number == 115
```

La trama 81 muestra Basic.Nack con Requeue verdadero; la 84, la reentrega; la 115, Channel.Close con código 404. Los resultados esperados y observados se desarrollan en el PDF.

## Fuentes técnicas

- [Tutorial Python/Pika](https://www.rabbitmq.com/tutorials/tutorial-one-python).
- [Modelo AMQP 0-9-1](https://www.rabbitmq.com/tutorials/amqp-concepts).
- [Confirmaciones y reentregas](https://www.rabbitmq.com/docs/confirms).
- [Canales](https://www.rabbitmq.com/docs/channels).

