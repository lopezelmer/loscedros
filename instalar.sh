#!/usr/bin/env bash
# Instala la app los_cedros en un bench de Frappe.
# Uso (desde la carpeta del bench, donde estan apps/ y sites/):
#   ./apps/los_cedros/instalar.sh <nombre-del-site>
set -euo pipefail
SITE="${1:-}"
if [ -z "$SITE" ]; then
  echo "Uso: ./apps/los_cedros/instalar.sh <nombre-del-site>"
  echo "Sites disponibles:"; ls -1 sites | grep -vE '^(assets|apps\.(txt|json)|common_site_config\.json|currentsite\.txt)$' || true
  exit 1
fi
[ -d apps/frappe ] || { echo "ERROR: ejecuta esto desde la carpeta del bench (donde estan apps/ y sites/)."; exit 1; }
[ -d "sites/$SITE" ] || { echo "ERROR: no existe el site '$SITE' en sites/."; exit 1; }

echo "1/5  Instalando el paquete de Python..."
./env/bin/pip install -q -e apps/los_cedros

echo "2/5  Registrando la app en sites/apps.txt..."
if ! grep -qx "los_cedros" sites/apps.txt; then
  [ -n "$(tail -c1 sites/apps.txt)" ] && echo >> sites/apps.txt
  echo "los_cedros" >> sites/apps.txt
fi

echo "3/5  Instalando en el site $SITE (crea tablas, rol y contenido de ejemplo)..."
# Frappe guarda en cache la lista de modulos por app; sin limpiarla no crea los DocTypes nuevos.
bench --site "$SITE" clear-cache
bench --site "$SITE" install-app los_cedros --force
N=$(bench --site "$SITE" console <<< 'print("LC_DT", len(frappe.get_all("DocType", filters={"module": "Los Cedros"})))' 2>/dev/null | grep -o 'LC_DT [0-9]*' | awk '{print $2}')
if [ "${N:-0}" -lt 9 ]; then
  echo "ERROR: se esperaban 9 DocTypes de Los Cedros y hay ${N:-0}. Copia el error de arriba."; exit 1
fi
echo "     ${N} DocTypes creados."

echo "4/5  Publicando estilos, script e imagenes..."
bench build --app los_cedros

echo "5/5  Limpiando cache..."
bench --site "$SITE" clear-cache
bench --site "$SITE" clear-website-cache

echo
echo "Listo. Reinicia el servidor (bench start o sudo supervisorctl restart all) y abre:"
echo "  http://<ip-del-servidor>:8000/          -> sitio de la comunidad"
echo "  http://<ip-del-servidor>:8000/app/aviso-comunidad  -> editar avisos"
