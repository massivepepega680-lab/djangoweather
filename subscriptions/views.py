from rest_framework import viewsets, permissions
from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to view and manage their subscriptions"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Returns a list of all the subscriptions for the currently authenticated user"""
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associates the subscription with the currently authenticated user"""
        serializer.save(user=self.request.user)