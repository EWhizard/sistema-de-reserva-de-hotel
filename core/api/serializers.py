from rest_framework import serializers

from base.models import Hotel, Reservation, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'location', 'rooms_available', 'price_per_night']

class ReservationSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'hotel', 'check_in', 'check_out', 'total_price', 'status']
        extra_kwargs = {
            'user': {'read_only': True},
            'total_price': {'read_only': True},
            'status': {'read_only': True}
        }
