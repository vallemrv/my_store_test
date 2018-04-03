# @Author: Manuel Rodriguez <valle>
# @Date:   26-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: urls.py
# @Last modified by:   valle
# @Last modified time: 31-Dec-2017
# @License: Apache license vesion 2.0

from django.conf.urls import url, include
from . import views
API_SMS = [
    url(r'^get_all_telf/$', views.get_all_telf, name="get_all_telf"),

]

urlpatterns = [
    url(r'^get_documento_firma/$', views.get_documento_firma, name="get_documento_firma"),
    url(r'^set_firma/(?P<id_compra>\d*)/(?P<dni>.*)/$', views.set_firma, name="set_firma"),
    url(r'^set_firma_compra_insitu/(?P<id_compra>\d*)/(?P<dni>.*)/$', views.set_firma_compra_insitu, name="set_firma_compra_insitu"),
    url(r'^set_firma_press_insitu/(?P<id_press>\d*)/(?P<dni>.*)/$', views.set_firma_press_insitu, name="set_firma_press_insitu"),
    url(r'^set_firma_testeo_insitu/(?P<id_test>\d*)/(?P<dni>.*)/$', views.set_firma_testeo_insitu, name="set_firma_testeo_insitu"),

]+ API_SMS
