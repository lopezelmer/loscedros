app_name = "los_cedros"
app_title = "Los Cedros"
app_publisher = "Condominio Los Cedros"
app_description = "Sitio web y Portal de Residentes del Condominio Los Cedros"
app_email = "admin@loscedros.example"
app_license = "mit"

required_apps = ["helpdesk"]

# La raiz del sitio ("/") muestra la pagina www/inicio.html
home_page = "inicio"

before_install = "los_cedros.install.before_install"
after_install = "los_cedros.install.after_install"
after_migrate = "los_cedros.install.after_migrate"
