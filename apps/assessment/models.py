from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.utils.abstracts import AbstractUUID, TimeStampedModel

User = get_user_model()



class AssessmentType(AbstractUUID, TimeStampedModel):
    """Stores types of assessments (e.g., Cognitive Test, Physical Exam)"""
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"
    

class Question(AbstractUUID, TimeStampedModel):
    """Defines individual questions for assessments."""
    text = models.TextField()
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return f"Question: {self.text}"


class Answer(AbstractUUID, TimeStampedModel):
    """Represents possible answers to questions, with a boolean flag to denote the correct answer."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer: {self.text} (Correct: {self.is_correct})"


class Assessment(AbstractUUID, TimeStampedModel):
    """Represents an assessment instance, linking practitioners, patients, and types."""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_assessments")
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    final_score = models.IntegerField(default=0)  # This could be dynamically calculated based on results.

    def calculate_final_score(self):
        """Calculate the final score based on correct answers in AssessmentResult."""
        correct_answers = self.results.filter(answer__is_correct=True).count()
        total_questions = self.results.count()
        if total_questions == 0:
            return 0
        return int((correct_answers / total_questions) * 100)

    def save(self, *args, **kwargs):
        """Override save method to calculate final score before saving."""
        self.final_score = self.calculate_final_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assessment ({self.assessment_type}) by {self.practitioner} for {self.patient} on {self.date}"


class AssessmentResult(AbstractUUID, TimeStampedModel):
    """Stores the results for each question within an assessment."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="results")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f"Result: {self.assessment} - Question: {self.question}"

