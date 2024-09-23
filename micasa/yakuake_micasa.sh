#!/bin/bash
# Resto de tu script

sleep 60
# Abrir Yakuake
yakuake &

# Esperar un momento para que Yakuake se abra completamente
sleep 3

# Definir las rutas
ruta1="$HOME/robocomp/components/dsr-graph/components/idserver"
ruta2="$HOME/robocomp/components/micasa_agent"
ruta3="$HOME/robocomp/components/micasa/escucharDSR_agente"

# Función para abrir una nueva pestaña en Yakuake y ejecutar un comando en ella
function abrir_nueva_pestania() {
    xdotool key ctrl+shift+t
    sleep 0.5
    xdotool type "$1"
    xdotool key Return
}

# Abrir las cuatro shells en distintas rutas
abrir_nueva_pestania "bash /home/robolab-micasa/robocomp/tools/rcnode/rcnode.sh &"
sleep 2
abrir_nueva_pestania "cd $ruta1 && bin/idserver etc/config_pioneer"
abrir_nueva_pestania "cd $ruta2 && src/micasa_agent.py etc/config"
abrir_nueva_pestania "cd $ruta3 && src/escucharDSR_agente.py etc/config"

