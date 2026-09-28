"""config URL Configuration"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from airports.views import AirportViewSet, RouteViewSet
from flights.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
)
from orders.views import OrderViewSet, TicketViewSet
from users.views import EmailTokenObtainPairView, UserViewSet


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
    path(
        "api/users/login/",
        EmailTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/users/login/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/", include(router.urls)),
]
