from rest_framework import permissions, viewsets

from orders.models import Order, Ticket
from orders.serializers import OrderSerializer, TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("tickets__flight__airplane")
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


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.select_related(
        "flight__airplane",
        "order",
    )
    serializer_class = TicketSerializer
    permission_classes = (permissions.AllowAny,)
