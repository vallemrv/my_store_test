# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   09-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 07-Feb-2018
# @License: Apache license vesion 2.0


from django.conf import settings
from django.template.loader import get_template
#from django.template import Context
from adminshop.models import (ConfigSite, Compras, LineasVentas, Presupuesto,
                              LineasPresupuesto, LineasAbonos)
from io import BytesIO, open as OpenIO
import trml2pdf
import os

def get_documento_compra(producto, compra):
    if compra.tipo_vendedor == 'CL':
        tmpl_path = settings.DOCUMENT_TMPL
        vendedor = compra.get_vendedor()
        file_rml = os.path.join(tmpl_path, "documento_compra.xml")
        data = {'title': "Documento de compra %s" % vendedor["nombre"],
                "fecha": compra.fecha_entrada,
                "codigo_compra": compra.codigo_compra,
                "num_factura": compra.id,
                "nombre": vendedor["nombre"],
                "telefono": vendedor['telefono'],
                "DNI": vendedor["DNI"].upper(),
                "domicilio": vendedor['direccion'],
                "firma": compra.firma,
                "modelo": producto.modelo,
                "ns_imei": producto.ns_imei,
                "precio": str(producto.precio_compra)+" €",
                "firma_freak": ConfigSite.objects.all()[0].firma_tienda}
        template = get_template(file_rml)
        xmlstring = template.render(data)
        pdfstr = trml2pdf.parseString(xmlstring.encode("utf-8"))
        output = BytesIO()
        output.write(pdfstr)
        return output
    else:
        tmpl_path = settings.DOCUMENT_PROVEEDOR
        file_rml = os.path.join(tmpl_path, str(compra.doc_proveedor))
        if os.path.exists(file_rml):
            file = open(file_rml, "rb")
            output = BytesIO()
            output.write(file.read())
            return output
        else:
            return get_documeto_error()

def get_documeto_policia(intervalo):
    response = BytesIO()
    tmpl_path = settings.INFORMES_POLICIA
    file_rml = os.path.join(tmpl_path, intervalo+".pdf" )
    if os.path.exists(file_rml):
        f = open(file_rml, "rb")
        response.write(f.read())
        return response
    else:
        return get_documeto_error()
    

def crear_documento_policia(compras, start, end):
    try:
        tmpl_path = settings.DOCUMENT_TMPL
        path_doc = settings.INFORMES_POLICIA
        informe = open(os.path.join(path_doc, start.strftime("%d_%m_%Y")+"-"+end.strftime("%d_%m_%Y")+".pdf"), "w")
        data = {"reg": [],
                "start": start.strftime("%d/%m/%Y"),
                "end": end.strftime("%d/%m/%Y")}
        for c in compras:
            v = c.get_vendedor()
            d = {"nombre": unicode(v["nombre"]),
                 "direccion": unicode(v["direccion"]),
                 "DNI": unicode(v["DNI"]),
                 "codigo": unicode(c.codigo_compra),
                 "ns_imei": unicode(c.producto.ns_imei),
                 "des": unicode(c.producto)}
            data["reg"].append(d)


        file_rml = os.path.join(tmpl_path, "documento_policia.xml")
        template = get_template(file_rml)
        xmlstring = template.render(data)
        pdfstr = trml2pdf.parseString(xmlstring.encode("utf-8"))
        informe.write(pdfstr)
        informe.close()
    except Exception as e:
        print e
        return False
    return True

def get_documento_garantia(garantia):
    response = BytesIO()
    tmpl_path = settings.DOCUMENT_PROVEEDOR
    file_rml = os.path.join(tmpl_path, garantia.documento.name )
    if os.path.exists(file_rml):
        f = open(file_rml, "rb")
        response.write(f.read())
        return response
    else:
        return get_documeto_error()

def get_documento_venta(venta, cliente, domicilio):
    if cliente == None:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

        tmpl_path = settings.DOCUMENT_TMPL
        file_rml = os.path.join(tmpl_path, "ticket.xml")
        total = get_total_factura(venta.pk)
        lineas, regimen = get_regimen_ventas(venta)
        PAGE_HEIGHT = len(lineas) * 150
        data = {"file_name":"ticket_num_%s.pdf" % venta.id,
                'title': "Ticket num %s" % venta.id,
                "entrega": venta.entrega,
                "devolver": venta.entrega - total,
                "fecha": venta.fecha_salida,
                "num_factura": venta.id,
                "productos": lineas,
                "forma_pago": venta.get_forma_pago_display(),
                "total": total,
                "regimen": regimen
                }
        output = BytesIO()
        c = canvas.Canvas(output)
        c.setPageSize((62*mm, PAGE_HEIGHT*mm))
        logo = os.path.join(tmpl_path, "freakmedia-logo.jpg")
        c.drawImage(logo, 2 * mm,(PAGE_HEIGHT * mm)-30*mm, width=60*mm, height=22*mm, mask='auto')
        c.drawCentredString(62*mm/2.0, (PAGE_HEIGHT * mm)-35*mm, "14631732-Y")
        c.drawCentredString(62*mm/2.0, (PAGE_HEIGHT * mm)-40*mm, "CAMINO DE RONDA, 73")
        c.drawCentredString(62*mm/2.0, (PAGE_HEIGHT * mm)-45*mm, "18004, GRANADA")
        c.showPage()
        c.save()
        return output
    else:
        tmpl_path = settings.DOCUMENT_TMPL
        total = get_total_factura(venta.pk)
        lineas, regimen = get_regimen_ventas(venta)
        doc_template = get_template_factura(venta.pk)
        file_rml = os.path.join(tmpl_path, doc_template)
        data = {'title': "Factura num %s" % venta.id,
                "entrega": venta.entrega,
                "devolver": "%.2f" % (float(venta.entrega) - total),
                "fecha": venta.fecha_salida,
                "num_factura": venta.id,
                "nombre": cliente.nombre_completo,
                "telefono": cliente.telefono,
                "DNI": cliente.DNI.upper(),
                "domicilio": domicilio,
                "productos": lineas,
                "forma_pago": venta.get_forma_pago_display(),
                "total": total,
                "regimen": regimen,
                "pk": venta.pk
                }

        template = get_template(file_rml)
        #context = Context(data)
        xmlstring = template.render(data)
        pdfstr = trml2pdf.parseString(xmlstring.encode("utf-8"))
        output = BytesIO()
        output.write(pdfstr)
        return output


# crea el documento pdf y lo muestra
def get_documento_presupuesto(pres, cliente, direccion):
    tmpl_path = settings.DOCUMENT_TMPL
    response = BytesIO()
    file_rml = os.path.join(tmpl_path, "documento_presupuesto.xml")
    total = get_total_presupuesto(pres.pk)
    data = {'title': "Presupuesto num %s" % pres.id,
            "producto": pres.producto,
            "fecha": pres.fecha,
            "entrega": pres.entrega,
            "total_cobro": "{0:.2f}".format(float(total) - float(pres.entrega)),
            "num_pres": pres.id,
            "sn_imei": pres.producto.ns_imei,
            "nombre": cliente.nombre_completo,
            "domicilio": direccion,
            "telefono": cliente.telefono,
            "DNI": cliente.DNI,
            "detalle": pres.notas_cliente,
            "lineas": LineasPresupuesto.objects.filter(presupuesto__pk=pres.pk),
            "total": total,
            "firma_cliente": pres.firma,
            "firma_freak": ConfigSite.objects.all()[0].firma_tienda
            }
    template = get_template(file_rml)
    #context = Context(data)
    xmlstring = template.render(data)
    pdfstr = trml2pdf.parseString(xmlstring.encode("utf-8"))
    response.write(pdfstr)
    return response


def get_documento_testeo(doc):
    tmpl_path = settings.DOCUMENT_TMPL
    response = BytesIO()
    file_rml = os.path.join(tmpl_path, "documento_testeo.xml")
    data = {'title': "Documento de testeo %s" % doc.producto,
            "fecha": doc.fecha,
            "nombre": doc.cliente.nombre_completo,
            "telefono": doc.cliente.telefono,
            "DNI": doc.cliente.DNI.upper(),
            "firma": doc.firma,
            "modelo": doc.producto.modelo,
            "ns_imei": doc.producto.ns_imei,
            "firma_freak": ConfigSite.objects.all()[0].firma_tienda}
    template = get_template(file_rml)
    #context = Context(data)
    xmlstring = template.render(data)
    pdfstr = trml2pdf.parseString(xmlstring.encode("utf-8"))
    response.write(pdfstr)
    return response

def get_documento_abono(abono, cliente, domicilio):
    tmpl_path = settings.DOCUMENT_TMPL
    file_rml = os.path.join(tmpl_path, "documento_abono.xml")
    data = {'title': "Abono num %s" % abono.id,
            "fecha": abono.fecha_salida,
            "num_factura": abono.factura_id,
            "num_abono": abono.id,
            "nombre": cliente.nombre_completo,
            "telefono": cliente.telefono,
            "DNI": cliente.DNI.upper(),
            "domicilio": domicilio,
            "productos": LineasAbonos.objects.filter(abono__pk=abono.pk),
            "forma_pago": abono.get_forma_pago_display(),
            "total": get_total_abono(abono.pk),
            }

    template = get_template(file_rml)
    #context = Context(data)
    xmlstring = template.render(data)
    pdfstr = trml2pdf.parseString(xmlstring.encode("utf-8"))
    respose = BytesIO()
    respose.write(pdfstr)
    return respose

def get_regimen_ventas(venta):
    lineas = LineasVentas.objects.filter(venta__pk=venta.pk)
    regimen = "REBU"
    try:
        compras = Compras.objects.filter(codigo_compra=lineas[0].codigo_compra)
        if len(compras) == 1:
            compra = compras[0]
        elif len(compras) > 1:
            compra = Compras.objects.get(producto__ns_imei=lineas[0].ns_imei)
        regimen = compra.tipo_compra
    except Exception as e:
        print(e)
    return lineas, regimen

def get_total_factura(pk):
    lineas =  LineasVentas.objects.filter(venta__pk=pk)
    total = 0
    for l in lineas:
        descuento = 1 - (float(l.descuento)/100.00)
        total += float(l.can) * float(l.p_unidad) * float(descuento)
    return float("%.2f" % total)


def get_total_presupuesto(pk):
    lineas =  LineasPresupuesto.objects.filter(presupuesto__pk=pk)
    total = 0
    for l in lineas:
        descuento = 1 - (float(l.descuento)/100.00)
        total += float(l.can) * float(l.precio) * float(descuento)
    return float("%.2f" % total)

def get_total_abono(pk):
    lineas =  LineasAbonos.objects.filter(abono__pk=pk)
    total = 0
    for l in lineas:
        descuento = 1 - (float(l.descuento)/100.00)
        total += float(l.can) * float(l.p_unidad) * float(descuento)
    return float("%.2f" % total)


def get_documeto_error():
    response = BytesIO()
    tmpl_path = settings.DOCUMENT_TMPL
    file_rml = os.path.join(tmpl_path, 'error_pdf.pdf' )
    f = open(file_rml, "rb")
    response.write(f.read())
    return response


def get_template_factura(pk):
        p = Presupuesto.objects.filter(factura_id=pk)
        if len(p) > 0:
            return "documento_factura_rep.xml"
        else:
            return "documento_factura.xml"
