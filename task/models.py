from django.db import models
from team.models import User, Team
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver


class Task(models.Model):
    """업무 모델

    Args:
        id (AutoField): 고유 아이디(pk)
        create_user (ForeignKey): Task 생성자
        team (ManyToManyField): Task 할당 팀
        title (CharField): Task 제목
        content (TextField): Task 내용
        is_complete (BooleanField): 완료 여부
        completed_date (DateTimeField): 완료된 시간
        created_at (DateTimeField): Task 생성 시간
        modified_at (DateTimeField): Task 수정 시간
    """

    id = models.AutoField(primary_key=True)
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ManyToManyField(Team)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)


class SubTask(models.Model):
    """하위업무 모델

    Args:
        id (AutoField): 고유 아이디(pk)
        team (ManyToManyField): SubTask 할당 팀
        is_complete (BooleanField): 완료 여부
        completed_date (DateTimeField): 완료된 시간
        created_at (DateTimeField): SubTask 생성 시간
        modified_at (DateTimeField): SubTask 수정 시간
    """

    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name="subtasks", on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team} - {self.task.title}"


@receiver(m2m_changed, sender=Task.team.through)
def update_subtasks(sender, instance, action, reverse, pk_set, **kwargs):
    """수정(저장, 삭제)시 처리 데코레이터

    Task 수정시 할당되어 있는 SubTask 처리를 위한 함수
    ManyToMany 필드 추가, 삭제 시에 실행
    """
    if action == "pre_clear":
        SubTask.objects.filter(task=instance, is_complete=False).delete()
        return

    if action in ["pre_add", "pre_remove"]:
        current_teams = set(instance.team.values_list("pk", flat=True))
        added_teams = set(pk_set) if not reverse else set()
        removed_teams = set(pk_set) if reverse else set()

        if reverse:
            final_teams = current_teams - removed_teams
        else:
            final_teams = current_teams | added_teams

        SubTask.objects.filter(
            task=instance, team__in=(current_teams - final_teams), is_complete=False
        ).delete()

        for team_pk in final_teams - current_teams:
            team = Team.objects.get(pk=team_pk)
            SubTask.objects.get_or_create(team=team, task=instance)

        if action == "pre_remove":
            SubTask.objects.filter(
                task=instance, team__in=added_teams, is_complete=False
            ).delete()


@receiver(post_save, sender=SubTask)
def complete_parent_task(sender, instance, **kwargs):
    """업무 완료 데코레이터

    post_save시 SubTask 모두 완료되었을 때, Task 완료되는 함수
    """
    if instance.task and instance.task.subtasks.exists():
        all_subtasks_completed = (
            instance.task.subtasks.filter(is_complete=False).count() == 0
        )
        if all_subtasks_completed:
            instance.task.is_complete = True
            instance.task.completed_date = instance.completed_date
            instance.task.save()
