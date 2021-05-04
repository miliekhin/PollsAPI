from .views import PollViewSet
from .views import QuestionViewSet
from .views import AnswerTextViewSet
from .views import AnswerMultiViewSet
from .views import AnswerSingleViewSet
from .views import PollsActiveViewSet
from .views import PollsMyViewSet
from rest_framework.routers import SimpleRouter
from django.urls import path

router = SimpleRouter()
router.register('polls', PollViewSet)
router.register('questions', QuestionViewSet)

urlpatterns = [
    path('polls/active/', PollsActiveViewSet.as_view({'get': 'list'}), name='polls_active'),
    path('polls/my/', PollsMyViewSet.as_view({'get': 'list'}), name='polls_my'),
    path('answers/text/', AnswerTextViewSet.as_view({'post': 'create'}), name='answer_text'),
    path('answers/single/', AnswerSingleViewSet.as_view({'post': 'create'}), name='answer_single'),
    path('answers/multi/', AnswerMultiViewSet.as_view({'post': 'create'}), name='answer_multi'),
]
urlpatterns += router.urls
