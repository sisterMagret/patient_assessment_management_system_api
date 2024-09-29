from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from ..models import (
    AssessmentType,
    Question,
    Answer,
    Assessment,
    AssessmentResult,
)
from ..serializers import (
    AssessmentTypeSerializer,
    QuestionSerializer,
    AnswerSerializer,
    CreateAssessmentSerializer,
)


class AssessmentSerializerTests(TestCase):
    def setUp(self):
        """Create test data for the serializers."""
        self.assessment_type = AssessmentType.objects.create(
            name="Psychological Assessment",
            description="Assessment for psychological conditions.",
        )
        self.user = User.objects.create_user(
            first_name="Uncle",
            last_name="Rukus",
            phone_number="1234567890",
            email="sistermagret007@gmail.com",
            username="sistermagret007@gmail.com",
            password="password123",
            is_accept_terms_and_condition=True,
        )
        self.question = Question.objects.create(
            text="Do you feel anxious?",
            assessment_type=self.assessment_type,  # Ensure it's linked to the assessment type
        )
        self.answer = Answer.objects.create(
            question=self.question, text="Yes"
        )
        self.assessment_data = {
            "assessment_type": self.assessment_type.id,
            "patient": self.user.id,
            "date": "2024-09-29",
            "final_score": 85.0,
            "results": [
                {"question": self.question.id, "answer": self.answer.id}
            ],
        }

    # def test_assessment_type_serializer(self):
    #     """Test the AssessmentTypeSerializer."""
    #     serializer = AssessmentTypeSerializer(instance=self.assessment_type)
    #     self.assertEqual(
    #         serializer.data,
    #         {
    #             "id": str(self.assessment_type.id),
    #             "name": self.assessment_type.name,
    #             "description": self.assessment_type.description,
    #             "created_at": self.assessment_type.created_at,
    #             "updated_at": self.assessment_type.updated_at,
    #         },
    #     )

    # def test_question_serializer(self):
    #     """Test the QuestionSerializer."""
    #     serializer = QuestionSerializer(instance=self.question)
    #     self.assertEqual(
    #         serializer.data,
    #         {
    #             "id": str(self.question.id),
    #             "text": self.question.text,
    #         },
    #     )

    def test_answer_serializer(self):
        """Test the AnswerSerializer."""
        serializer = AnswerSerializer(instance=self.answer)
        self.assertEqual(
            serializer.data,
            {
                "id": str(self.answer.id),
                "is_correct": self.answer.is_correct,  # Ensure it's a string
                "text": self.answer.text,
            },
        )

    def test_create_assessment_serializer_valid(self):
        """Test CreateAssessmentSerializer with valid data."""
        serializer = CreateAssessmentSerializer(data=self.assessment_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['assessment_type'], self.assessment_type)
        self.assertEqual(serializer.validated_data['patient'], self.user)

    def test_create_assessment_serializer_invalid_question(self):
        """Test CreateAssessmentSerializer with an invalid question."""
        invalid_data = self.assessment_data.copy()
        invalid_data["results"] = [
            {"question": 999, "answer": self.answer.id}
        ]  # Invalid question ID
        serializer = CreateAssessmentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("results", serializer.errors)

    def test_create_assessment_serializer_invalid_answer(self):
        """Test CreateAssessmentSerializer with an invalid answer."""
        invalid_data = self.assessment_data.copy()
        invalid_data["results"] = [
            {"question": self.question.id, "answer": 999}
        ]  # Invalid answer ID
        serializer = CreateAssessmentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("results", serializer.errors)

    def tearDown(self):
        # Clean up any created instances if necessary
        User.objects.all().delete()
        AssessmentType.objects.all().delete()
        Question.objects.all().delete()
        Answer.objects.all().delete()
        Assessment.objects.all().delete()
        AssessmentResult.objects.all().delete()
