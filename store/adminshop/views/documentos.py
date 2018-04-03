# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   31-Jan-2018
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 03-Feb-2018
# @License: Apache license vesion 2.0

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import RangoPolicia
from adminshop.models import (DocumentSendPolice, DocumentSendGestoria, Compras,
                              ConfigSite)
from adminshop.utility import crear_documento_policia, get_documeto_policia

from datetime import datetime
import threading
import os
import io

@login_required(login_url='login_tk')
def lista_doc_policia(request):
    return render(request, "informes/policia/listado.html",
                  {"form": RangoPolicia(),
                   "query": DocumentSendPolice.objects.all()})

@login_required(login_url='login_tk')
def crear_informe_policia(request):
    if request.method == "POST":
        fecha_informe = RangoPolicia(request.POST)
        if fecha_informe.is_valid():
            start = request.POST["fecha_inicio"]
            end = request.POST["fecha_fin"]
            start = datetime.strptime(start, "%d/%m/%Y")
            end = datetime.strptime(end, "%d/%m/%Y")
            compras  = Compras.objects.filter(fecha_entrada__range=(start,end)).exclude(tipo_vendedor="NO", enviar_policia=True)
            crear_documento_policia(compras, start, end)
            policia = DocumentSendPolice(intervalo=start.strftime("%d_%m_%Y")+"-"+end.strftime("%d_%m_%Y"))
            policia.save()
        else:
            print fecha_informe.errors

    return render(request, "informes/policia/listado.html",
                  {"form": RangoPolicia(),
                   "query": DocumentSendPolice.objects.all()})

@login_required(login_url='login_tk')
def ver_documento_policia(request, id):
    doc = DocumentSendPolice.objects.get(pk=id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="%s.pdf"' % doc.intervalo
    docstr = get_documeto_policia(doc.intervalo)
    response.write(docstr.getvalue())
    return response


@login_required(login_url='login_tk')
def rm_doc_policia(request, id):
    doc = None
    try:
        doc = DocumentSendPolice.objects.get(pk=id)
        tmpl_path = settings.INFORMES_POLICIA
        file_doc = os.path.join(tmpl_path, doc.intervalo+".pdf")
        if os.path.exists(file_doc):
            os.remove(file_doc)
        doc.delete()
    except Exception as e:
        print e

    return render(request, "informes/policia/listado.html",
                  {"form": RangoPolicia(),
                   "query": DocumentSendPolice.objects.all()})



# para ver el documento pdf los usuarios
@login_required(login_url='login_tk')
def send_doc_policia(request, id):
    doc = DocumentSendPolice.objects.get(pk=id)
    doc.enviado = True
    doc.save()
    threading.Thread(target=send_doc_mail_policia, args=(doc,)).start()
    return render(request, "informes/policia/listado.html",
                  {"form": RangoPolicia(),
                   "query": DocumentSendPolice.objects.all()})


def send_doc_mail_policia(doc):
    docstr = get_documeto_policia(doc.intervalo)
    msg_plain = render_to_string(settings.BASE_DIR+'/templates/email/send_doc_policia.html',{
        "intervalo": doc.intervalo
    })
    email_policia = ConfigSite.objects.all()[0].email_policia
    if email_policia != "":
        email = EmailMessage(
            'Informe de compras',
            msg_plain,
            'info@freakmedia.es',
            [ConfigSite.objects.all()[0].email_policia],
            headers={'Message-ID': doc.intervalo},
        )
        email.attach(doc.intervalo+".pdf", docstr.getvalue(), 'application/pdf')
        email.send()
