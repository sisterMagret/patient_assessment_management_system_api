from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.utils.abstracts import AbstractUUID


class AssessmentType(AbstractUUID):
    """Model to represent different types of assessments"""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Question(AbstractUUID):
    """Model to represent individual questions in assessments."""

    text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Answer(AbstractUUID):
    """Model to represent answers to assessment questions."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to: {self.question}"


class Assessment(AbstractUUID):
    """Model to represent an assessment instance."""

    practitioner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE
    )
    assessment_type = models.ForeignKey(
        AssessmentType,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    patient = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    date = models.DateField(default=timezone.now)
    final_score = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Assessment for {self.patient} on {self.date}"


class AssessmentResult(AbstractUUID):
    """Model to store the relationship between assessment questions and answers."""

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="results"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assessment} - {self.question}"
