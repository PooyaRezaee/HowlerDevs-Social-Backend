from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema

from core import logger

from .models import User
from .services.user import create_user
from .validators import validate_password



class RegisterAPIView(APIView):
    class InputRegisterSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)
        password = serializers.CharField(
            validators=[validate_password]
        )

    class OutPutRegisterSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("username", "joined_at")

    @extend_schema(
        request=InputRegisterSerializer,
        responses={200: OutPutRegisterSerializer},
    )
    def post(self, request):
        srz = self.InputRegisterSerializer(data=request.data)
        srz.is_valid(raise_exception=True)

        try:
            username = srz.data["username"]
            password = srz.data["password"]
            user = create_user(username, password)
            return Response(
                self.OutPutRegisterSerializer(
                    user,
                ).data
            )
        except Exception as e:
            logger.error(f"Error in register user {e}")
            return Response(
                {"detail": "Internal Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
