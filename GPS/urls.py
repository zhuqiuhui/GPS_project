from django.conf.urls import url
from . import view,search,search2
from GPS_app import views
import settings


urlpatterns = [
    url(r'^search-form$', search.search_form),
    url(r'^search$', search.search),
    url(r'^search-post$', search2.search_post),
    url(r'^success/$', view.uploadFileResult, name='success'),
    url(r'^uploadFile/$', view.upload_file, name='upload'),
    url(r'^table/$',view.table,name='table'), #
    url(r'^gpsPoint/$',views.select), #
    url(r'^main/$',view.mainFrame), #
    url(r'^mainFooter/$',view.mainFooter), #
    url(r'^mainTop/$',view.mainTop), #
    url(r'^mainLeft/$',view.mainLeft), #
    url(r'^mainRight/$',view.mainRight), #
    url(r'^importGPS/$',view.importGPS), #
    url(r'^importGPSSubmit/$',view.importGPSSubmit), #
    url(r'^displayGPSByDate/$',view.displayGPSByDate), #
    url(r'^displayGPSByDateSubmit/$',view.displayGPSByDateSubmit), #
    url(r'^displayGPSById/$',view.displayGPSById), #
    url(r'^displayGPSByIdSubmit/$',view.displayGPSByIdSubmit), #
    url(r'^feaAnalysis/$',view.feaAnalysis), #
    url(r'^feaAnalysisSubmit/$',view.feaAnalysisSubmit), #
    url(r'^inferTM/$',view.inferTM), #
    url(r'^inferTMSubmit/$',view.inferTMSubmit), #
]