from .models import Payment
from .serializers import PaymentHistorySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class PaymentHistoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user

        if user.is_staff or user.is_superuser:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(paid_by = user)

        serializer = PaymentHistorySerializer(payments, many = True)
        return Response(serializer.data)
    