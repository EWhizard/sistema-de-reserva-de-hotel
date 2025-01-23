from django.urls import path
from .views import home, registerCustomer, additionalDetails, loginUser, logoutUser, book, bookRoom, listReservations, cancel, aboutView

urlpatterns = [
    path('home/', home, name='home'),
    path('register/', registerCustomer, name='register'),
    path('additional-details/', additionalDetails, name='additional-details'),
    path('login/', loginUser, name='login'),
    path('logout/', logoutUser, name='logout'),
    path('book/', book, name='book'),
    path('book-room/<int:pk>/', bookRoom, name='book-room'),
    path('reservations/', listReservations, name='list-reservations'),
    path('cancel/<int:pk>/', cancel, name='cancel'),
    path('about/', aboutView, name='about'),
]

