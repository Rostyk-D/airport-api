"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
Including another URLconf
    1. Add an import:  from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from airports.views import AirportViewSet, RouteViewSet
from flights.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
)
from orders.views import OrderViewSet, TicketViewSet
from users.views import UserViewSet


router = DefaultRouter()

router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("crew", CrewViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)
router.register("users", UserViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/users/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/users/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
