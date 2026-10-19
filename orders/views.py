from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets

from orders.models import Order, Ticket
from orders.serializers import OrderSerializer, TicketSerializer


@extend_schema(
    tags=["Orders"],
    description=(
        "Orders require authentication. Regular users can access only their own "
        "orders; staff users can manage all orders. An order must contain at least "
        "one ticket, submitted as a nested list."
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("tickets__flight__airplane")
        .order_by("pk")
    )
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve", "create"):
            return [permissions.IsAuthenticated()]

        return [permissions.IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset

        return self.queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action in ("update", "partial_update"):
            context["order_instance"] = self.get_object()

        return context


@extend_schema(
    tags=["Tickets"],
    description="Tickets are read-only through this API and are created together with an order.",
)
class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.select_related(
        "flight__airplane",
        "order",
    ).order_by("pk")
    serializer_class = TicketSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(order__user=self.request.user)
