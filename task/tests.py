from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from team.models import User, Team
from task.models import Task, SubTask

"""테스트 요약

1. 업무(Task) 생성
2. 업무(Task) 수정
3. 하위업무(SubTask) 완료처리
4. 하위업무(SubTask) 완료취소
"""


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@a.com", password="testpassword"
        )
        self.team1 = Team.objects.create(team_name="Team 1")
        self.team2 = Team.objects.create(team_name="Team 2")
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        """1. 업무(Task) 생성

        업무생성 정상동작 테스트입니다.
        스테이터스 코드, DB값을 검사합니다.
        """
        url = reverse("task-create")
        data = {
            "title": "테스트 업무",
            "content": "테스트 업무 작성",
            "create_user": 1,
            "team": [1, 2],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.get(pk=response.data["id"])
        self.assertEqual(task.create_user, self.user)
        self.assertEqual(task.title, "테스트 업무")
        self.assertEqual(task.content, "테스트 업무 작성")
        self.assertListEqual(list(task.team.values_list("id", flat=True)), [1, 2])

    def test_update_task(self):
        """2. 업무(Task) 수정

        업무 수정 정상동작 테스트입니다.
        스테이터스 코드, DB값을 검사합니다.
        """
        task = Task.objects.create(
            title="테스트 업무", content="테스트 업무 작성", create_user=self.user
        )
        url = reverse("task-detail", args=[task.id])
        data = {"title": "업무 수정", "content": "업무 수정 완료"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "업무 수정")
        self.assertEqual(task.content, "업무 수정 완료")


class SubTaskViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@a.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.team = Team.objects.create(team_name="Test Team")
        self.task = Task.objects.create(
            title="Test Task", content="This is a test task.", create_user=self.user
        )
        self.subtask = SubTask.objects.create(task=self.task, team=self.team)

    def test_complete_subtask(self):
        """3. 하위업무(SubTask) 완료처리

        하위업무 완료처리 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        url = reverse("subtask-complete", args=[self.subtask.id])
        data = {
            "is_complete": True,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "하위업무 완료처리.")
        self.subtask.refresh_from_db()
        self.assertTrue(self.subtask.is_complete)

    def test_complete_subtask_already_completed(self):
        """4. 하위업무(SubTask) 완료취소

        하위업무 완료취소 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        self.subtask.is_complete = True
        self.subtask.save()
        url = reverse("subtask-complete", args=[self.subtask.id])
        data = {
            "is_complete": True,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "하위업무 완료취소.")
