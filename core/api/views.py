# views.py
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from base.models import User, Hotel, Room, Reservation, Bill
from .serializers import UserSerializer, HotelSerializer, RoomSerializer, ReservationSerializer, BillSerializer
from django.contrib.auth import authenticate, login, logout

@api_view(['GET'])
def home(request):
    return JsonResponse({"message": "Welcome to the API!"})

@api_view(['POST'])
def registerCustomer(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def additionalDetails(request):
    user = request.user
    user.phoneNumber = request.data.get("phone_no")
    user.dob = request.data.get("dob")
    user.gender = request.data.get("gender")
    user.preference = request.data.get("pref")
    try:
        user.save()
        return Response({"message": "Details updated successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def loginUser(request):
    mail = request.data.get("email")
    passwd = request.data.get("password")
    user = authenticate(request, email=mail, password=passwd)
    if user is not None:
        login(request, user)
        return Response({"message": "Logged in successfully."})
    return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logoutUser(request):
    logout(request)
    return Response({"message": "Logged out successfully."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def book(request):
    hotels = Hotel.objects.all().order_by("-rating")
    serializer = HotelSerializer(hotels, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bookRoom(request, pk):
    # Implement the booking logic as in your original view
    # Use request.data to get POST data
    # Example of getting data:
    from_date_str = request.data.get("from_date")
    to_date_str = request.data.get("to_date")
    num_occupants = int(request.data.get("num"))
    room_type = request.data.get("room_type")

    from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

    # Additional booking logic goes here...
    return Response({"message": "Booking successful."})  # Adjust this response accordingly

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listReservations(request):
    reservations = Reservation.objects.filter(customer=request.user, isCancelled=False)
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel(request, pk):
    try:
        reservation = Reservation.objects.get(id=pk)
        reservation.isCancelled = True
        reservation.save()
        bill = Bill.objects.get(booking=reservation)
        bill.status = "CANCELLED"
        bill.save()
        return Response({"message": "Reservation cancelled successfully."})
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def aboutView(request):
    return JsonResponse({"message": "About this API"})