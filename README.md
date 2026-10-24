# Los Cedros: sitio de la comunidad (app de Frappe)

Sitio web del Condominio Los Cedros servido por el mismo Frappe del Portal de Residentes (Helpdesk).
El contenido se edita desde el Desk de Frappe; no hace falta tocar HTML.

## Instalar

```bash
cd ~/frappe-bench                      # tu carpeta del bench
cp -r /ruta/a/los_cedros apps/         # copia esta carpeta dentro de apps/
./apps/los_cedros/instalar.sh <site>   # <site> = nombre de la carpeta dentro de sites/
```

Reinicia el servidor y abre `http://<servidor>:8000/`.

## Portal de Residentes (v1.1)

- `/reportar`: el residente escoge una categoría, llena el formulario y adjunta hasta 3 fotos. Se crea un caso en Helpdesk (HD Ticket) con el tipo y la prioridad de la categoría.
- `/mis-reportes`: el residente ve sus casos, las respuestas de la Administración y contesta. Solo ve los suyos (verificado en el servidor).
- La Administración trabaja en `/helpdesk` como siempre.
- Categorías: `/app/categoria-reporte` (nombre, prioridad, equipo, sugerencias y campos extra del formulario). Cada categoría se crea también como Tipo de ticket en Helpdesk.
- Residentes: `/app/residente` (edificio, apartamento, teléfono). Marca **Verificado** para fijar su unidad.

## Página de inicio de sesión (v1.2)

- `/login` usa el diseño de Los Cedros (`los_cedros/www/login.html` extiende la plantilla de Frappe, así que siguen funcionando la recuperación de contraseña y la verificación en dos pasos).
- «Login with Email Link» está eliminado: el parche `v1_2.disable_email_link_login` apaga la opción en System Settings y `/login#login-with-email-link` vuelve a `#login`.

## Cuenta: contraseña y cierre de sesión (v1.3)

- `/update-password` (cambiar contraseña, o crearla desde el enlace de «¿Olvidaste tu contraseña?») y las páginas de mensaje de Frappe (por ejemplo «Sesión cerrada» en `/?cmd=web_logout`) usan el mismo diseño que `/login`.
- El menú del Portal de Residentes tiene «Cambiar contraseña».
- La lógica sigue siendo la de Frappe; solo cambian el diseño y los textos.

## Qué se edita y dónde

| Contenido | Dónde en el Desk |
|---|---|
| Avisos del boletín | `/app/aviso-comunidad` |
| Fechas del calendario | `/app/evento-comunidad` |
| Junta y Administración | `/app/miembro-junta` |
| Preguntas frecuentes | `/app/pregunta-frecuente` |
| Teléfono, correo, horario, días de cuota, mensaje de la Junta, aviso de portada, enlace del Portal, foto | `/app/configuracion-sitio` |

- Un aviso aparece si **Publicado** está marcado y, si tiene **Mostrar hasta**, mientras no pase esa fecha.
- El calendario muestra las fechas desde hace 14 días en adelante.
- El rol **Editor Sitio** permite editar solo este contenido. Asígnalo a la persona de la Administración (usuario tipo *System User*).

## Archivos

- `los_cedros/www/inicio.html`, `inicio.py`: la página (plantilla Jinja y datos).
- `los_cedros/public/`: estilos, script, logo y foto de portada.
- `los_cedros/los_cedros/doctype/`: tablas de contenido.
- `los_cedros/install.py`: crea el rol y el contenido de ejemplo al instalar.
