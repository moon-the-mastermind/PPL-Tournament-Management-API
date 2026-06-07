from django.urls import path
from . import views

urlpatterns = [

    path("initiate/", views.InitiatePaymentView.as_view(), name = "initiate_payment"),
    path("success/", views.PaymentSuccessView.as_view(), name = "payment_success"),
    path("success/", views.PaymentFailView.as_view(), name = "payment_fail"),
    path("success/", views.PaymentCancelView.as_view(), name = "payment_cancel"),

    path("history/", views.PaymentHistoryListView.as_view(), name = "payment_history"),
]