from django.conf.urls import url
from myapp.views import UserRegistrationAPIView, UserLoginAPIView, UserLogoutAPIView, \
	MakeView, ModelView, VehicleInfoView, SaleInfoView, SaleInfoFileView, FilterView

urlpatterns = [
    url(r'^register/$', UserRegistrationAPIView.as_view(), name="register"),
    url(r'^login/$', UserLoginAPIView.as_view(), name="login"),
    url(r'^logout/$', UserLogoutAPIView.as_view(), name="logout"),
    url(r'^make/$', MakeView.as_view(), name="make"),
    url(r'^make/(?P<pk>[0-9]+)/$', MakeView.as_view()),
    url(r'^model/$', ModelView.as_view(), name="model"),
    url(r'^model/(?P<pk>[0-9]+)/$', ModelView.as_view()),
    url(r'^vehicle/$', VehicleInfoView.as_view(), name="model"),
    url(r'^vehicle/(?P<pk>[0-9]+)/$', VehicleInfoView.as_view()),
    url(r'^sale/$', SaleInfoView.as_view(), name="model"),
    url(r'^sale/(?P<pk>[0-9]+)/$', SaleInfoView.as_view()),
    url(r'^sale/file/$', SaleInfoFileView.as_view(), name="model"),
    url(r'^filter/$', FilterView.as_view(), name="model"),

]
