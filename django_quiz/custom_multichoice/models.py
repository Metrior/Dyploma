from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django.db import models
from quiz.models import Question


ANSWER_ORDER_OPTIONS = (
    ('content', _('Content')),
    ('random', _('Random')),
    ('none', _('None'))
)


class MCQuestion(Question):

    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("The order in which custom_multichoice "
                    "answer options are displayed "
                    "to the user"),
        verbose_name=_("Answer Order"))
    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset
    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")


@python_2_unicode_compatible
class Answer(models.Model):
    question = models.ForeignKey(MCQuestion, verbose_name=_("Question"))
    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Enter the answer text that "
                                           "you want displayed"),
                               verbose_name=_("Content"))
    racionalnost = models.IntegerField(
        verbose_name=_("racionalnost"),
        default=0,
        help_text=_('Enter racionalnost??')
    )
    statika = models.IntegerField(
        verbose_name=_("statika"),
        default=0,
        help_text=_('Enter statika??')
    )
    strategy = models.IntegerField(
        verbose_name=_("strategy"),
        default=0,
        help_text=_('Enter strategy??')
    )
    emotivizm = models.IntegerField(
        verbose_name=_("emotivizm"),
        default=0,
        help_text=_('Enter emotivizm??')
    )
    def __str__(self):
        return {
            'content': self.content,
            'racionalnost': self.racionalnost,
            'statika': self.statika,
            'strategy': self.strategy,
            'emotivizm': self.emotivizm,
        }
    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")