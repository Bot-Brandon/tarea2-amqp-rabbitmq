#!/bin/sh
set -eu
case "${1:-todas}" in todas|P01|P02|P03) prueba="${1:-todas}";; *) echo 'Use todas, P01, P02 o P03'; exit 2;; esac
tcpdump -i eth0 -p -Z root -U -s 0 -w "/evidencias/${prueba}.pcap" 'tcp port 5672' >"/evidencias/${prueba}-captura.log" 2>&1 &
captura=$!
finalizar() { kill -INT "$captura" 2>/dev/null || true; wait "$captura" || true; }
trap finalizar EXIT
sleep 1
kill -0 "$captura"
python -u /app/laboratorio.py "$prueba"
sleep 1
