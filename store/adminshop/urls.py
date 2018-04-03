# @Author: Manuel Rodriguez <valle>
# @Date:   26-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: urls.py
# @Last modified by:   valle
# @Last modified time: 03-Feb-2018
# @License: Apache license vesion 2.0


from django.conf.urls  import url, handler404

from adminshop import views

DOCUMENTOS = [
    url(r'^lista_doc_policia/$', views.lista_doc_policia, name="lista_doc_policia"),
    url(r'^crear_informe_policia/$', views.crear_informe_policia, name="crear_informe_policia"),
    url(r'^ver_documento_policia/(?P<id>\d*)$', views.ver_documento_policia, name="ver_documento_policia"),
    url(r'^rm_doc_policia/(?P<id>\d*)$', views.rm_doc_policia, name="rm_doc_policia"),
    url(r'^send_doc_policia/(?P<id>\d*)$', views.send_doc_policia, name="send_doc_policia"),
]

BALANCES = [
    url(r'^get_ventas_chart/$', views.get_ventas_chart, name="get_ventas_chart"),
    url(r'^get_stock/$', views.get_stock, name="get_stock"),
]

GARANTIAS = [
    url(r'^lista_garantias/$', views.lista_garantias, name="lista_garantias"),
    url(r'^garantias/$', views.garantias, name="garantias_none"),
    url(r'^garantias/(?P<id_garantia>\d*)/$', views.garantias, name="garantias"),
    url(r'^rm_garantia/(?P<id_garantia>\d*)/$', views.rm_garantia, name="rm_garantia"),
    url(r'^get_documento_garantia/(?P<id_garantia>\d*)/$', views.get_documento_garantia, name="get_documento_garantia"),
]

PROVEEDOR = [
     url(r'^find_proveedor/$', views.find_proveedor, name="find_proveedor"),
     url(r'^proveedores/$', views.proveedores, name="proveedores"),
     url(r'^proveedores/(?P<id_proveedor>\d*)/$', views.proveedores, name="proveedores"),
     url(r'^rm_proveedores/(?P<id_proveedor>\d*)/$', views.rm_proveedores, name="rm_proveedores"),
     url(r'^lista_proveedores/$', views.lista_proveedores, name="lista_proveedores"),
     url(r'^salir_compra_proveedor/$', views.salir_compra_proveedor, name="salir_compra_proveedor"),
     url(r'^cp_productos_proveedor/$', views.cp_productos_proveedor, name="cp_productos_proveedor_none"),
     url(r'^cp_productos_proveedor/(?P<id_modelo>\d*)/$', views.cp_productos_proveedor, name="cp_productos_proveedor"),
     url(r'^cp_lista_modelos_proveedor/$', views.cp_lista_modelos_proveedor, name="cp_lista_modelos_proveedor"),
     url(r'^finalizar_compra_proveedor/$', views.finalizar_compra_proveedor, name="finalizar_compra_proveedor"),
]

ABONOS = [
    url(r'^abonos_find_cliente/$', views.abonos_find_cliente, name="abonos_find_cliente"),
    url(r'^salir_abonar/$', views.salir_abonar, name="salir_abonar"),
    url(r'^abonos/$', views.abonos, name="abonos"),
    url(r'^abonar/$', views.abonar, name="abonar"),
    url(r'^get_status_abonos/$', views.get_status_abonos, name="get_status_abonos"),
    url(r'^get_producto_abonar/$', views.get_producto_abonar, name="get_producto_abonar"),
    url(r'^get_productos_factura/$', views.get_productos_factura, name="get_productos_factura"),
    url(r'^listado_abonos/$', views.listado_abonos, name="listado_abonos"),
    url(r'^get_abono_by_id/(?P<id_abono>\d*)/$', views.get_abono_by_id, name="get_abono_by_id"),
    url(r'^find_abonos/$', views.find_abonos, name="find_abonos"),
    url(r'^send_abono/(?P<id_abono>\d*)/$', views.send_abono, name="send_abono"),
]

SIGN = [
    url(r'^rm_sign/(?P<id_sign>\d*)$', views.rm_sign, name="rm_sign"),
    url(r'^listado_sign/$', views.listado_sign, name="listado_sign"),
    url(r'^get_document_sign/$', views.get_document_sign, name="get_document_sign"),
    url(r'^get_sign/$', views.get_sign, name="get_sign"),
    url(r'^send_firma_press_insitu/(?P<id_producto>\d*)/(?P<estado>.*)/$', views.send_firma_press_insitu, name="send_firma_press_insitu"),
]

USER = [
    url(r'^login/$', views.login, name="login_tk"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^en_construccion/$', views.en_construccion, name="en_construccion"),
    url(r'^change_password/$', views.change_password, name="change_password"),
    url(r'^reset_password/$', views.reset_password, name="password_reset"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.confirm_reset_password, name='password_reset_confirm'),
]

MENU = [
    url(r'^$', views.tienda, name="tienda"),
    url(r'^taller/$', views.taller, name="taller"),
    url(r'^almacen/$', views.almacen, name="almacen"),
    url(r'^gestion/$', views.gestion, name="gestion"),
    url(r'^informes/$', views.informes, name="informes"),
]

TALLER = [
    url(r'^presupuesto_find_cliente/$', views.presupuesto_find_cliente,
        name="presupuesto_find_cliente"),
    url(r'^cancelar_presupuesto/(?P<pg>.*)/$', views.cancelar_presupuesto,
        name="cancelar_presupuesto"),
    url(r'^presupuesto/$', views.presupuesto, name="presupuesto"),
    url(r'^get_lineas_presupuesto/$', views.get_lineas_presupuesto, name="get_lineas_presupuesto"),
    url(r'^get_lineas_presupuesto/(?P<id_pres>\d*)/$', views.get_lineas_presupuesto, name="get_lineas_presupuesto"),
    url(r'^get_presupuesto_by_id/(?P<id_producto>\d*)/$', views.get_presupuesto_by_id, name="get_presupuesto_by_id"),
    url(r'^get_presupuesto_by_code/(?P<code>.*)/$', views.get_presupuesto_by_code, name="get_presupuesto_by_code"),
    url(r'^send_producto_rp/(?P<id_producto>\d*)/$', views.send_producto_rp, name="send_producto_rp"),
    url(r'^get_presupuesto_pdf/(?P<id_producto>\d*)/$', views.get_presupuesto_pdf, name="get_presupuesto_pdf"),
    url(r'^salir_presupuesto/$', views.salir_presupuesto, name="salir_presupuesto"),
    url(r'^save_presupuesto/$', views.save_presupuesto, name="save_presupuesto"),
    url(r'^save_actuacion/$', views.save_actuacion, name="save_actuacion"),
    url(r'^get_actuacion/$', views.get_actuacion, name="get_actuacion"),
    url(r'^find_actuacion/$', views.find_actuacion, name="find_actuacion"),
    url(r'^presupuestar/(?P<pg>.*)/$', views.presupuestar, name="presupuestar"),
    url(r'^actuaciones/$', views.actuaciones, name="actuaciones"),
    url(r'^actuaciones/(?P<id_actuacion>\d*)/$', views.actuaciones, name="actuaciones"),
    url(r'^rm_actuacion/(?P<id_actuacion>\d*)/$', views.rm_actuacion, name="rm_actuacion"),
    url(r'^reparacion/(?P<id_producto>\d*)/$', views.reparacion, name="reparacion"),
    url(r'^set_reparado/(?P<id_producto>\d*)/(?P<estado>.*)/$', views.set_reparado, name="set_reparado"),
    url(r'^set_entregado/(?P<id_producto>\d*)/$', views.set_entregado, name="set_entregado"),
    url(r'^entrega_reparacion/(?P<id_producto>\d*)/$', views.entrega_reparacion, name="entrega_reparacion"),
    url(r'^modificar_presupuesto/(?P<id_producto>\d*)/$', views.modificar_presupuesto, name="modificar_presupuesto"),
    url(r'^save_lineas_pres/(?P<id_pres>\d*)/$', views.save_lineas_pres, name="save_lineas_pres"),
    url(r'^find_presupuesto/$', views.find_presupuesto, name="find_presupuesto"),
    url(r'^send_presupuesto/(?P<id_producto>\d*)/$', views.send_presupuesto, name="send_presupuesto"),
    url(r'^find_actuacion_taller/$', views.find_actuacion_taller, name="find_actuacion_taller"),
    url(r'^facturar_presupuesto/(?P<id_pres>\d*)/$', views.facturar_presupuesto, name="facturar_presupuesto"),
    url(r'^add_nota_reparacion/(?P<id_pres>\d*)/$', views.add_nota_reparacion, name="add_nota_reparacion"),
    url(r'^rm_nota_reparacion/(?P<id_nota>\d*)/(?P<id_producto>\d*)/$', views.rm_nota_reparacion, name="rm_nota_reparacion"),
]

GESTION = [
    url(r'^clientes/$', views.clientes, name="clientes"),
    url(r'^clientes/(?P<id_cliente>\d*)/$', views.clientes, name="clientes"),
    url(r'^save_cliente/$', views.save_cliente, name="save_cliente"),


    url(r'^direcciones/$', views.direcciones, name="direcciones"),
    url(r'^direcciones/(?P<id_cliente>\d*)/$', views.direcciones, name="direcciones"),

    url(r'^modelos/$', views.modelos, name="modelos"),
    url(r'^modelos/(?P<id_modelo>\d*)/$', views.modelos, name="modelos"),
    url(r'^save_modelo/$', views.save_modelo, name="save_modelo"),

    url(r'^marcas/$', views.marcas, name="marcas"),
    url(r'^marcas/(?P<id_marca>\d*)/$', views.marcas, name="marcas"),

    url(r'^categorias/$', views.categorias, name="categorias"),
    url(r'^categorias/(?P<id_categoria>\d*)/$', views.categorias, name="categorias"),

    url(r'^almacenes/$', views.almacenes, name="almacenes"),
    url(r'^almacenes/(?P<id_almacen>\d*)/$', views.almacenes, name="almacenes"),

    url(r'^tipo_usados/$', views.tipos, name="tipo_usados"),
    url(r'^tipo_usados/(?P<id_tipo>\d*)/$', views.tipos, name="tipo_usados"),

    url(r'^empleados/$', views.usuarios, name="usuarios"),
    url(r'^empleados/(?P<id_user>\d*)/$', views.usuarios, name="usuarios"),

    url(r'^tipo_testeo/$', views.tipo_testeo, name="tipo_testeo"),
    url(r'^tipo_testeo/(?P<id_tipo>\d*)/$', views.tipo_testeo, name="tipo_testeo"),

    url(r'^rm_categorias/(?P<id_categoria>\d*)/$', views.rm_categorias, name="rm_categorias"),
    url(r'^rm_marcas/(?P<id_marca>\d*)/$', views.rm_marcas, name="rm_marcas"),
    url(r'^rm_modelos/(?P<id_modelo>\d*)/$', views.rm_modelos, name="rm_modelos"),
    url(r'^rm_almacenes/(?P<id_almacen>\d*)/$', views.rm_almacenes, name="rm_almacenes"),
    url(r'^rm_tipos/(?P<id_tipo>\d*)/$', views.rm_tipos, name="rm_tipos"),
    url(r'^rm_clientes/(?P<id_cliente>\d*)/$', views.rm_clientes, name="rm_clientes"),
    url(r'^rm_direcciones/(?P<id_direccion>\d*)/$', views.rm_direcciones, name="rm_direcciones"),
    url(r'^rm_empleados/(?P<id_user>\d*)/$', views.rm_empleados, name="rm_empleados"),
    url(r'^rm_tipo_testeo/(?P<id_tipo>\d*)/$', views.rm_tipo_testeo, name="rm_tipo_testeo"),

    url(r'^edit_direcciones/(?P<id_direccion>\d*)/$', views.edit_direcciones, name="edit_direcciones"),
    url(r'^lista_clientes/$', views.lista_clientes, name="lista_clientes"),
    url(r'^lista_usuarios/$', views.lista_usuarios, name="lista_usuarios"),
    url(r'^lista_modelos/$', views.lista_modelos, name="lista_modelos"),

    url(r'^configuracion/$', views.configuracion, name="configuracion"),
]

ALMACEN = [
    url(r'^productos/$', views.productos, name="productos"),
    url(r'^productos/(?P<id_producto>\d*)/$', views.productos, name="productos"),
    url(r'^modificar_precio_venta/(?P<id_producto>\d*)/$', views.modificar_precio_venta, name="modificar_precio_venta"),
    url(r'^modificar_precio_venta/$', views.modificar_precio_venta, name="modificar_precio_venta_none"),

    url(r'^rm_productos/(?P<id_producto>\d*)/$', views.rm_producto, name="rm_producto"),
    url(r'^rm_productos/(?P<id_producto>\d*)/(?P<pg>.*)/$', views.rm_producto, name="rm_producto"),

    url(r'^complementos/$', views.complementos, name="complementos"),
    url(r'^complementos/(?P<id_producto>\d*)/$', views.complementos, name="complementos"),
    url(r'^save_complemento/$', views.save_complemento, name="save_complemento"),


    url(r'^cp_productos/(?P<id_modelo>\d*)/$', views.cp_productos, name="cp_productos"),
    url(r'^lista_complementos/$', views.lista_complementos, name="lista_complementos"),
    url(r'^listado_productos/(?P<estado>.*)$', views.lista_productos, name="lista_productos"),

    url(r'^salir_productos_usados/$', views.salir_productos_usados, name="salir_productos_usados"),
    url(r'^salir_elegir_modelo/$', views.salir_elegir_modelo, name="salir_elegir_modelo"),
    url(r'^al_find_cliente/$', views.al_find_cliente, name="al_find_cliente"),
    url(r'^al_find_modelo/$', views.al_find_modelo, name="al_find_modelo"),
    url(r'^al_productos/$', views.marcas, name="al_productos"),
    url(r'^al_set_cliente/(?P<id_cliente>\d*)/$', views.al_set_cliente, name="al_set_cliente"),
    url(r'^al_set_cliente/$', views.al_set_cliente, name="al_set_cliente_none"),
    url(r'^al_set_modelo/(?P<id_modelo>\d*)/$', views.al_set_modelo, name="al_set_modelo"),
    url(r'^cambiar_estado/(?P<id>\d*)/$', views.cambiar_estado, name="cambiar_estado"),
]

INFORMES = [
    url(r'^listado_facturas/$', views.listado_facturas, name="listado_facturas"),
    url(r'^listado_compras/$', views.listado_compras, name="listado_compras"),
    url(r'^lista_presupuestos/$', views.lista_presupuestos, name="lista_presupuestos"),
    url(r'^find_facturas/$', views.find_facturas, name="find_facturas"),
    url(r'^find_compra/$', views.find_compra, name="find_compra"),
    url(r'^lista_doc_testeo/$', views.listado_doc_testeos, name="lista_doc_testeo"),
    url(r'^get_doc_testeo_by_id/(?P<id_doc>\d*)/$', views.get_doc_testeo_by_id, name="get_doc_testeo_by_id"),
    url(r'^balances/$', views.balances, name="balances"),
]

urlpatterns = [
    url(r'^salir_compra/$', views.salir_compra, name="salir_compra"),
    url(r'^salir_venta/$', views.salir_venta, name="salir_venta"),
    url(r'^find_cliente/$', views.find_cliente, name="find_cliente"),
    url(r'^cp_productos/$', views.cp_productos, name="cp_productos_none"),
    url(r'^cp_lista_modelos/$', views.cp_lista_modelos, name="cp_lista_modelos"),
    url(r'^calcular_precio_usado/(?P<id_modelo>\d*)/$', views.calcular_precio_usado, name="calcular_precio_usado"),
    url(r'^hacer_compra/$', views.hacer_compra, name="hacer_compra"),
    url(r'^cancelar_compra/$', views.cancelar_compra, name="cancelar_compra"),
    url(r'^testeo/(?P<id_producto>\d*)/$', views.testeo, name="testeo"),
    url(r'^set_estado_testeo/(?P<test_id>\d*)/(?P<p_id>\d*)/(?P<estado>.*)/$', views.set_estado_testeo, name="set_estado_testeo"),
    url(r'^set_estado_testeo/$', views.set_estado_testeo, name="set_estado_testeo_none"),
    url(r'^send_para_tester/(?P<id_modelo>\d*)/$', views.send_para_tester, name="send_para_tester"),
    url(r'^finalizar_testeo/$', views.finalizar_testeo, name="finalizar_testeo"),
    url(r'^get_historial/(?P<id_producto>\d*)/$', views.get_historial, name="get_historial"),
    url(r'^get_document_by_id/(?P<id_producto>\d*)/$', views.get_document_by_id, name="get_document_by_id"),
    url(r'^get_document_by_code/(?P<code>.*)/$', views.get_document_by_code, name="get_document_by_code"),
    url(r'^trato_compra/(?P<id_producto>\d*)/$', views.trato_compra, name="trato_compra"),
    url(r'^cancelar_trato/(?P<id_producto>\d*)/$', views.cancelar_trato, name="cancelar_trato"),
    url(r'^editar_producto/(?P<id_producto>\d*)/$', views.productos, name="productos"),
    url(r'^validar_compra/(?P<id_compra>\d*)/$', views.validar_compra, name="validar_compra"),
    url(r'^sign_compra/(?P<code>.+)/$', views.sign_compra, name="sign_compra"),
    url(r'^send_sign/(?P<id_producto>\d*)/$', views.send_sign, name="send_sign"),
    url(r'^volver_testear_producto/(?P<id_producto>\d*)/$', views.volver_testear_producto, name="volver_testear_producto"),
    url(r'^ventas_find_cliente/$', views.ventas_find_cliente, name="ventas_find_cliente"),
    url(r'^ventas/$', views.ventas, name="ventas"),
    url(r'^ticket/$', views.ticket, name="ticket"),
    url(r'^get_modificar_factura/(?P<id_venta>\d*)/$', views.get_modificar_factura, name="get_modificar_factura"),
    url(r'^modificar_factura/(?P<id_venta>\d*)/$', views.modificar_factura, name="modificar_factura"),
    url(r'^get_modificar_compra/(?P<id_compra>\d*)/$', views.get_modificar_compra, name="get_modificar_compra"),
    url(r'^modificar_compra/(?P<id_compra>\d*)/$', views.modificar_compra, name="modificar_compra"),
    url(r'^ch_find_cliente/$', views.ch_find_cliente, name="ch_find_cliente"),
    url(r'^ch_find_modelo/$', views.ch_find_modelo, name="ch_find_modelo"),
    url(r'^get_sugestion/.*/$', views.get_sugestion, name="get_sugestion"),
    url(r'^get_producto/$', views.get_producto, name="get_producto"),
    url(r'^facturar/$', views.facturar, name="facturar"),
    url(r'^get_estatus/$', views.get_status, name="get_status"),
    url(r'^get_factura_by_id/(?P<id_venta>\d*)/$', views.get_factura_by_id, name="get_factura_by_id"),
    url(r'^get_lineas_factura/(?P<id_venta>\d*)/$', views.get_lineas_factura, name="get_lineas_factura"),
    url(r'^get_factura_by_code/(?P<code>.*)/$', views.get_factura_by_code, name="get_factura_by_code"),
    url(r'^get_all_document/(?P<id_producto>\d*)/$', views.get_all_document, name="get_all_document"),
    url(r'^send_factura/(?P<id_venta>\d*)/$', views.send_factura, name="send_factura"),
]+ MENU + ALMACEN + GESTION + TALLER + USER + SIGN + INFORMES + ABONOS

urlpatterns = urlpatterns + PROVEEDOR + GARANTIAS + BALANCES + DOCUMENTOS
