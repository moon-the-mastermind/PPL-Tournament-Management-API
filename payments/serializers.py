from rest_framework import serializers
from .models import Payment

class PaymentHistorySerializer(serializers.ModelSerializer):
    paid_by_name = serializers.SerializerMethodField()
    team_name = serializers.ReadOnlyField(source = "team.name")

    class Meta:
        model = Payment
        fields = [
            "id", "team", "team_name", "paid_by", 
            "paid_by_name", "transaction_id", "amount",
            "currency", "sender_number", "card_type", "status",
            "created_at"
        ]

        def get_paid_by_name(self, obj):
            if object.paid_by:
                return obj.paid_by.get_full_name() or obj.paid_by.username
            return "Guest"