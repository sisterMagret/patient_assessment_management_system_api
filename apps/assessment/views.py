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
from apps.utils.permissions import (
    patient_access_only,
    practitioner_access_only,
)


class AssessmentViewSet(BaseViewSet):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()

    def get_queryset(self):
        return self.queryset

    def get_object(self):
        return get_object_or_404(Assessment, pk=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_summary="List all assessments",
        operation_description="Retrieve a paginated list of assessments for a patient.",
        responses={
            200: openapi.Response(
                "Success", AssessmentSerializer(many=True)
            )
        },
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_queryset().filter(
                    Q(patient=self.request.user)
                    | Q(practitioner=self.request.user)
                ),
                serializer_class=self.serializer_class,
            )
            context.update({"data": paginate})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="Retrieve assessment details",
        operation_description="Retrieve a specific assessment by ID.",
        responses={200: openapi.Response("Success", AssessmentSerializer)},
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def retrieve(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance = self.get_object()
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=CreateAssessmentSerializer,
        operation_summary="Create a new assessment",
        operation_description="Create a new assessment for a patient with associated questions and answers.",
        responses={201: openapi.Response("Created", AssessmentSerializer)},
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def create(self, request, *args, **kwargs):
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = CreateAssessmentSerializer(data=data)
            if serializer.is_valid():
                assessment = serializer.save()
                assessment.practitioner = request.user
                assessment.save()
                context.update(
                    {
                        "data": self.serializer_class(assessment).data,
                        "message": "Assessment created successfully",
                    }
                )
            else:
                context.update(
                    {
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=CreateAssessmentSerializer,
        operation_summary="Update an assessment",
        operation_description="Update an existing assessment by providing new data.",
        responses={200: openapi.Response("Success", AssessmentSerializer)},
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def update(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance = self.get_object()
            data = self.get_data(request)
            serializer = CreateAssessmentSerializer(
                instance, data=data, partial=True
            )
            if serializer.is_valid():
                assessment = serializer.save()
                context.update(
                    {
                        "data": self.serializer_class(assessment).data,
                        "message": "Assessment updated successfully",
                    }
                )
            else:
                context.update(
                    {
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(operation_summary="Delete an assessment")
    @method_decorator(practitioner_access_only(), name="dispatch")
    def destroy(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.delete()
            context.update({"message": "Assessment deleted successfully"})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="List assessment questions",
        operation_description="List the questions and answers for a given assessment.",
        responses={
            200: openapi.Response("Success", QuestionSerializer(many=True))
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="questions",
        description="List all questions in an assessment",
    )
    def list_questions(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            assessment = self.get_object()
            questions = Question.objects.filter(assessment=assessment)
            context.update(
                {"data": QuestionSerializer(questions, many=True).data}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=QuestionSerializer,
        operation_summary="Add a question to an assessment",
        operation_description="Add a new question to an existing assessment.",
        responses={201: openapi.Response("Created", QuestionSerializer)},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="questions",
        description="Add a question to the assessment",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def add_question(self, request, *args, **kwargs):
        context = {"status": status.HTTP_201_CREATED}
        try:
            assessment = self.get_object()
            data = self.get_data(request)
            data["assessment"] = assessment.id
            serializer = QuestionSerializer(data=data)
            if serializer.is_valid():
                question = serializer.save()
                context.update(
                    {
                        "data": serializer.data,
                        "message": "Question added successfully",
                    }
                )
            else:
                context.update(
                    {
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="List all assessment types",
        operation_description="Retrieve a list of available assessment types.",
        responses={
            200: openapi.Response(
                "Success", AssessmentTypeSerializer(many=True)
            )
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="types",
        description="List all assessment types",
    )
    def list_assessment_types(self, request, *args, **kwargs):
        """List all available assessment types"""
        context = {"status": status.HTTP_200_OK}
        try:
            assessment_types = AssessmentType.objects.all()
            context.update(
                {
                    "data": AssessmentTypeSerializer(
                        assessment_types, many=True
                    ).data
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AssessmentTypeSerializer,
        operation_summary="Create a new assessment type",
        operation_description="Create a new type of assessment.",
        responses={
            201: openapi.Response("Created", AssessmentTypeSerializer)
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="types",
        description="Create a new assessment type",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def create_assessment_type(self, request, *args, **kwargs):
        """Create a new assessment type"""
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = request.data
            serializer = AssessmentTypeSerializer(data=data)
            if serializer.is_valid():
                assessment_type = serializer.save()
                context.update(
                    {
                        "data": serializer.data,
                        "message": "Assessment type created successfully",
                    }
                )
            else:
                context.update(
                    {
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="Delete an assessment type",
        operation_description="Delete an assessment type by ID.",
        responses={204: "No Content"},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="types/(?P<type_id>[^/.]+)",
        description="Delete an assessment type",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def delete_assessment_type(
        self, request, type_id=None, *args, **kwargs
    ):
        """Delete an assessment type"""
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            assessment_type = AssessmentType.objects.get(id=type_id)
            assessment_type.delete()
            context.update(
                {"message": "Assessment type deleted successfully"}
            )
        except AssessmentType.DoesNotExist:
            context.update(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Assessment type not found",
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AssessmentTypeSerializer,
        operation_summary="Update an assessment type",
        operation_description="Update an existing assessment type by ID.",
        responses={
            200: openapi.Response("Success", AssessmentTypeSerializer)
        },
    )
    @action(
        detail=True,
        methods=["put"],
        url_path="types/(?P<type_id>[^/.]+)",
        description="Update an assessment type",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def update_assessment_type(
        self, request, type_id=None, *args, **kwargs
    ):
        """Update an existing assessment type"""
        context = {"status": status.HTTP_200_OK}
        try:
            assessment_type = AssessmentType.objects.get(id=type_id)
            serializer = AssessmentTypeSerializer(
                assessment_type, data=request.data, partial=True
            )
            if serializer.is_valid():
                assessment_type = serializer.save()
                context.update(
                    {
                        "data": serializer.data,
                        "message": "Assessment type updated successfully",
                    }
                )
            else:
                context.update(
                    {
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except AssessmentType.DoesNotExist:
            context.update(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Assessment type not found",
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="List questions and answers for an assessment",
        operation_description="Retrieve the list of questions and their answers for a specific assessment.",
        responses={
            200: openapi.Response("Success", QuestionSerializer(many=True))
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="questions-and-answers",
        description="List all questions and answers for an assessment",
    )
    def list_questions_and_answers(self, request, *args, **kwargs):
        """List all questions and answers for the assessment"""
        context = {"status": status.HTTP_200_OK}
        try:
            assessment = self.get_object()
            questions = Question.objects.filter(assessment=assessment)
            data = []
            for question in questions:
                question_data = QuestionSerializer(question).data
                answer = Answer.objects.filter(question=question).first()
                if answer:
                    question_data["answer"] = AnswerSerializer(answer).data
                else:
                    question_data["answer"] = None
                data.append(question_data)
            context.update({"data": data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AnswerSerializer,
        operation_summary="Submit an answer to a question",
        operation_description="Submit an answer for a specific question within an assessment.",
        responses={201: openapi.Response("Created", AnswerSerializer)},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="questions/(?P<question_id>[^/.]+)/answer",
        description="Submit an answer for a question",
    )
    def submit_answer(self, request, question_id=None, *args, **kwargs):
        """Submit an answer to a question"""
        context = {"status": status.HTTP_201_CREATED}
        try:
            question = Question.objects.get(id=question_id)
            data = request.data
            data["question"] = question.id
            serializer = AnswerSerializer(data=data)
            if serializer.is_valid():
                answer = serializer.save()
                context.update(
                    {
                        "data": serializer.data,
                        "message": "Answer submitted successfully",
                    }
                )
            else:
                context.update(
                    {
                        "errors": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Question.DoesNotExist:
            context.update(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Question not found",
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=AnswerSerializer,
        operation_summary="Update an answer to a question",
        operation_description="Update an existing answer for a specific question within an assessment.",
        responses={200: openapi.Response("Success", AnswerSerializer)},
    )
    @action(
        detail=True,
        methods=["put"],
        url_path="questions/(?P<question_id>[^/.]+)/answer",
        description="Update an answer for a question",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def update_answer(self, request, question_id=None, *args, **kwargs):
        """Update an existing answer for a question"""
        context = {"status": status.HTTP_200_OK}
        try:
            question = Question.objects.get(id=question_id)
            answer = Answer.objects.filter(question=question).first()
            if not answer:
                context.update(
                    {
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "Answer not found",
                    }
                )
            else:
                serializer = AnswerSerializer(
                    answer, data=request.data, partial=True
                )
                if serializer.is_valid():
                    answer = serializer.save()
                    context.update(
                        {
                            "data": serializer.data,
                            "message": "Answer updated successfully",
                        }
                    )
                else:
                    context.update(
                        {
                            "errors": serializer.errors,
                            "status": status.HTTP_400_BAD_REQUEST,
                        }
                    )
        except Question.DoesNotExist:
            context.update(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Question not found",
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    # Create a new question and answer for an assessment
    @swagger_auto_schema(
        method="post",
        request_body=QuestionSerializer,
        operation_summary="Create a new question and answer",
        operation_description="Create a new question and answer for an assessment.",
        responses={201: openapi.Response("Created", QuestionSerializer)},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="questions",
        description="Create a new question in an assessment",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def create_question(self, request, *args, **kwargs):
        assessment = self.get_object()
        data = self.get_data(request)
        data["assessment"] = assessment.id
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    # Update a question in an assessment
    @swagger_auto_schema(
        method="put",
        request_body=QuestionSerializer,
        operation_summary="Update a question and answer",
        operation_description="Update an existing question and answer for an assessment.",
        responses={200: openapi.Response("Success", QuestionSerializer)},
    )
    @action(
        detail=True,
        methods=["put"],
        url_path="questions/(?P<question_id>[^/.]+)",
        description="Update a question",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def update_question(self, request, question_id=None, *args, **kwargs):
        try:
            question = Question.objects.get(
                id=question_id, assessment=self.get_object()
            )
            serializer = QuestionSerializer(
                question, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except Question.DoesNotExist:
            return Response(
                {"detail": "Question not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # Delete a question in an assessment
    @swagger_auto_schema(
        operation_summary="Delete a question",
        operation_description="Delete a question and its answer from an assessment.",
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="questions/(?P<question_id>[^/.]+)",
        description="Delete a question",
    )
    @method_decorator(practitioner_access_only(), name="dispatch")
    def delete_question(self, request, question_id=None, *args, **kwargs):
        try:
            question = Question.objects.get(
                id=question_id, assessment=self.get_object()
            )
            question.delete()
            return Response(
                {"detail": "Question deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Question.DoesNotExist:
            return Response(
                {"detail": "Question not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
