from django.db import models
from config.utils import QA_TYPE_TEXT, QA_TYPE_MULTI, QA_TYPE_SINGLE


class UserAnonymous(models.Model):
    """ Анонимный пользователь """
    user = models.CharField(max_length=39)


class Poll(models.Model):
    """ Опрос """
    name = models.CharField(max_length=128, help_text='Наименование опроса')
    description = models.TextField(max_length=1024, help_text='Описание опроса')
    start_date = models.DateTimeField(auto_now_add=True, help_text='Дата начала опроса')
    end_date = models.DateTimeField(help_text='Дата окончания опроса')
    is_active = models.BooleanField(default=False, help_text='Активность опроса')


class Question(models.Model):
    """ Вопрос """
    QUESTION_TYPE = (
        (QA_TYPE_TEXT, 'Text'),
        (QA_TYPE_SINGLE, 'Single'),
        (QA_TYPE_MULTI, 'Multiple'),
    )
    poll = models.ForeignKey(Poll, related_name='question', on_delete=models.CASCADE, help_text='ID опроса')
    text = models.TextField(max_length=1024, help_text='Текст вопроса')
    type = models.CharField(max_length=1, choices=QUESTION_TYPE, help_text='Тип вопроса')


class AnswerText(models.Model):
    """ Текстовый ответ """
    question = models.ForeignKey(
        Question,
        related_name='answer_text',
        on_delete=models.CASCADE,
        help_text='ID вопроса')
    user = models.ForeignKey(UserAnonymous, null=False, related_name='answer_text', on_delete=models.CASCADE)
    answer = models.TextField(max_length=512, help_text='Текст ответа')


class AnswerVariants(models.Model):
    """ Варианты ответа """
    variant = models.PositiveSmallIntegerField(unique=True, default=0)


class AnswerMulti(models.Model):
    """ Ответ с несколькими вариантами """
    question = models.ForeignKey(
        Question,
        related_name='answer_multi',
        on_delete=models.CASCADE,
        help_text='ID вопроса')
    user = models.ForeignKey(UserAnonymous, null=False, related_name='answer_multi', on_delete=models.CASCADE)
    answer = models.ManyToManyField(AnswerVariants, help_text='Варианты ответов')


class AnswerSingle(models.Model):
    """ Ответ с одним вариантом """
    question = models.ForeignKey(
        Question,
        related_name='answer_single',
        on_delete=models.CASCADE,
        help_text='ID вопроса')
    user = models.ForeignKey(UserAnonymous, null=False, related_name='answer_single', on_delete=models.CASCADE)
    answer = models.PositiveSmallIntegerField(help_text='Номер ответа')
