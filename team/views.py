from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from team.serializers import UserSerializer


class UserView(APIView):
    """유저 뷰

    회원 가입 처리
    """

    def post(self, request):
        """회원가입

        Args:
            request: email, password, username 입력 받음

        Returns:
            정상 201: "회원가입 완료" 메세지 반환
            오류 400: 유효하지 않은 정보
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
