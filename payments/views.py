from .models import Payment
from .serializers import PaymentHistorySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from teams.models import Team
import uuid
from django.conf import settings
import requests



class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        team_id = request.data.get("team_id")
        amount = request.data.get("amount")

        # Validation check
        if not team_id or not amount:
            return Response(
                {
                    "error" : "team_id and amount are required."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response(
                {
                    "error" : "Team not found."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique transaction id
        transaction_id = f"TNX-{uuid.uuid4().hex[:10].upper()}"

        # Generate a PENDING record on database
        payment_record = Payment.objects.create(
            team=team,
            paid_by=user,
            transaction_id=transaction_id,
            amount=amount,
            status="PENDING"
        )
        
        # Create data-payload for SSLCOMMERZ
        ssl_data = {
            "store_id" : settings.SSLCOMMERZ_STORE_ID,
            "store_passwd" : settings.SSLCOMMERZ_STORE_PASS,
            "total_amount" : amount,
            "currency" : "BDT",
            "tran_id" : transaction_id,

            # Redirect URLs
            "success_url" : settings.SSLCOMMERZ_SUCCESS_URL,
            "fail_url" : settings.SSLCOMMERZ_FAIL_URL,
            "cancel_url" : settings.SSLCOMMERZ_CANCEL_URL,

            # Customer info (Fixed 'username' typo)
            "cus_name" : user.get_full_name() or user.username,
            "cus_email" : user.email or "noemail@test.com",
            "cus_phone" : getattr(user, "phone", "01700000000"),
            
            # Required address fields to bypass SSLCommerz validation
            "cus_add1": "Dhaka, Bangladesh",
            "cus_city": "Dhaka",
            "cus_state": "Dhaka",
            "cus_postcode": "1200",
            "cus_country": "Bangladesh",

            # Product info
            "product_category" : "Tournament Registration",
            "shipping_method" : "NO",
            "num_of_item" : 1,
        }

        gateway_url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php" if settings.SSLCOMMERZ_IS_SANDBOX else "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
        
        try:
            response = requests.post(gateway_url, data=ssl_data)
            response_data = response.json()

            # Fixed: checking status and reading GatewayPageURL from response_data
            if response_data.get('status') == "SUCCESS":
                payment_url = response_data.get("GatewayPageURL")
                return Response(
                    {
                        "message" : "Payment session created successfully.",
                        "transaction_id" : transaction_id,
                        "payment_url" : payment_url,
                    }, status=status.HTTP_200_OK
                )
            else:
                payment_record.status = "FAILED"
                payment_record.save()
                return Response(
                    {
                        "error" : "Failed to initiate payment with SSLCOMMERZ.",
                        "details": response_data 
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except requests.exceptions.RequestException as e:
            payment_record.status = "FAILED"
            payment_record.save()
            return Response(
                {
                    "error" : f"Network error occurred: {str(e)}" 
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name = "dispatch")
class PaymentSuccessView(APIView):
    permission_classes = []


    def post(self, request):
        tran_id = request.data.get("tran_id")
        val_id = request.data.get("val_id")
        card_type = request.data.get("card_type")
        bank_tran_id = request.data.get("bank_tran_id")

        try:
            payment = Payment.objects.get(transaction_id = tran_id)
            payment.status = "SUCCESS"
            payment.val_id = val_id
            payment.card_type = card_type
            payment.bank_tran_id = bank_tran_id
            payment.save()

            payment.team.is_verified = True
            payment.team.save()

            return Response({
                "message" : "Payment Successful."
            }, status= status.HTTP_200_OK)
        
        except Payment.DoesNotExist:
            return Response({
                "error" : "Transaction not found."
            }, status= status.HTTP_400_BAD_REQUEST)
        


@method_decorator(csrf_exempt, name = "dispatch")
class PaymentFailView(APIView):
    permission_classes = []

    def post(self, request):
        tran_id = request.data.get(tran_id)

        try:
            payment = Payment.objects.get(transaction_id = tran_id)
            payment.status = "FAILED"
            payment.save()

            return Response({
                "message" : "Payment Failed."
            }, status= status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({
                "message" : "Transaction not found."
            }, status= status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name = "dispatch")
class PaymentCancelView(APIView):
    permission_classes = []

    def post(self, request):

        tran_id = request.data.get("tran_id")
        try:
            payment = Payment.objects.get(transction_id = tran_id)
            payment.status = "CANCELLED"
            payment.save()

            return Response({
                "message" : "Payment cancelled."
            }, status= status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({
                "message" : "Transaction not found."
            }, status= status.HTTP_404_NOT_FOUND)



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
    