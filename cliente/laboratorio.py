"""Pruebas reales AMQP 0-9-1: resultados y captura se guardan en /evidencias."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import pika


def conectar():
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=os.environ.get('AMQP_HOST', 'rabbitmq'),
        credentials=pika.PlainCredentials(os.environ['AMQP_USER'], os.environ['AMQP_PASSWORD']),
        heartbeat=30, socket_timeout=10, blocked_connection_timeout=15))


def p01():
    with conectar() as conn:
        ch = conn.channel()
        q = ch.queue_declare(queue='', exclusive=True).method.queue
        ch.confirm_delivery()
        mensajes = ['Hola desde Brandon y Nicolas', 'Segundo mensaje AMQP', 'Tercer mensaje AMQP']
        for texto in mensajes:
            ch.basic_publish(exchange='', routing_key=q, body=texto.encode(), mandatory=True)
        recibidos = []
        for _ in mensajes:
            method, _, body = ch.basic_get(queue=q, auto_ack=False)
            if method is None:
                raise AssertionError('Falta un mensaje publicado')
            recibidos.append(body.decode())
            ch.basic_ack(method.delivery_tag)
        assert recibidos == mensajes, (recibidos, mensajes)
        assert ch.queue_declare(queue=q, passive=True).method.message_count == 0
        return {'publicados': mensajes, 'recibidos': recibidos, 'cola_final': 0,
                'operaciones': 'Queue.Declare, Confirm.Select, Basic.Publish, Basic.Get, Basic.Ack'}


def p02():
    with conectar() as conn:
        ch = conn.channel()
        q = ch.queue_declare(queue='', exclusive=True).method.queue
        ch.confirm_delivery()
        ch.basic_publish(exchange='', routing_key=q, body=b'Mensaje para reentrega', mandatory=True)
        method, _, body = ch.basic_get(queue=q, auto_ack=False)
        assert method is not None
        primera = method.redelivered
        ch.basic_nack(method.delivery_tag, requeue=True)
        method2, _, body2 = ch.basic_get(queue=q, auto_ack=False)
        assert method2 is not None and method2.redelivered and body2 == body
        ch.basic_ack(method2.delivery_tag)
        assert ch.queue_declare(queue=q, passive=True).method.message_count == 0
        return {'mensaje': body2.decode(), 'primera_redelivered': primera,
                'segunda_redelivered': method2.redelivered, 'cola_final': 0,
                'operaciones': 'Basic.Nack(requeue=True), Basic.GetOk(redelivered=True), Basic.Ack'}


def p03():
    with conectar() as conn:
        ch = conn.channel()
        # Nombre aleatorio exclusivo: se elimina antes de comprobar que ya no existe.
        q = ch.queue_declare(queue='', exclusive=True).method.queue
        ch.queue_delete(queue=q)
        try:
            ch.queue_declare(queue=q, passive=True)
        except pika.exceptions.ChannelClosedByBroker as exc:
            assert exc.reply_code == 404, exc.reply_code
            assert conn.is_open, 'El error de canal cerro la conexion'
            return {'codigo': exc.reply_code, 'respuesta': exc.reply_text,
                    'conexion_sigue_abierta': conn.is_open,
                    'operaciones': 'Queue.Declare(passive=True), Channel.Close(404), Channel.CloseOk'}
        raise AssertionError('Se esperaba error 404 por cola inexistente')


if __name__ == '__main__':
    pruebas = {'P01': p01, 'P02': p02, 'P03': p03}
    seleccion = sys.argv[1] if len(sys.argv) > 1 else 'todas'
    nombres = list(pruebas) if seleccion == 'todas' else [seleccion]
    resultados = []
    for nombre in nombres:
        resultado = {'prueba': nombre, 'fecha_utc': datetime.now(timezone.utc).isoformat(),
                     'pika': pika.__version__, 'resultado': 'OK', 'detalle': pruebas[nombre]()}
        resultados.append(resultado)
        print(json.dumps(resultado, ensure_ascii=False), flush=True)
    Path(f'/evidencias/{seleccion}-resultados.json').write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding='utf-8')
