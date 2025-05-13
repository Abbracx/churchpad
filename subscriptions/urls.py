from django.urls import path
from . import views


app_name = 'subscriptions'

urlpatterns = [
    path('subscriptions/', views.list_subscriptions, name='subscription_list'),
    path('subscriptions/create/', views.subscribe, name='subscription_create'),
    path('subscriptions/confirm/', views.confirm_subscription, name='subscription_confirm'),
    path('subscriptions/<int:pk>/delete/', views.unsubscribe, name='subscription_delete'),
    path('plans/', views.list_plans, name='plan_list'), 
    path('plans/register-price/', views.register_price, name='register_price'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]