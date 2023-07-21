from rest_framework.test import APITestCase
from django.urls import reverse
from team.models import User

"""테스트 요약
    
1. 회원가입 테스트
2. 토큰 로그인
3. 토큰 리프레쉬
"""


class UserBaseTestCase(APITestCase):
    """유저기능 테스트 셋업

    유저기능 테스트 셋업입니다.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_signup_data = {
            "username": "admin",
            "password": "ajdcjddl",
            "email": "admin@gmail.com",
        }
        cls.set_up_user = User.objects.create_user(
            email="testuser@gmail.com",
            password="ajdcjddl",
        )
        cls.user_edit_data = {"username": "testuser"}
        cls.user_login_data = {"email": "testuser@gmail.com", "password": "ajdcjddl"}

    def setUp(self) -> None:
        login_user = self.client.post(reverse("login"), self.user_login_data).data
        self.access = login_user["access"]
        self.refresh = login_user["refresh"]


class UserSignUpTestCase(UserBaseTestCase):
    """유저 회원가입 테스트

    UserView에 회원가입 기능을 테스트합니다.
    """

    def test_signup(self):
        """1. 회원가입

        회원가입 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        url = reverse("signup")
        data = self.user_signup_data
        response = self.client.post(
            path=url,
            data=data,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"message": "회원가입 완료"})
        self.assertTrue(User.objects.get(email=data["email"]))


class UserTokenTestCase(UserBaseTestCase):
    """토큰 로그인 및 갱신 테스트

    TokenObtainPairView, TokenRefreshView의
    토큰 로그인 기능, 토큰 리프레쉬 기능을 테스트합니다.
    """

    def test_login(self):
        """2. 토큰 로그인

        토큰 로그인 정상동작 테스트입니다.
        스테이터스 코드, 결과 여부를 검사합니다.
        """
        url = reverse("login")
        data = self.user_login_data
        response = self.client.post(
            path=url,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_token_refresh(self):
        """3. 토큰 리프레쉬

        토큰 리프레쉬 정상동작 테스트입니다.
        스테이터스 코드, 결과 여부를 검사합니다.
        """
        url = reverse("token_refresh")
        data = {"refresh": self.refresh}
        response = self.client.post(
            path=url,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
