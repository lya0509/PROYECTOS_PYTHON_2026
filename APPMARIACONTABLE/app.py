import flet as ft
import os
import shutil
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE LA RUTA LOCAL PORTABLE
# ==========================================
CONFIG_LOCAL = "config_ruta_local.txt"

if os.path.exists(CONFIG_LOCAL):
    with open(CONFIG_LOCAL, "r") as f:
        BASE_DIR = f.read().strip()
else:
    BASE_DIR = "Contabilidad_Maria" 
    with open(CONFIG_LOCAL, "w") as f:
        f.write(BASE_DIR)

EMPRESAS_DIR = os.path.join(BASE_DIR, "Empresas")
PASS_FILE = os.path.join(BASE_DIR, "contrasenas.xlsx")

# Inicialización del sistema base
os.makedirs(EMPRESAS_DIR, exist_ok=True)
if not os.path.exists(PASS_FILE):
    pd.DataFrame(columns=["Sitio/Servicio", "Usuario", "Contraseña", "Notas"]).to_excel(PASS_FILE, index=False)

# Configuración de Nube Local (Servidor) - ¡CORREGIDO POR DEFECTO!
CONFIG_SERVER = "config_servidor.txt"
if os.path.exists(CONFIG_SERVER):
    with open(CONFIG_SERVER, "r") as f:
        RUTA_SERVIDOR = f.read().strip()
else:
    RUTA_SERVIDOR = r"\\DESKTOP-6N7LCT7\Respaldos_Maria"
    with open(CONFIG_SERVER, "w") as f:
        f.write(RUTA_SERVIDOR)

# Traductor de meses para la interfaz visual
MESES_ESP = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}

def main(page: ft.Page):
    page.title = "Sistema de Gestión Contable - María"
    page.window_width = 1000
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1e1e24"
    page.padding = 20
    
    # Estado de la sesión
    state = {"empresa_actual": ""}

    def mostrar_snack(texto, color_bg):
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color_bg)
        page.snack_bar.open = True
        page.update()

    # ==========================================
    # VISTA 1: MENÚ PRINCIPAL
    # ==========================================
    def mostrar_bienvenida():
        page.clean()
        
        banner = ft.Container(
            content=ft.Column([
                ft.Text("¡Hola, bienvenida María! 👋", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text("Panel Central de Operaciones", size=18, color=ft.colors.BLUE_GREY_200),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30, bgcolor="#2a2a35", border_radius=15, alignment=ft.alignment.center
        )

        def ejecutar_respaldo(e):
            try:
                if os.path.exists(RUTA_SERVIDOR):
                    # Formatear la estampa de tiempo
                    fecha_hora = datetime.now().strftime('%d-%m-%Y a las %I:%M %p')
                    destino = os.path.join(RUTA_SERVIDOR, f"Respaldo_{datetime.now().strftime('%Y%m%d_%H%M')}")
                    
                    # Copia física a través de la red LAN
                    shutil.copytree(BASE_DIR, destino)
                    
                    # --- VENTANA EMERGENTE DE ÉXITO AUTOMÁTICA ---
                    def cerrar_dialogo(sub_e):
                        dialogo.open = False
                        page.update()

                    dialogo = ft.AlertDialog(
                        modal=True,
                        title=ft.Row([
                            ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN_400, size=30),
                            ft.Text(" ¡Respaldo Exitoso!", weight=ft.FontWeight.BOLD)
                        ]),
                        content=ft.Text(
                            f"La contabilidad se envió correctamente a la PC Servidor.\n\n"
                            f"📅 Sincronizado: {fecha_hora}\n"
                            f"📂 Destino: {RUTA_SERVIDOR}",
                            size=15
                        ),
                        actions=[
                            ft.ElevatedButton("Entendido", on_click=cerrar_dialogo, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    
                    page.dialog = dialogo
                    dialogo.open = True
                    page.update()
                else:
                    mostrar_snack("Servidor de red no detectado. Copia de seguridad retenida localmente.", ft.colors.ORANGE_700)
            except Exception as ex:
                mostrar_snack(f"Error en red: {ex}", ft.colors.RED_700)

        btn_contrasenas = ft.Container(
            content=ft.Column([ft.Icon(ft.icons.LOCK, size=45, color=ft.colors.BLUE_400), ft.Text("🔑 Contraseñas", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220, height=140, bgcolor="#252530", border_radius=15, ink=True, on_click=lambda _: mostrar_contrasenas(), alignment=ft.alignment.center
        )

        btn_contabilidad = ft.Container(
            content=ft.Column([ft.Icon(ft.icons.ANALYTICS, size=45, color=ft.colors.GREEN_400), ft.Text("📊 Contabilidad", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220, height=140, bgcolor="#252530", border_radius=15, ink=True, on_click=lambda _: mostrar_empresas(), alignment=ft.alignment.center
        )

        btn_respaldo = ft.Container(
            content=ft.Column([ft.Icon(ft.icons.CLOUD_SYNC, size=45, color=ft.colors.PURPLE_400), ft.Text("☁️ Respaldar Red", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220, height=140, bgcolor="#252530", border_radius=15, ink=True, on_click=ejecutar_respaldo, alignment=ft.alignment.center
        )

        bloque_botones = ft.Row([btn_contrasenas, btn_contabilidad, btn_respaldo], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        page.add(
            ft.AppBar(title=ft.Text("Menú Principal"), bgcolor="#1a1a24", center_title=True),
            ft.Column([banner, ft.Container(height=20), bloque_botones], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # ==========================================
    # VISTA 2: GESTOR DE CREDENCIALES
    # ==========================================
    def mostrar_contrasenas():
        page.clean()
        input_sitio = ft.TextField(label="Sitio o Servicio", width=200)
        input_user = ft.TextField(label="Usuario / Correo", width=200)
        input_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=180)
        tabla_items = ft.DataTable(columns=[ft.DataColumn(ft.Text("Sitio")), ft.DataColumn(ft.Text("Usuario")), ft.DataColumn(ft.Text("Contraseña"))], rows=[])

        def cargar_tabla_passwords():
            tabla_items.rows.clear()
            df = pd.read_excel(PASS_FILE)
            for _, fila in df.iterrows():
                tabla_items.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(fila['Sitio/Servicio']))), ft.DataCell(ft.Text(str(fila['Usuario']))), ft.DataCell(ft.Text(str(fila['Contraseña'])))]))
            page.update()

        def guardar_nueva_password(e):
            if input_sitio.value and input_user.value and input_pass.value:
                df = pd.concat([pd.read_excel(PASS_FILE), pd.DataFrame([{"Sitio/Servicio": input_sitio.value, "Usuario": input_user.value, "Contraseña": input_pass.value, "Notes": "App"}])], ignore_index=True)
                df.to_excel(PASS_FILE, index=False)
                input_sitio.value = input_user.value = input_pass.value = ""
                cargar_tabla_passwords()
                mostrar_snack("Credencial guardada con éxito", ft.colors.GREEN_700)

        btn_guardar = ft.ElevatedButton("Guardar", icon=ft.icons.SAVE, on_click=guardar_nueva_password)
        page.add(
            ft.AppBar(title=ft.Text("Llavero de Contraseñas"), bgcolor="#1a1a24", leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: mostrar_bienvenida())),
            ft.Row([input_sitio, input_user, input_pass, btn_guardar], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            ft.Container(content=ft.Column([tabla_items], scroll=ft.ScrollMode.AUTO), height=400)
        )
        cargar_tabla_passwords()

    # ==========================================
    # VISTA 3: ADMINISTRACIÓN DE EMPRESAS
    # ==========================================
    def mostrar_empresas():
        page.clean()
        lista_empresas_ui = ft.ListView(expand=True, spacing=10, padding=10)
        input_nueva_empresa = ft.TextField(label="Nombre de la nueva empresa (Ej: Rapid Foto)", expand=True)

        def actualizar_lista_empresas():
            lista_empresas_ui.controls.clear()
            carpetas = [c for c in os.listdir(EMPRESAS_DIR) if os.path.isdir(os.path.join(EMPRESAS_DIR, c))]
            if not carpetas:
                lista_empresas_ui.controls.append(ft.Text("No hay empresas registradas aún.", color=ft.colors.GREY_400, italic=True))
            else:
                for emp in carpetas:
                    lista_empresas_ui.controls.append(
                        ft.Container(
                            content=ft.ListTile(
                                leading=ft.Icon(ft.icons.BUSINESS, color=ft.colors.GREEN_400),
                                title=ft.Text(emp, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text("Clic para ver carpetas mensuales"),
                                trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                                on_click=lambda e, name=emp: abrir_empresa(name)
                            ), bgcolor="#252530", border_radius=10, ink=True
                        )
                    )
            lista_empresas_ui.update()

        def crear_empresa_click(e):
            try:
                valor = input_nueva_empresa.value
                if not valor or str(valor).strip() == "":
                    mostrar_snack("¡Escribe el nombre de la empresa!", ft.colors.RED_700)
                    return
                nombre = str(valor).strip()
                ruta_nueva = os.path.join(EMPRESAS_DIR, nombre)
                if not os.path.exists(ruta_nueva):
                    os.makedirs(ruta_nueva)
                    input_nueva_empresa.value = ""
                    input_nueva_empresa.update()
                    actualizar_lista_empresas()
                    mostrar_snack(f"Empresa '{nombre}' registrada", ft.colors.GREEN_700)
                else:
                    mostrar_snack("Esa empresa ya está registrada", ft.colors.ORANGE_700)
            except Exception as ex:
                mostrar_snack(f"Error: {ex}", ft.colors.RED_900)

        row_agregar = ft.Row([
            input_nueva_empresa,
            ft.ElevatedButton("Agregar Empresa", icon=ft.icons.ADD, on_click=crear_empresa_click, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)
        ], spacing=15)

        page.add(
            ft.AppBar(title=ft.Text("Módulo Contable - Clientes"), bgcolor="#1a1a24", leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: mostrar_bienvenida())),
            lista_empresas_ui, ft.Divider(), row_agregar
        )
        actualizar_lista_empresas()

    # ==========================================
    # VISTA 4: ORGANIZACIÓN POR CARPETAS DE MESES
    # ==========================================
    def abrir_empresa(nombre_empresa):
        state["empresa_actual"] = nombre_empresa
        page.clean()
        ruta_empresa = os.path.join(EMPRESAS_DIR, nombre_empresa)
        lista_meses_ui = ft.ListView(expand=True, spacing=10)

        def actualizar_lista_meses():
            lista_meses_ui.controls.clear()
            if os.path.exists(ruta_empresa):
                subcarpetas = [d for d in os.listdir(ruta_empresa) if os.path.isdir(os.path.join(ruta_empresa, d)) and not d.startswith(('~', '.'))]
            else:
                subcarpetas = []
            
            if not subcarpetas:
                lista_meses_ui.controls.append(ft.Text("No hay carpetas mensuales en esta empresa. Genera una abajo.", color=ft.colors.GREY_400, italic=True))
            else:
                subcarpetas.sort(reverse=True)
                for folder_mes in subcarpetas:
                    partes = folder_mes.split("_")
                    nombre_visible = folder_mes
                    if len(partes) == 2:
                        año, mes_num = partes
                        nombre_visible = f"📁 Carpeta Mensual: {MESES_ESP.get(mes_num, mes_num)} del {año}"
                    
                    lista_meses_ui.controls.append(
                        ft.Container(
                            content=ft.ListTile(
                                leading=ft.Icon(ft.icons.FOLDER, color=ft.colors.ORANGE_400),
                                title=ft.Text(nombre_visible, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text("Contiene 'Contabilidad.xlsx' y documentos del mes"),
                                trailing=ft.IconButton(ft.icons.EDIT, on_click=lambda e, f_mes=folder_mes: trabajar_en_excel(f_mes))
                            ), bgcolor="#2a2a38", border_radius=10
                        )
                    )
            page.update()

        def crear_libro_mes_actual(e):
            nombre_carpeta_mes = datetime.now().strftime('%Y_%m')
            ruta_carpeta_mes = os.path.join(ruta_empresa, nombre_carpeta_mes)
            
            os.makedirs(ruta_carpeta_mes, exist_ok=True)
            ruta_excel = os.path.join(ruta_carpeta_mes, "Contabilidad.xlsx")
            
            if not os.path.exists(ruta_excel):
                with pd.ExcelWriter(ruta_excel, engine='openpyxl') as writer:
                    pd.DataFrame(columns=["Fecha", "Tipo", "Factura", "Cliente/Proveedor", "Monto ($)", "IVA ($)"]).to_excel(writer, sheet_name="Compra_Venta", index=False)
                    pd.DataFrame(columns=["Fecha", "Categoría", "Descripción", "Monto ($)"]).to_excel(writer, sheet_name="Gastos", index=False)
                    pd.DataFrame(columns=["Fecha", "Cuenta", "Descripción", "Debe ($)", "Haber ($)"]).to_excel(writer, sheet_name="Asientos", index=False)
                    pd.DataFrame(columns=["Concepto", "Monto ($)"]).to_excel(writer, sheet_name="Ganancias_Perdidas", index=False)
                
                actualizar_lista_meses()
                mostrar_snack(f"¡Carpeta mensual [{nombre_carpeta_mes}] inicializada correctamente!", ft.colors.GREEN_700)
            else:
                mostrar_snack("La carpeta y el libro de este mes ya existen.", ft.colors.ORANGE_700)

        page.add(
            ft.AppBar(title=ft.Text(f"Empresa: {nombre_empresa}"), bgcolor="#1a1a24", leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: mostrar_empresas())),
            ft.Text("Carpetas Mensuales de Contabilidad:", size=16, weight=ft.FontWeight.BOLD),
            lista_meses_ui, ft.Divider(),
            ft.Row([ft.ElevatedButton("Inicializar Carpeta del Mes Actual", icon=ft.icons.CREATE_NEW_FOLDER, on_click=crear_libro_mes_actual, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER)
        )
        actualizar_lista_meses()

    # ==========================================
    # VISTA 5: INTERFAZ DE TABS NAVEGABLES
    # ==========================================
    def trabajar_en_excel(nombre_carpeta_mes):
        page.clean()
        emp_actual = state["empresa_actual"]
        ruta_completa_excel = os.path.join(EMPRESAS_DIR, emp_actual, nombre_carpeta_mes, "Contabilidad.xlsx")

        # TAB 1: COMPRA / VENTA
        cb_tipo = ft.Dropdown(label="Tipo de Operación", options=[ft.dropdown.Option("Compra"), ft.dropdown.Option("Venta")], width=160)
        txt_factura = ft.TextField(label="Factura N°", width=120)
        txt_entidad = ft.TextField(label="Cliente / Proveedor", width=200)
        txt_monto = ft.TextField(label="Monto ($)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        txt_iva = ft.TextField(label="IVA ($)", width=100, keyboard_type=ft.KeyboardType.NUMBER)
        dt_compra_venta = ft.DataTable(columns=[ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Tipo")), ft.DataColumn(ft.Text("Factura")), ft.DataColumn(ft.Text("Entidad")), ft.DataColumn(ft.Text("Monto")), ft.DataColumn(ft.Text("IVA"))], rows=[])

        # TAB 2: DISTRIBUCIÓN DE GASTOS
        txt_gasto_cat = ft.TextField(label="Categoría (Ej: Alquiler, Luz)", width=200)
        txt_gasto_desc = ft.TextField(label="Descripción", width=250)
        txt_gasto_monto = ft.TextField(label="Monto ($)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        dt_gastos = ft.DataTable(columns=[ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Categoría")), ft.DataColumn(ft.Text("Descripción")), ft.DataColumn(ft.Text("Monto"))], rows=[])

        # TAB 3: ASIENTOS CONTABLES
        txt_asiento_cuenta = ft.TextField(label="Cuenta Contable", width=180)
        txt_asiento_desc = ft.TextField(label="Descripción / Glosa", width=240)
        txt_asiento_debe = ft.TextField(label="Debe ($)", width=110, value="0", keyboard_type=ft.KeyboardType.NUMBER)
        txt_asiento_haber = ft.TextField(label="Haber ($)", width=110, value="0", keyboard_type=ft.KeyboardType.NUMBER)
        dt_asientos = ft.DataTable(columns=[ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Cuenta")), ft.DataColumn(ft.Text("Descripción")), ft.DataColumn(ft.Text("Debe")), ft.DataColumn(ft.Text("Haber"))], rows=[])

        # TAB 4: GANANCIAS Y PÉRDIDAS
        dt_balance = ft.DataTable(columns=[ft.DataColumn(ft.Text("Estructura de Rendimiento")), ft.DataColumn(ft.Text("Monto ($)"))], rows=[])

        def guardar_en_pestaña(nombre_pestana, diccionario_fila):
            excel_file = pd.ExcelFile(ruta_completa_excel)
            todas_las_hojas = {n: excel_file.parse(n) for n in excel_file.sheet_names}
            todas_las_hojas[nombre_pestana] = pd.concat([todas_las_hojas[nombre_pestana], pd.DataFrame([diccionario_fila])], ignore_index=True)
            
            with pd.ExcelWriter(ruta_completa_excel, engine='openpyxl') as writer:
                for n, df in todas_las_hojas.items():
                    df.to_excel(writer, sheet_name=n, index=False)

        def cargar_todo():
            excel_file = pd.ExcelFile(ruta_completa_excel)
            df_cv = excel_file.parse("Compra_Venta")
            df_g = excel_file.parse("Gastos")
            df_as = excel_file.parse("Asientos")

            dt_compra_venta.rows.clear()
            for _, r in df_cv.iterrows():
                dt_compra_venta.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(r.get('Fecha','')))),
                        ft.DataCell(ft.Text(str(r.get('Tipo','')))),
                        ft.DataCell(ft.Text(str(r.get('Factura','')))),
                        ft.DataCell(ft.Text(str(r.get('Cliente/Proveedor','')))),
                        ft.DataCell(ft.Text(f"$ {r.get('Monto ($)',0)}")),
                        ft.DataCell(ft.Text(f"$ {r.get('IVA ($)',0)}"))
                    ])
                )

            dt_gastos.rows.clear()
            for _, r in df_g.iterrows():
                dt_gastos.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(r.get('Fecha','')))),
                        ft.DataCell(ft.Text(str(r.get('Categoría','')))),
                        ft.DataCell(ft.Text(str(r.get('Descripción','')))),
                        ft.DataCell(ft.Text(f"$ {r.get('Monto ($)',0)}"))
                    ])
                )

            dt_asientos.rows.clear()
            for _, r in df_as.iterrows():
                dt_asientos.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(r.get('Fecha','')))),
                        ft.DataCell(ft.Text(str(r.get('Cuenta','')))),
                        ft.DataCell(ft.Text(str(r.get('Descripción','')))),
                        ft.DataCell(ft.Text(f"$ {r.get('Debe ($)',0)}")),
                        ft.DataCell(ft.Text(f"$ {r.get('Haber ($)',0)}"))
                    ])
                )

            ventas_totales = df_cv[df_cv['Tipo'] == 'Venta']['Monto ($)'].sum()
            compras_totales = df_cv[df_cv['Tipo'] == 'Compra']['Monto ($)'].sum()
            gastos_totales = df_g['Monto ($)'].sum()
            neto = ventas_totales - compras_totales - gastos_totales

            dt_balance.rows.clear()
            dt_balance.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("(+) Ventas Totales (Ingresos)")), ft.DataCell(ft.Text(f"$ {ventas_totales:.2f}", color="green"))]))
            dt_balance.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("(-) Compras Totales (Costos)")), ft.DataCell(ft.Text(f"$ {compras_totales:.2f}", color="red"))]))
            dt_balance.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("(-) Gastos Operacionales")), ft.DataCell(ft.Text(f"$ {gastos_totales:.2f}", color="red"))]))
            dt_balance.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("(=) EQUILIBRIO NETO DEL MES", weight="bold")), ft.DataCell(ft.Text(f"$ {neto:.2f}", color="green" if neto >= 0 else "red", weight="bold"))]))

            df_balance_guardar = pd.DataFrame([{"Concepto": "Ventas", "Monto ($)": ventas_totales}, {"Concepto": "Compras", "Monto ($)": compras_totales}, {"Concepto": "Gastos", "Monto ($)": gastos_totales}, {"Concepto": "Rendimiento Neto", "Monto ($)": neto}])
            
            with pd.ExcelWriter(ruta_completa_excel, engine='openpyxl') as writer:
                df_cv.to_excel(writer, sheet_name="Compra_Venta", index=False)
                df_g.to_excel(writer, sheet_name="Gastos", index=False)
                df_as.to_excel(writer, sheet_name="Asientos", index=False)
                df_balance_guardar.to_excel(writer, sheet_name="Ganancias_Perdidas", index=False)
            page.update()

        def click_registrar_cv(e):
            if cb_tipo.value and txt_factura.value and txt_entidad.value and txt_monto.value:
                try: m_val = float(txt_monto.value); i_val = float(txt_iva.value) if txt_iva.value else 0.0
                except: mostrar_snack("Valores numéricos inválidos", "red"); return
                guardar_en_pestaña("Compra_Venta", {"Fecha": datetime.now().strftime('%Y-%m-%d'), "Tipo": cb_tipo.value, "Factura": txt_factura.value, "Cliente/Proveedor": txt_entidad.value, "Monto ($)": m_val, "IVA ($)": i_val})
                cb_tipo.value = txt_factura.value = txt_entidad.value = txt_monto.value = txt_iva.value = ""
                cargar_todo(); mostrar_snack("Registro en Libro Compra/Venta guardado", "green")

        def click_registrar_gasto(e):
            if txt_gasto_cat.value and txt_gasto_desc.value and txt_gasto_monto.value:
                try: m_val = float(txt_gasto_monto.value)
                except: mostrar_snack("Monto inválido", "red"); return
                guardar_en_pestaña("Gastos", {"Fecha": datetime.now().strftime('%Y-%m-%d'), "Categoría": txt_gasto_cat.value, "Descripción": txt_gasto_desc.value, "Monto ($)": m_val})
                txt_gasto_cat.value = txt_gasto_desc.value = txt_gasto_monto.value = ""
                cargar_todo(); mostrar_snack("Distribución de gasto asentada", "green")

        def click_registrar_asiento(e):
            if txt_asiento_cuenta.value and txt_asiento_desc.value:
                try: d_val = float(txt_asiento_debe.value); h_val = float(txt_asiento_haber.value)
                except: mostrar_snack("Montos del asiento erróneos", "red"); return
                guardar_en_pestaña("Asientos", {"Fecha": datetime.now().strftime('%Y-%m-%d'), "Cuenta": txt_asiento_cuenta.value, "Descripción": txt_asiento_desc.value, "Debe ($)": d_val, "Haber ($)": h_val})
                txt_asiento_cuenta.value = txt_asiento_desc.value = ""
                txt_asiento_debe.value = txt_asiento_haber.value = "0"
                cargar_todo(); mostrar_snack("Asiento contable fijado en libro diario", "green")

        tab_compra_venta = ft.Tab(text="🛒 Libro Compra / Venta", content=ft.Column([ft.Row([cb_tipo, txt_factura, txt_entidad, txt_monto, txt_iva, ft.ElevatedButton("Registrar", icon=ft.icons.ADD, on_click=click_registrar_cv, bgcolor=ft.colors.GREEN_700)], wrap=True, spacing=10), ft.Divider(), ft.Container(content=ft.Column([dt_compra_venta], scroll=ft.ScrollMode.AUTO), height=350, expand=True)], scroll=ft.ScrollMode.AUTO))
        tab_gastos = ft.Tab(text="💸 Distribución de Gastos", content=ft.Column([ft.Row([txt_gasto_cat, txt_gasto_desc, txt_gasto_monto, ft.ElevatedButton("Asignar Gasto", icon=ft.icons.ADD, on_click=click_registrar_gasto, bgcolor=ft.colors.GREEN_700)], wrap=True, spacing=10), ft.Divider(), ft.Container(content=ft.Column([dt_gastos], scroll=ft.ScrollMode.AUTO), height=350, expand=True)], scroll=ft.ScrollMode.AUTO))
        tab_asientos = ft.Tab(text="📓 Asientos Contables", content=ft.Column([ft.Row([txt_asiento_cuenta, txt_asiento_desc, txt_asiento_debe, txt_asiento_haber, ft.ElevatedButton("Fijar Asiento", icon=ft.icons.ADD, on_click=click_registrar_asiento, bgcolor=ft.colors.GREEN_700)], wrap=True, spacing=10), ft.Divider(), ft.Container(content=ft.Column([dt_asientos], scroll=ft.ScrollMode.AUTO), height=350, expand=True)], scroll=ft.ScrollMode.AUTO))
        tab_ganancias = ft.Tab(text="📊 Ganancias y Pérdidas", content=ft.Column([ft.Text("Balance de Resultados Integrados Automatizados", size=16, weight=ft.FontWeight.BOLD), ft.Container(content=dt_balance, padding=15, bgcolor="#252530", border_radius=10, margin=ft.margin.only(top=10))], scroll=ft.ScrollMode.AUTO))

        navegacion_tabs = ft.Tabs(selected_index=0, tabs=[tab_compra_venta, tab_gastos, tab_asientos, tab_ganancias], expand=1)

        page.add(
            ft.AppBar(title=ft.Text(f"Carpeta: {nombre_carpeta_mes} | Cliente: {emp_actual}"), bgcolor="#1a1a24", leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: abrir_empresa(emp_actual))),
            navegacion_tabs
        )
        cargar_todo()

    mostrar_bienvenida()

if __name__ == "__main__":
    ft.app(target=main)