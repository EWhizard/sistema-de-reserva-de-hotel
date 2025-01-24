from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_customer, name='register-customer'),  # Register new user
    path('login/', views.login_user, name='login'),  # Login user
    path('logout/', views.logout_user, name='logout'),  # Logout user
    path('additional-details/', views.add_additional_details, name='additional-details'),  # Update additional details
    path('hotels/', views.list_hotels, name='list-hotels'),  # List all hotels
    path('book-room/<int:pk>/', views.book_room, name='book-room'),  # Book a room by hotel ID
    path('reservations/', views.list_reservations, name='list-reservations'),  # List user reservations
    path('cancel-reservation/<int:pk>/', views.cancel_reservation, name='cancel-reservation'),  # Cancel a reservation
]
