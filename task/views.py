from django.db.models import Q
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import TaskSerializer
from .models import Task, SubTask


class TaskView(APIView):
    """업무 뷰

    업무(Task) 작성 뷰
    """

    def post(self, request):
        """업무 작성

        Args:
            request: title, content, team 입력

        Returns:
            정상 201: 업무(Task) 생성
            오류 400: 유효하지 않은 값
        """
        data = request.data.copy()
        data["create_user"] = request.user.id
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    """업무 상세 뷰


    업무(Task) 조회 및 수정 뷰
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        """업무 조회

        Args:
            task_id: 업무(Task) 아이디

        Returns:
            정상 200: 조회된 값 반환
        """
        if request.user.team != None:
            user_team_id = request.user.team.id

            tasks = Task.objects.filter(
                Q(team=user_team_id) | Q(subtasks__team=user_team_id) | Q(pk=task_id)
            ).distinct()
        else:
            tasks = Task.objects.filter(Q(subtasks__id=task_id)).distinct()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, task_id):
        """업무 수정

        Args:
            request: title, content, team 값 입력 받음
            task_id: 업무(Task) 아이디

        Returns:
            정상 200: 업무 수정(title, team, content)
            오류 400: 유효하지 않은 값
        """
        task = get_object_or_404(Task, pk=task_id)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsSubTaskOwner(BasePermission):
    """하위업무 관리

    같은 팀만 처리할 수 있도록 작성
    """

    def has_object_permission(self, request, view, obj):
        return request.user.team == obj.team


class SubTaskView(APIView):
    """하위업무 뷰

    하위업무(SubTask) 관리 뷰
    """

    permission_classes = [IsSubTaskOwner]

    def patch(self, request, subtask_id):
        """하위업무 완료처리

        Args:
            subtask_id: 하위업무 고유 아이디

        Returns:
            정상 200: "하위업무 완료취소." 메세지 반환
            정상 200: "하위업무 완료처리." 메세지 반환
        """
        subtask = get_object_or_404(SubTask, pk=subtask_id)

        if subtask.is_complete:
            subtask.is_complete = False
            subtask.save()
            return Response({"message": "하위업무 완료취소."}, status=status.HTTP_200_OK)
        else:
            subtask.is_complete = True
            subtask.save()
            return Response({"message": "하위업무 완료처리."}, status=status.HTTP_200_OK)
