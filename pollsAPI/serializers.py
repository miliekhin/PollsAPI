from rest_framework import serializers
from .models import Poll, Question, AnswerText, AnswerSingle, AnswerMulti, AnswerVariants
from django.utils import timezone
from config.utils import QA_TYPE_TEXT, QA_TYPE_MULTI, QA_TYPE_SINGLE


def is_question_was_answered(question, user):
    """ Отвечал ли пользователь уже на этот вопрос любым из типов ответа"""
    answered_questions = (
        AnswerSingle.objects.filter(question=question, user=user).exists(),
        AnswerMulti.objects.filter(question=question, user=user).exists(),
        AnswerText.objects.filter(question=question, user=user).exists(),
    )
    if any(answered_questions):
        raise serializers.ValidationError({"error": "Нельзя два раза ответить на вопрос."})


def is_answer_type_valid(answer_type, data):
    """ Совпадают ли тип вопроса и ответа """
    try:
        question_type = Question.objects.get(id=data['question'].id).type
    except Exception as e:
        raise serializers.ValidationError(str(e))

    if question_type != answer_type:
        raise serializers.ValidationError(f'Тип ответа {answer_type} не совпадает с типом вопроса {question_type}')


class PollSerializer(serializers.ModelSerializer):
    """Сериализация опроса"""

    class Meta:
        model = Poll
        fields = '__all__'

    def validate_end_date(self, value):
        """ Время окончания опроса не должно быть меньше текущего """
        if timezone.now() > value:
            raise serializers.ValidationError("Время окончания опроса не должно быть меньше текущего")
        return value


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализация вопроса"""

    class Meta:
        model = Question
        fields = '__all__'


class QuestionUpdateSerializer(serializers.ModelSerializer):
    """Сериализация редактирования вопроса"""
    reset_answers = serializers.BooleanField(help_text='Сброс всех ответов на этот вопрос')

    class Meta:
        model = Question
        fields = '__all__'


class AnswerTextSerializer(serializers.ModelSerializer):
    """ Сериализация текстового ответа """

    class Meta:
        model = AnswerText
        fields = ['id', 'question', 'answer']

    def validate(self, data):
        is_answer_type_valid(QA_TYPE_TEXT, data)
        return data

    def create(self, validated_data):
        is_question_was_answered(validated_data['question'], validated_data['user'])
        return AnswerText.objects.create(**validated_data)

    def to_representation(self, instance):
        ret = {
            'id': instance.id,
            'question': instance.question.id,
            'answer_data': instance.answer
        }
        return ret


class AnswerSingleSerializer(serializers.ModelSerializer):
    """ Сериализация ответа с одним вариантом """

    class Meta:
        model = AnswerSingle
        exclude = ['user']

    def validate(self, data):
        is_answer_type_valid(QA_TYPE_SINGLE, data)
        return data

    def create(self, validated_data):
        is_question_was_answered(validated_data['question'], validated_data['user'])
        return AnswerSingle.objects.create(**validated_data)

    def to_representation(self, instance):
        ret = {
            'id': instance.id,
            'question': instance.question.id,
            'answer_data': instance.answer
        }
        return ret


class AnswerMultiSerializer(serializers.ModelSerializer):
    """ Сериализация ответа с несколькими вариантоми """
    answer_data = serializers.ListField(help_text='Варианты ответов')

    class Meta:
        model = AnswerMulti
        fields = ['question', 'answer_data']

    def validate(self, data):
        is_answer_type_valid(QA_TYPE_MULTI, data)
        if len(data['answer_data']) > len(set(data['answer_data'])):
            raise serializers.ValidationError({'answer_data': f'Варианты ответа не уникальны {data["answer_data"]}'})
        return data

    def create(self, validated_data):
        is_question_was_answered(validated_data['question'], validated_data['user'])
        variants = (AnswerVariants(variant=i) for i in validated_data['answer_data'])
        AnswerVariants.objects.bulk_create(variants, ignore_conflicts=True)
        answer_multi = AnswerMulti.objects.create(user=validated_data['user'], question=validated_data['question'])
        variants = AnswerVariants.objects.filter(variant__in=validated_data['answer_data'])
        answer_multi.answer.add(*list(variants))
        return answer_multi

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'question': instance.question.id,
            'answer_data': [a.variant for a in instance.answer.all()]
        }


class QuestionAnswerSerializer(serializers.ModelSerializer):
    answer_text = AnswerTextSerializer(many=True)
    answer_single = AnswerSingleSerializer(many=True)
    answer_multi = AnswerMultiSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'answer_text', 'answer_single', 'answer_multi', ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # ret.pop('type')
        a_t = ret.pop('answer_text')
        a_s = ret.pop('answer_single')
        a_m = ret.pop('answer_multi')
        answer = None
        if a_t:
            answer = a_t[0]
        elif a_s:
            answer = a_s[0]
        if a_m:
            answer = a_m[0]
        ret['answer'] = answer
        ret['answer'].pop('question')
        return ret


class MyPollsSerializer(serializers.ModelSerializer):
    """Сериализация опросов которые прошел юзер """
    question = QuestionAnswerSerializer(many=True)

    class Meta:
        model = Poll
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'question']
