import flet as ft
from supabase import create_client, Client
import requests 

#conexion bd
SUPABASE_URL = "https://cvqwxjsxstwkewoqqpfd.supabase.co"
SUPABASE_KEY = "sb_publishable_xMbOiHxGZIu0kO2AN0ESPA_WmdO7NrP" # ¡Pega tu llave real aquí!

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Inventario"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    page.window.width = 500
    page.window.height = 800

    productos_en_nube = []
    
    tasa_bcv = 0.0
    tasa_euro = 0.0

#texto divisas
    txt_tasa_bcv = ft.Text("Dólar BCV: Cargando...", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_800, size=14)
    txt_tasa_euro = ft.Text("Euro BCV: Cargando...", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800, size=14)

    txt_stock = ft.TextField(label="Stock", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    txt_precio = ft.TextField(label="Precio ($)", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    
    dropdown_categoria = ft.Dropdown(
        label="Categoría",
        width=200, 
        options=[
            ft.dropdown.Option("Limpieza"),
            ft.dropdown.Option("Consumo/Alimentos"),
        ],
    )

    lista_productos = ft.ListView(expand=True, spacing=10)
    producto_seleccionado = {"referencia": None} 

#api del dolar
    def obtener_divisas():
        nonlocal tasa_bcv, tasa_euro
        try:
            # Consultamos la API oficial para Venezuela (Dólar y Euro)
            res_bcv = requests.get("https://ve.dolarapi.com/v1/dolares/oficial").json()
            res_euro = requests.get("https://ve.dolarapi.com/v1/euros/oficial").json()
            
            tasa_bcv = res_bcv["promedio"]
            tasa_euro = res_euro["promedio"]
            
            # Actualizamos los textos en la pantalla
            txt_tasa_bcv.value = f"Dólar BCV: Bs. {tasa_bcv:.2f}"
            txt_tasa_euro.value = f"Euro BCV: Bs. {tasa_euro:.2f}"
            page.update()
            
            # Refrescamos la lista para que calcule los precios
            cargar_productos()
        except Exception as e:
            txt_tasa_bcv.value = "Dólar BCV: Error API"
            txt_tasa_euro.value = "Euro BCV: Error API"
            page.update()

    # #Gemini (LÓGICA DE AUTOCOMPLETADO BLINDADO)
    txt_nombre = ft.TextField(label="Producto (Ej: Cloro, Arroz)")
    
    sugerencias_ui = ft.Column(spacing=0)
    contenedor_sugerencias = ft.Container(
        content=sugerencias_ui,
        visible=False,
        bgcolor=ft.colors.BLUE_GREY_50,
        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
        border_radius=5,
        padding=5,
    )

    def al_seleccionar_sugerencia(e):
        p = e.control.data
        txt_nombre.value = p["nombre"]
        dropdown_categoria.value = p["categoria"]
        txt_precio.value = str(p["precio"])
        contenedor_sugerencias.visible = False
        page.update()

    def al_cambiar_nombre(e):
        texto_buscado = txt_nombre.value.lower()
        sugerencias_ui.controls.clear()
        
        if texto_buscado:
            for p in productos_en_nube:
                if texto_buscado in p["nombre"].lower():
                    sugerencias_ui.controls.append(
                        ft.ListTile(
                            title=ft.Text(p["nombre"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"Categoría: {p['categoria']} | Precio: ${p['precio']:.2f}"),
                            leading=ft.Icon(ft.icons.SEARCH),
                            on_click=al_seleccionar_sugerencia,
                            data=p 
                        )
                    )
            contenedor_sugerencias.visible = len(sugerencias_ui.controls) > 0
        else:
            contenedor_sugerencias.visible = False
        page.update()

    txt_nombre.on_change = al_cambiar_nombre

    campo_producto_ui = ft.Column(
        controls=[txt_nombre, contenedor_sugerencias],
        spacing=2
    )

#BD
    def cargar_productos():
        nonlocal productos_en_nube
        lista_productos.controls.clear()
        
        try:
            respuesta = supabase.table("productos").select("*").order("id").execute()
            productos_en_nube = respuesta.data
        except Exception as e:
            print("Error conectando a Supabase:", e)
            productos_en_nube = []

        for prod in productos_en_nube:
            color_icono = ft.colors.BLUE_400 if prod["categoria"] == "Limpieza" else ft.colors.ORANGE_400
            icono = ft.icons.CLEANING_SERVICES if prod["categoria"] == "Limpieza" else ft.icons.RESTAURANT

            # Hacemos la multiplicación automática si la tasa ya cargó (usando Dólar BCV como base del inventario)
            precio_usd = prod['precio']
            texto_precio = f"${precio_usd:.2f}"
            if tasa_bcv > 0:
                precio_bs = precio_usd * tasa_bcv
                texto_precio += f" (Bs. {precio_bs:.2f})"

            lista_productos.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Row(
                            controls=[
                                ft.Icon(icono, color=color_icono, size=30),
                                ft.Column(
                                    controls=[
                                        ft.Text(prod["nombre"], weight=ft.FontWeight.BOLD, size=16),
                                        ft.Text(f"Categoría: {prod['categoria']} | Precio: {texto_precio}", size=12, color=ft.colors.GREY_600),
                                    ],
                                    expand=True
                                ),
                                ft.Container(
                                    content=ft.Text(str(prod["stock"]), weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    bgcolor=ft.colors.GREEN_500 if prod["stock"] > 10 else ft.colors.RED_500,
                                    padding=8,
                                    border_radius=5,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(icon=ft.icons.POINT_OF_SALE, icon_color=ft.colors.GREEN_600, tooltip="Vender", data=prod, on_click=abrir_venta),
                                        ft.IconButton(icon=ft.icons.ATTACH_MONEY, icon_color=ft.colors.BLUE_600, tooltip="Editar Precio", data=prod, on_click=abrir_edicion_precio),
                                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED_500, tooltip="Eliminar", data=prod, on_click=eliminar_producto),
                                    ],
                                    spacing=0
                                )
                            ]
                        )
                    )
                )
            )
        page.update()

    def agregar_producto(e):
        if not txt_nombre.value or not txt_stock.value or not dropdown_categoria.value:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, llena al menos Nombre, Stock y Categoría"), open=True)
            page.update()
            return

        try:
            nombre_input = txt_nombre.value.strip()
            stock_int = int(txt_stock.value)
            precio_input = txt_precio.value.strip()
            
            busqueda = supabase.table("productos").select("*").ilike("nombre", nombre_input).execute()
            
            if len(busqueda.data) > 0:
                prod_existente = busqueda.data[0]
                nuevo_stock = prod_existente["stock"] + stock_int
                supabase.table("productos").update({"stock": nuevo_stock}).eq("id", prod_existente["id"]).execute()
                mensaje_exito = f"¡Stock sumado a {nombre_input}!"
            else:
                if not precio_input:
                    page.snack_bar = ft.SnackBar(ft.Text("Para un producto nuevo, el precio es obligatorio"), open=True)
                    page.update()
                    return
                
                precio_float = float(precio_input)
                supabase.table("productos").insert({
                    "nombre": nombre_input, 
                    "categoria": dropdown_categoria.value,
                    "stock": stock_int,
                    "precio": precio_float
                }).execute()
                mensaje_exito = "¡Producto nuevo guardado en la nube!"

            txt_nombre.value = ""
            txt_stock.value = ""
            txt_precio.value = ""
            dropdown_categoria.value = None
            contenedor_sugerencias.visible = False
            
            cargar_productos()
            page.snack_bar = ft.SnackBar(ft.Text(mensaje_exito), open=True)
            
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Error: El stock y el precio deben ser números válidos."), open=True)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"), open=True)
            
        page.update()

#dialogos
    txt_nuevo_precio = ft.TextField(label="Nuevo Precio ($)", keyboard_type=ft.KeyboardType.NUMBER)

    def guardar_nuevo_precio(e):
        try:
            nuevo_precio_float = float(txt_nuevo_precio.value)
            prod = producto_seleccionado["referencia"]
            supabase.table("productos").update({"precio": nuevo_precio_float}).eq("id", prod["id"]).execute()
            dialogo_editar_precio.open = False
            cargar_productos() 
            page.snack_bar = ft.SnackBar(ft.Text("¡Precio actualizado en la nube!"), open=True)
            page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Error: Ingresa un número válido."), open=True)
            page.update()

    dialogo_editar_precio = ft.AlertDialog(
        modal=True,
        title=ft.Text("Modificar Precio"),
        content=txt_nuevo_precio,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialogo_editar_precio)),
            ft.TextButton("Guardar", on_click=guardar_nuevo_precio),
        ],
    )
    page.overlay.append(dialogo_editar_precio)

    def abrir_edicion_precio(e):
        prod = e.control.data
        producto_seleccionado["referencia"] = prod
        dialogo_editar_precio.title = ft.Text(f"Modificar precio de:\n{prod['nombre']}")
        txt_nuevo_precio.value = str(prod["precio"])
        dialogo_editar_precio.open = True
        page.update()

    txt_cantidad_vender = ft.TextField(label="Cantidad a vender", keyboard_type=ft.KeyboardType.NUMBER)

    def confirmar_venta(e):
        try:
            cantidad = int(txt_cantidad_vender.value)
            prod = producto_seleccionado["referencia"]
            
            if cantidad <= 0:
                page.snack_bar = ft.SnackBar(ft.Text("Ingresa una cantidad mayor a 0."), open=True)
            elif cantidad > prod["stock"]:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ No hay suficiente stock."), open=True)
            else:
                nuevo_stock = prod["stock"] - cantidad
                supabase.table("productos").update({"stock": nuevo_stock}).eq("id", prod["id"]).execute()
                dialogo_vender.open = False
                cargar_productos()
                page.snack_bar = ft.SnackBar(ft.Text(f"¡Venta registrada! Stock restante: {nuevo_stock}"), open=True)
            page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Error: Ingresa un número entero."), open=True)
            page.update()

    dialogo_vender = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registrar Venta"),
        content=txt_cantidad_vender,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialogo_vender)),
            ft.TextButton("Vender", on_click=confirmar_venta, style=ft.ButtonStyle(color=ft.colors.GREEN)),
        ],
    )
    page.overlay.append(dialogo_vender)

    def abrir_venta(e):
        prod = e.control.data
        producto_seleccionado["referencia"] = prod
        dialogo_vender.title = ft.Text(f"Vender: {prod['nombre']}\n(Stock actual: {prod['stock']})")
        txt_cantidad_vender.value = ""
        dialogo_vender.open = True
        page.update()

    def eliminar_producto(e):
        prod = e.control.data
        supabase.table("productos").delete().eq("id", prod["id"]).execute()
        cargar_productos()
        page.snack_bar = ft.SnackBar(ft.Text(f"Producto eliminado de la base de datos."), open=True)
        page.update()

    def cerrar_dialogo(dialogo):
        dialogo.open = False
        page.update()

  #interfaz
    contenedor_principal = ft.Column(
        expand=True,
        controls=[
            ft.Row(
                controls=[
                    ft.Text("PRODUCTOS A GUARDAR", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                    ft.Icon(ft.icons.CLOUD_DONE, color=ft.colors.BLUE_900)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            # PANEL DE TASAS DE DÓLAR Y EURO
            ft.Container(
                content=ft.Row(
                    controls=[txt_tasa_bcv, txt_tasa_euro],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                ),
                padding=10,
                bgcolor=ft.colors.YELLOW_50,
                border_radius=5,
                border=ft.border.all(1, ft.colors.YELLOW_200)
            ),
            ft.Divider(height=10),
            campo_producto_ui,
            ft.Row(
                controls=[dropdown_categoria, txt_stock, txt_precio],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    text="Procesar Mercancía",
                    icon=ft.icons.CLOUD_UPLOAD,
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE),
                    on_click=agregar_producto
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=10, bottom=10)
            ),
            ft.Divider(height=10),
            ft.Text("Stock Actual (Sincronizado)", size=16, weight=ft.FontWeight.BOLD),
            lista_productos
        ]
    )

    page.add(contenedor_principal)
    
    # Mandamos a cargar los datos de Supabase primero
    cargar_productos()
    # Y luego mandamos a buscar las divisas en tiempo real
    obtener_divisas()

ft.app(target=main)