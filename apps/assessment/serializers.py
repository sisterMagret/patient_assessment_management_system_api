from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.users.serializer import UserMiniSerializer
from .models import (
    AssessmentType,
    Question,
    Answer,
    Assessment,
    AssessmentResult,
)


class AssessmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentType model."""

    class Meta:
        model = AssessmentType
        fields = ["id", "name", "description"]


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""

    class Meta:
        model = Question
        fields = ["id", "text"]


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model."""

    class Meta:
        model = Answer
        fields = ["id", "question", "text"]


class QuestionAndAnswerSerializer(serializers.Serializer):
    """Serializer for question and answer pairs in Assessment results."""

    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), required=True
    )
    answer = serializers.PrimaryKeyRelatedField(
        queryset=Answer.objects.all(), required=False
    )


class AssessmentResultSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentResult model, showing related questions and answers."""

    question = QuestionSerializer(read_only=True)
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = AssessmentResult
        fields = ["id", "assessment", "question", "answer"]


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model, including related patient and results."""

    patient = UserMiniSerializer(read_only=True)
    assessment_type = AssessmentTypeSerializer(read_only=True)
    results = AssessmentResultSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id",
            "assessment_type",
            "patient",
            "date",
            "final_score",
            "results",
        ]


class CreateAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for creating an Assessment with associated results."""

    results = QuestionAndAnswerSerializer(many=True, required=False)

    class Meta:
        model = Assessment
        fields = [
            "assessment_type",
            "patient",
            "date",
            "final_score",
            "results",
        ]

    def create(self, validated_data):
        results_data = validated_data.pop("results", [])
        assessment = Assessment.objects.create(**validated_data)

        for result in results_data:
            question = get_object_or_404(Question, pk=result["question"])
            answer = get_object_or_404(Answer, pk=result.get("answer"))
            AssessmentResult.objects.create(
                assessment=assessment, question=question, answer=answer
            )

        return assessment

    def update(self, instance, validated_data):
        """Method to update an assessment and its associated results."""
        results_data = validated_data.pop("results", None)
        instance.final_score = validated_data.get(
            "final_score", instance.final_score
        )
        instance.save()

        if results_data is not None:
            AssessmentResult.objects.filter(assessment=instance).delete()
            for result in results_data:
                question = get_object_or_404(
                    Question, pk=result["question"]
                )
                answer = get_object_or_404(Answer, pk=result.get("answer"))
                AssessmentResult.objects.create(
                    assessment=instance, question=question, answer=answer
                )

        return instance
