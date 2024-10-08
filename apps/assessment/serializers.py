from rest_framework import serializers
from .models import Assessment, AssessmentType, Question, Answer, AssessmentResult


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['id']  # Assuming id should not be modified

    def validate(self, attrs):
        """Ensure only one answer can be marked as correct per question."""
        question_id = self.initial_data.get('question')
        if attrs.get('is_correct'):
            if Answer.objects.filter(question_id=question_id, is_correct=True).exists():
                raise serializers.ValidationError("Only one answer can be marked as correct.")
        return attrs


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']


class AssessmentResultSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    answer = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all())

    class Meta:
        model = AssessmentResult
        fields = ['question', 'answer']

    def validate(self, data):
        """
        Validate that the provided answer belongs to the question.
        """
        question = data.get('question')
        answer = data.get('answer')
        if answer.question != question:
            raise serializers.ValidationError("The answer does not belong to the provided question.")
        return data


class CreateAssessmentSerializer(serializers.ModelSerializer):
    results = AssessmentResultSerializer(many=True)

    class Meta:
        model = Assessment
        fields = ['assessment_type', 'patient', 'results']
        read_only_fields = ['id', 'patient']

    def create(self, validated_data):
        results_data = validated_data.pop('results', [])
        assessment = Assessment.objects.create(**validated_data)
        self._handle_results(assessment, results_data)
        return assessment

    def update(self, instance, validated_data):
        results_data = validated_data.pop('results', [])
        instance.assessment_type = validated_data.get('assessment_type', instance.assessment_type)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.save()

        # Update results by clearing old ones and creating new ones
        instance.results.all().delete()
        self._handle_results(instance, results_data)

        return instance

    def _handle_results(self, assessment, results_data):
        """
        Handle the creation of AssessmentResult and calculation of the final score.
        """
        results = []
        total_score = 0

        for result_data in results_data:
            question = result_data.get('question')
            answer = result_data.get('answer')

            # Check if the answer is correct and accumulate the score
            if answer.is_correct:
                total_score += 2  # Assume 2 points per correct answer

            results.append(
                AssessmentResult(
                    assessment=assessment,
                    question=question,
                    answer=answer
                )
            )

        # Bulk create the results to reduce the number of database hits
        AssessmentResult.objects.bulk_create(results)

        # Update the final score and save the assessment
        assessment.final_score = total_score
        assessment.save()


class AssessmentSerializer(serializers.ModelSerializer):
    results = AssessmentResultSerializer(many=True, read_only=True)
    assessment_type = serializers.StringRelatedField()
    patient = serializers.StringRelatedField()

    class Meta:
        model = Assessment
        fields = ['id', 'assessment_type', 'patient', 'final_score', 'results', 'date']


class AssessmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentType  
        fields = '__all__'  
