from rest_framework.viewsets import ModelViewSet
from .serializers import PollSerializer
from .serializers import QuestionSerializer, QuestionUpdateSerializer
from .serializers import AnswerTextSerializer
from .serializers import AnswerSingleSerializer
from .serializers import AnswerMultiSerializer
from .serializers import MyPollsSerializer
from .models import Poll, Question, AnswerText, UserAnonymous, AnswerSingle, AnswerMulti
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from rest_framework.response import Response


def get_anonymous_user_id(request):
    """ Получение ID сессии для дальнейшей идентификации анонимного юзера"""
    anon_user = request.session.session_key
    if not anon_user:
        request.session.save()
        anon_user = request.session.session_key
    return anon_user


class PollViewSet(ModelViewSet):
    """
    list: Список всех опросов
    create: Создание опроса
    retrieve: Получение опроса по ID
    update: Обновление всех атрибутов опроса
    partial_update: Частичное обновление атрибутов опроса
    delete: Удаление опроса
    """

    serializer_class = PollSerializer
    queryset = Poll.objects.all()
    permission_classes = [IsAuthenticated]


class QuestionViewSet(ModelViewSet):
    """
    list: Список всех вопросов
    create: Создание вопроса
    retrieve: Получение вопроса по ID
    update: Обновление всех атрибутов вопроса
    partial_update: Частичное обновление атрибутов вопроса
    delete: Удаление вопроса
    """
    queryset = Question.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'partial_update' or self.action == 'update':
            return QuestionUpdateSerializer
        return serializer_class

    def update(self, request, *args, **kwargs):
        # При изменении вопроса можно удалить все ответы всех пользователей на него
        if request.data['reset_answers']:
            question = Question.objects.get(id=kwargs['pk'])
            question.answer_text.all().delete()
            question.answer_single.all().delete()
            question.answer_multi.all().delete()
        ret = super(QuestionViewSet, self).update(request, *args, **kwargs)
        return ret


class AnswerTextViewSet(ModelViewSet):
    """ create: Создание текстового ответа """

    queryset = AnswerText.objects.all()
    serializer_class = AnswerTextSerializer

    def perform_create(self, serializer):
        anon_user, created = UserAnonymous.objects.get_or_create(user=get_anonymous_user_id(self.request))
        serializer.save(user=anon_user)


class AnswerSingleViewSet(ModelViewSet):
    """ create: Создание ответа с одним вариантом ответа """

    queryset = AnswerSingle.objects.all()
    serializer_class = AnswerSingleSerializer

    def perform_create(self, serializer):
        anon_user, created = UserAnonymous.objects.get_or_create(user=get_anonymous_user_id(self.request))
        serializer.save(user=anon_user)


class AnswerMultiViewSet(ModelViewSet):
    """ create: Создание ответа с несколькими вариантоми ответа """

    queryset = AnswerMulti.objects.all()
    serializer_class = AnswerMultiSerializer

    def perform_create(self, serializer):
        anon_user, created = UserAnonymous.objects.get_or_create(user=get_anonymous_user_id(self.request))
        serializer.save(user=anon_user)


class PollsActiveViewSet(ModelViewSet):
    """ list: Список активных опросов """
    serializer_class = PollSerializer
    queryset = Poll.objects.filter(is_active=True)


class PollsMyViewSet(ModelViewSet):
    """ list: Список опросов пройденных пользователем """
    serializer_class = MyPollsSerializer

    def list(self, request, *args, **kwargs):
        anon_user = get_anonymous_user_id(self.request)
        qt = AnswerText.objects.filter(user__user=anon_user)
        qs = AnswerSingle.objects.filter(user__user=anon_user)
        qm = AnswerMulti.objects.filter(user__user=anon_user).prefetch_related('answer')
        qq = Question.objects.filter(
            Q(answer_text__user__user=anon_user) |
            Q(answer_single__user__user=anon_user) |
            Q(answer_multi__user__user=anon_user)
        )
        qq = qq.prefetch_related(
            Prefetch('answer_text', queryset=qt),
            Prefetch('answer_single', queryset=qs),
            Prefetch('answer_multi', queryset=qm),
        )
        qp = Poll.objects.filter(
            Q(question__answer_text__user__user=anon_user) |
            Q(question__answer_single__user__user=anon_user) |
            Q(question__answer_multi__user__user=anon_user)
        ).distinct()
        queryset = qp.prefetch_related(Prefetch('question', queryset=qq))
        serializer = MyPollsSerializer(queryset, many=True)
        return Response(serializer.data)
