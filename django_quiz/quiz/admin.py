from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from .models import Quiz, Category, SubCategory, Progress, Question
from custom_multichoice.models import MCQuestion, Answer
from true_false.models import TF_Question
from essay.models import Essay_Question


class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):
    """
    below is from
    http://stackoverflow.com/questions/11657682/
    django-admin-interface-using-horizontal-filter-with-
    inline-manytomany-field
    """

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial =\
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set = self.cleaned_data['questions']
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title', )
    search_fields = ('description',)


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', )
    fields = ('content',
              'figure', 'quiz','answer_order',)

    search_fields = ('content',)
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """
    search_fields = ('user', 'score', )

admin.site.register(Quiz, QuizAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(Progress, ProgressAdmin)

