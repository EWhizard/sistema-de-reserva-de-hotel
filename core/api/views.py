from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from  django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta

from base.models import *
# User, Room, Hotel, Reservation, Bill
from .serializers import (
    UserSerializer,
    HotelSerializer,
    ReservationSerializer,
)

@api_view(["POST"])
def register_customer(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.username = user.name.lower()
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_additional_details(request):
    user = request.user
    data = request.data
    user.phoneNumber = data.get("phone_no")
    user.dob = data.get("dob")
    user.gender = data.get("gender")
    user.preference = data.get("preference")
    user.save()
    return Response({"message": "Details updated successfully"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=email, password=password)
    if user:
        login(request, user)
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def logout_user(request):
    logout(request)
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_hotels(request):
    hotels = Hotel.objects.all().order_by("-rating")
    serializer = HotelSerializer(hotels, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_room(request, pk):
    data = request.data
    from_date = data.get("from_date")
    to_date = data.get("to_date")
    num_occupants = data.get("num_occupants")
    room_type = data.get("room_type")
    hotel = get_object_or_404(Hotel, id=pk)


    # from_date = request.POST.get("from_date")
    #     to_date = request.POST.get("to_date")
    #     num_occupants = int(request.POST.get("num"))
    #     room_type = request.POST.get("room_type")
    #     hotel_id = pk  # Assuming you have the hotel ID in the form

        # Convert from_date and to_date strings to datetime objects
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")

    if from_date < datetime.now() or to_date < datetime.now():
        raise ValidationError("Dates cannot be in the past")

    booking_duration = (
            to_date - from_date
        ).days + 1  # Add 1 to include the last day

        # Validate booking duration to be between 1 and 10 nights
    if booking_duration < 1 or booking_duration > 10:
        raise ValidationError("Booking duration must be between 1 and 10 nights")

        # Retrieve rooms of the specified type in the selected hotel
    rooms_of_type = Room.objects.filter(hotel=hotel_id, type=room_type)

        # Filter reservations that overlap with the given date range
    overlapping_reservations = Reservation.objects.filter(
            Q(check_in__lte=to_date, check_out__gte=from_date)
            | Q(check_in__gte=from_date, check_out__lte=to_date)
            | Q(check_in__lte=from_date, check_out__gte=to_date),
            room__in=rooms_of_type,
        )

        # Exclude rooms with overlapping reservations
    available_rooms = rooms_of_type.exclude(
            id__in=overlapping_reservations.values_list("room_id", flat=True)
        )

        # Filter available rooms based on the number of occupants
        # available_rooms = available_rooms.filter(number_of_beds__gte=num_occupants)

    allocated_rooms = []
    remaining_occupants = num_occupants
    money = 0 
    for room in available_rooms:
        if remaining_occupants <= 0:
            break
        occupants_in_room = min(remaining_occupants, room.number_of_beds)
        reservation = Reservation.objects.create(
                room=room,
                customer=request.user,
                check_in=from_date,
                check_out=to_date,
                number_of_occupants=occupants_in_room,
                advance=0,  # You may adjust this based on your business logic
                booked_from=timezone.now(),
                booked_till=timezone.now(),
                method="",  # You may set payment method based on your business logic
                payment_status="",  # You may set payment status based on your business logic
            )
            # Create bill for the reservation
        bill_amount = calculate_bill_amount(
                reservation
            )  # You need to define this function
        money += bill_amount
        Bill.objects.create(
                booking=reservation,
                customer=request.user,
                amount=bill_amount,
                status="PENDING",  # You can set the status as needed
            )
        allocated_rooms.append(room)
        remaining_occupants -= occupants_in_room

    if remaining_occupants > 0:
        return Response({ "message" : "base/no_available_rooms.html"}, status = status.HTTP_400_BAD_REQUEST)
        # return render(request, "base/no_available_rooms.html")

        # Redirect or render a success message
    return Response(
            {"allocated_rooms": allocated_rooms,"amount" : money }, status=status.HTTP_200_OK
        )


def calculate_bill_amount(booking):
    room = booking.room
    booking_date = booking.booked_time

    # Retrieve room price details
    room_price = RoomPrice.objects.get(room=room)

    # Determine if the booking date falls on a weekday or a weekend
    total_amount = 0
    current_date = booking.check_in
    d = 0
    while current_date <= booking.check_out:
        d+=1
        # Determine if the current night is a weekend night excluding the first night
        if current_date.weekday() in [5, 6]:
            total_amount += (room_price.base + room_price.weekend)
        else:
            total_amount += room_price.base

        # Increment current date
        current_date += timedelta(days=1)

    # Determine if the booking date falls within the seasonal period
    is_seasonal = False  # You need to implement logic to determine this based on your requirements

    # Calculate the total amount

    if is_seasonal:
        total_amount += room_price.seasonal

    return total_amount



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_reservations(request):
    reservations = Reservation.objects.filter(customer=request.user, isCancelled=False)
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, id=pk)
    reservation.isCancelled = True
    reservation.save()

    # Update bill status
    bill = get_object_or_404(Bill, booking=reservation)
    bill.status = "CANCELLED"
    bill.save()

    return Response({"message": "Reservation cancelled"}, status=status.HTTP_200_OK)
