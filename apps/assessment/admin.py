from django.contrib import admin
from apps.assessment.models import Assessment, AssessmentType, Question, Answer, AssessmentResult

# Admin class for AssessmentType
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")

# Admin class for Question
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "created_at",
        "updated_at",
    )
    search_fields = ("text",)
    list_filter = ("created_at",)

# Admin class for Answer
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "text",
        "created_at",
        "updated_at",
    )
    search_fields = ("text", "question__text")
    list_filter = ("created_at",)

# Admin class for Assessment
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "practitioner",
        "assessment_type",
        "patient",
        "date",
        "final_score",
        "created_at",
        "updated_at",
    )
    search_fields = ("practitioner__username", "patient__username", "assessment_type__name")
    list_filter = ("assessment_type", "date", "practitioner", "patient")
    ordering = ("-date",)

# Admin class for AssessmentResult
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = (
        "assessment",
        "question",
        "answer",
        "created_at",
        "updated_at",
    )
    search_fields = ("assessment__id", "question__text", "answer__text")
    list_filter = ("created_at",)

# Register models with admin site
admin.site.register(AssessmentType, AssessmentTypeAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(AssessmentResult, AssessmentResultAdmin)
