from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import (
    AssessmentType,
    Question,
    Answer,
    Assessment,
    AssessmentResult,
)

User = get_user_model()


class AssessmentModelsTests(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            **{
                "first_name": "Uncle",
                "last_name": "Rukus",
                "phone_number": "1234567890",
                "email": "sistermagret007@gmail.com",
                "username": "sistermagret007@gmail.com",
                "password": "password123",
                "is_accept_terms_and_condition": True,
            }
        )

        # Create an AssessmentType instance
        self.assessment_type = AssessmentType.objects.create(
            name="Mental Health Assessment",
            description="A detailed assessment of mental health.",
        )

        # Create a Question instance
        self.question = Question.objects.create(
            text="How do you feel today?"
        )

        # Create an Answer instance
        self.answer = Answer.objects.create(
            question=self.question, text="I feel good."
        )

        # Create an Assessment instance
        self.assessment = Assessment.objects.create(
            practitioner=self.user,
            assessment_type=self.assessment_type,
            patient=self.user,  # Using the same user for testing purposes
            date="2024-09-29",
            final_score=90.0,
        )

    def test_assessment_type_str(self):
        """Test the string representation of AssessmentType."""
        self.assertEqual(
            str(self.assessment_type), "Mental Health Assessment"
        )

    def test_question_str(self):
        """Test the string representation of Question."""
        self.assertEqual(str(self.question), "How do you feel today?")

    def test_answer_str(self):
        """Test the string representation of Answer."""
        self.assertEqual(
            str(self.answer), "Answer to: How do you feel today?"
        )

    def test_assessment_str(self):
        """Test the string representation of Assessment."""
        self.assertEqual(
            str(self.assessment),
            f"Assessment for {self.user} on 2024-09-29",
        )

    def test_assessment_result_creation(self):
        """Test creating an AssessmentResult instance."""
        result = AssessmentResult.objects.create(
            assessment=self.assessment,
            question=self.question,
            answer=self.answer,
        )
        self.assertEqual(result.assessment, self.assessment)
        self.assertEqual(result.question, self.question)
        self.assertEqual(result.answer, self.answer)

    def test_assessment_result_str(self):
        """Test the string representation of AssessmentResult."""
        result = AssessmentResult.objects.create(
            assessment=self.assessment,
            question=self.question,
            answer=self.answer,
        )
        self.assertEqual(
            str(result), f"{self.assessment} - {self.question}"
        )

    def tearDown(self):
        # Clean up any created instances if necessary
        AssessmentType.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        Assessment.objects.all().delete()
        AssessmentResult.objects.all().delete()
        User.objects.all().delete()
