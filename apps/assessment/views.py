import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator
from apps.utils.base import BaseViewSet
from .serializers import (
    AnswerSerializer,
    AssessmentSerializer,
    AssessmentTypeSerializer,
    CreateAssessmentSerializer,
    QuestionSerializer,
)
from .models import Answer, Assessment, AssessmentType, Question
from apps.utils.permissions import practitioner_access_only


logger = logging.getLogger("assessment")


class AssessmentViewSet(BaseViewSet):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()

    def get_queryset(self):
        """Override to filter assessments for the current user."""
        # Ensure user is authenticated before filtering
        if self.request.user.is_authenticated:
            return self.queryset.filter(
            Q(patient=self.request.user) | Q(practitioner=self.request.user)
        )
        else:
            # Return an empty queryset or handle appropriately
            return Assessment.objects.none() 
        

    def get_object(self):
        """Get the assessment object based on the URL parameter."""
        return get_object_or_404(Assessment, pk=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_summary="List all assessments",
        operation_description="Retrieve a paginated list of assessments for a patient.",
        responses={200: openapi.Response("Success", AssessmentSerializer(many=True))}
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def list(self, request, *args, **kwargs):
        """List all assessments for the authenticated user."""
        context = {}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_queryset(),
                serializer_class=self.serializer_class,
            )
            context.update({"status": status.HTTP_200_OK, "data": paginate})
            logger.info(f"List assessments: {request.user} retrieved {self.get_queryset().count()} assessments.")
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="Retrieve assessment details",
        operation_description="Retrieve a specific assessment by ID.",
        responses={200: openapi.Response("Success", AssessmentSerializer)},
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific assessment."""
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        logger.info(f"Retrieve assessment: {request.user} accessed assessment {instance.id}.")
        return Response({"status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CreateAssessmentSerializer,
        operation_summary="Create a new assessment",
        operation_description="Create a new assessment for a patient with associated questions and answers.",
        responses={201: openapi.Response("Created", AssessmentSerializer)},
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def create(self, request, *args, **kwargs):
        """Create a new assessment."""
        serializer = CreateAssessmentSerializer(data=request.data)
        if serializer.is_valid():
            assessment = serializer.save(practitioner=request.user)
            logger.info(f"Create assessment: {request.user} created assessment {assessment.id}.")
            return Response(
                {"status": status.HTTP_201_CREATED, "data": self.serializer_class(assessment).data, "message": "Assessment created successfully"},
                status=status.HTTP_201_CREATED,
            )
        logger.error(f"Create assessment failed: {request.user} attempted to create an assessment with invalid data: {serializer.errors}.")
        return Response({"errors": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CreateAssessmentSerializer,
        operation_summary="Update an assessment",
        operation_description="Update an existing assessment by providing new data.",
        responses={200: openapi.Response("Success", AssessmentSerializer)},
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def update(self, request, *args, **kwargs):
        """Update an existing assessment."""
        instance = self.get_object()
        serializer = CreateAssessmentSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            assessment = serializer.save()
            logger.info(f"Update assessment: {request.user} updated assessment {assessment.id}.")
            return Response({"status": status.HTTP_200_OK, "data": self.serializer_class(assessment).data, "message": "Assessment updated successfully"}, status=status.HTTP_200_OK)
        logger.error(f"Update assessment failed: {request.user} attempted to update assessment {instance.id} with invalid data: {serializer.errors}.")
        return Response({"errors": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_summary="Delete an assessment")
    @method_decorator(practitioner_access_only(), name="dispatch")
    def destroy(self, request, *args, **kwargs):
        """Delete an assessment."""
        instance = self.get_object()
        instance.delete()
        logger.info(f"Delete assessment: {request.user} deleted assessment {instance.id}.")
        return Response({"status": status.HTTP_204_NO_CONTENT, "message": "Assessment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="List assessment questions",
        operation_description="List the questions for a given assessment.",
        responses={200: openapi.Response("Success", QuestionSerializer(many=True))}
    )
    @action(detail=True, methods=["get"], url_path="questions", description="List all questions in an assessment")
    def list_questions(self, request, *args, **kwargs):
        """List all questions for a specific assessment."""
        assessment = self.get_object()
        
        # Assuming each question is linked to an AssessmentType
        questions = Question.objects.filter(assessment_type=assessment.assessment_type)
        
        serializer = QuestionSerializer(questions, many=True)
        logger.info(f"List questions: {request.user} retrieved questions for assessment {assessment.id}.")
        return Response({"status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=QuestionSerializer,
        operation_summary="Add a question to an assessment",
        operation_description="Add a new question to an existing assessment.",
        responses={201: openapi.Response("Created", QuestionSerializer)},
    )
    @action(detail=True, methods=["post"], url_path="questions", description="Add a question to the assessment")
    @method_decorator(practitioner_access_only(), name="dispatch")
    def add_question(self, request, *args, **kwargs):
        """Add a question to a specific assessment."""
        assessment = self.get_object()
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            logger.info(f"Add question: {request.user} added question {question.id} to assessment {assessment.id}.")
            return Response({"status": status.HTTP_201_CREATED, "data": serializer.data, "message": "Question added successfully"}, status=status.HTTP_201_CREATED)
        logger.error(f"Add question failed: {request.user} attempted to add a question to assessment {assessment.id} with invalid data: {serializer.errors}.")
        return Response({"errors": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="List all assessment types",
        operation_description="Retrieve a list of available assessment types.",
        responses={200: openapi.Response("Success", AssessmentTypeSerializer(many=True))}
    )
    @action(detail=False, methods=["get"], url_path="types", description="List all assessment types")
    def list_assessment_types(self, request, *args, **kwargs):
        """List all assessment types."""
        assessment_types = AssessmentType.objects.all()
        serializer = AssessmentTypeSerializer(assessment_types, many=True)
        logger.info(f"List assessment types: {request.user} retrieved all assessment types.")
        return Response({"status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AssessmentTypeSerializer,
        operation_summary="Create a new assessment type",
        operation_description="Create a new type of assessment.",
        responses={201: openapi.Response("Created", AssessmentTypeSerializer)},
    )
    @action(detail=False, methods=["post"], url_path="types", description="Create a new assessment type")
    @method_decorator(practitioner_access_only(), name="dispatch")
    def create_assessment_type(self, request, *args, **kwargs):
        """Create a new assessment type."""
        serializer = AssessmentTypeSerializer(data=request.data)
        if serializer.is_valid():
            assessment_type = serializer.save()
            logger.info(f"Create assessment type: {request.user} created assessment type {assessment_type.id}.")
            return Response({"status": status.HTTP_201_CREATED, "data": serializer.data, "message": "Assessment type created successfully"}, status=status.HTTP_201_CREATED)
        logger.error(f"Create assessment type failed: {request.user} attempted to create assessment type with invalid data: {serializer.errors}.")
        return Response({"errors": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete an assessment type",
        operation_description="Delete an assessment type by ID.",
        responses={204: "No Content"}
    )
    @action(detail=True, methods=["delete"], url_path="types", description="Delete an assessment type")
    @method_decorator(practitioner_access_only(), name="dispatch")
    def delete_assessment_type(self, request, *args, **kwargs):
        """Delete an assessment type."""
        assessment_type = get_object_or_404(AssessmentType, pk=kwargs["pk"])
        assessment_type.delete()
        logger.info(f"Delete assessment type: {request.user} deleted assessment type {assessment_type.id}.")
        return Response({"status": status.HTTP_204_NO_CONTENT, "message": "Assessment type deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
