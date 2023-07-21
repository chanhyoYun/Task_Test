from django.urls import path
from task import views

urlpatterns = [
    path("create/", views.TaskView.as_view(), name="task-create"),
    path("<int:task_id>/", views.TaskDetailView.as_view(), name="task-detail"),
    path(
        "<int:subtask_id>/complete/",
        views.SubTaskView.as_view(),
        name="subtask-complete",
    ),
]
