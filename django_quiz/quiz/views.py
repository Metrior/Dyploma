import random
import sqlite3

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView

from .forms import QuestionForm, EssayForm
from .models import Quiz, Category, Progress, Sitting, Question
from essay.models import Essay_Question


class QuizMarkerMixin(object):
    @method_decorator(login_required)
    @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


class QuizListView(ListView):
    model = Quiz

    def get_queryset(self):
        queryset = super(QuizListView, self).get_queryset()
        return queryset.filter(draft=False)


class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CategoriesListView(ListView):
    model = Category


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            category=self.kwargs['category_name']
        )

        return super(ViewQuizListByCategory, self).\
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category, draft=False)


class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        return context


class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        queryset = super(QuizMarkingList, self).get_queryset()\
                                               .filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)


        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] =\
            context['sitting'].get_questions(with_answers=True)
        return context


class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        self.logged_in_user = self.request.user.is_authenticated()

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(request.user,
                                                        self.quiz)
        else:
            raise PermissionDenied

        if self.sitting is False:
            return render(request, 'single_complete.html')

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()
        else:
            return redirect('/q/test/')
            # self.question = self.anon_next_question()
            # self.progress = self.anon_sitting_progress()



        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()
        else:
            self.form_valid_anon(form)
            if not self.request.session[self.quiz.anon_q_list()]:
                return self.final_result_anon()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    # def racionalnost_score(self):
    #     racionalnost_score={}
    #     # stratedy_score={}
    #     # statika_score={}
    #     # emotivizm_score={}
    #     return racionalnost_score

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        from pprint import pprint
        pprint(form.cleaned_data)
        pprint(form.__dict__)
        from custom_multichoice.models import Answer
        obj = Answer.objects.get(id=int(guess))
        progress.update_score(self.question, guess)
        self.sitting.add_to_emotivizm(int(obj.emotivizm))
        self.sitting.add_to_statika(int(obj.statika))
        self.sitting.add_to_strategy(int(obj.strategy))
        self.sitting.add_to_racionalnost(int(obj.racionalnost))
        if int(obj.racionalnost)==0 and int(obj.emotivizm)==0 and int(obj.statika)==0 and int(obj.strategy)==0:
            self.dual_type=1
            self.soctype='Gugo'
            self.dual='Robespier'
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==0 and int(obj.statika)==0 and int(obj.strategy)==1:
            self.i=2
            self.soctype='Robespier'
            self.dual='Gugo'
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==0 and int(obj.statika)==1 and int(obj.strategy)==0:
            self.i=3
            self.soctype='Gamlet'
            self.dual='Gorki'
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==0 and int(obj.statika)==1 and int(obj.strategy)==1:
            self.i=4
            self.soctype='Gorki'
            self.dual='Gamlet'
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==1 and int(obj.statika)==0 and int(obj.strategy)==0:
            self.i=5
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==1 and int(obj.statika)==0 and int(obj.strategy)==1:
            self.i=6
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==1 and int(obj.statika)==1 and int(obj.strategy)==0:
            self.i=7
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==1 and int(obj.statika)==1 and int(obj.strategy)==1:
            self.i=8
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==0 and int(obj.emotivizm)==0 and int(obj.statika)==0 and int(obj.strategy)==0:
            self.i=9
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==0 and int(obj.statika)==0 and int(obj.strategy)==1:
            self.i=10
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==0 and int(obj.statika)==1 and int(obj.strategy)==0:
            self.i=11
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==0 and int(obj.statika)==1 and int(obj.strategy)==1:
            self.i=12
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==1 and int(obj.statika)==0 and int(obj.strategy)==0:
            self.i=13
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==1 and int(obj.statika)==0 and int(obj.strategy)==1:
            self.i=14
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==1 and int(obj.statika)==1 and int(obj.strategy)==0:
            self.i=15
            progress.update(self.question, self.i)
        elif int(obj.racionalnost)==1 and int(obj.emotivizm)==1 and int(obj.statika)==1 and int(obj.strategy)==1:
            self.i=16
            progress.update(self.question, self.i)


        # is_correct = self.question.check_if_correct(guess)
        # if is_correct is True:
        #     self.sitting.add_to_score(1)
        #     progress.update_score(self.question, 1, 1)
        # else:
        #     self.sitting.add_incorrect_question(self.question)
        #     progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def random_user(self):
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        sql = "SELECT * FROM quiz_progress WHERE score='%s'"%self.i
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            id = row[1]
            name = random.choice(id)
        cursor.execute("SELECT email FROM auth_user WHERE id='%s'"% name)
        results2=cursor.fetchall()
        for row in results2:
            selected = row[0]
        db.close
        return selected

    def final_result_user(self):

        friend = self.random_user()
        soctype = self.soctype
        dual = self.dual
        results = {
            'quiz': self.quiz,
            'soctype': soctype,
            'friend': friend,
            'dual': dual,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_quiz_complete()



        if self.quiz.exam_paper is False:
            self.sitting.delete()

        return render(self.request, 'result.html', results)

    def anon_load_sitting(self):
        if self.quiz.single_attempt is True:
            return False

        if self.quiz.anon_q_list() in self.request.session:
            return self.request.session[self.quiz.anon_q_list()]
        else:
            return self.new_anon_quiz_session()

    def new_anon_quiz_session(self):
        """
        Sets the session variables when starting a quiz for the first time
        as a non signed-in user
        """
        self.request.session.set_expiry(259200)  # expires after 3 days
        questions = self.quiz.get_questions()
        question_list = [question.id for question in questions]

        if self.quiz.random_order is True:
            random.shuffle(question_list)

        if self.quiz.max_questions and (self.quiz.max_questions
                                        < len(question_list)):
            question_list = question_list[:self.quiz.max_questions]

        # session score for anon users
        self.request.session[self.quiz.anon_score_id()] = 0

        # session list of questions
        self.request.session[self.quiz.anon_q_list()] = question_list

        # session list of question order and incorrect questions
        self.request.session[self.quiz.anon_q_data()] = dict(
            order=question_list,
        )

        return self.request.session[self.quiz.anon_q_list()]

    def anon_next_question(self):
        next_question_id = self.request.session[self.quiz.anon_q_list()][0]
        return Question.objects.get_subclass(id=next_question_id)

    def anon_sitting_progress(self):
        total = len(self.request.session[self.quiz.anon_q_data()]['order'])
        answered = total - len(self.request.session[self.quiz.anon_q_list()])
        return (answered, total)



        self.previous = {}
        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess,

                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}

        self.request.session[self.quiz.anon_q_list()] =\
            self.request.session[self.quiz.anon_q_list()][1:]

    def final_result_anon(self):
        score = self.request.session[self.quiz.anon_score_id()]
        q_order = self.request.session[self.quiz.anon_q_data()]['order']
        max_score = len(q_order)
        percent = int(round((float(score) / max_score) * 100))
        session, session_possible = anon_session_score(self.request.session)
        if score is 0:
            score = "0"

        results = {
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'session': session,
            'possible': session_possible
        }

        del self.request.session[self.quiz.anon_q_list()]

        if self.quiz.answers_at_end:
            results['questions'] = sorted(
                self.quiz.question_set.filter(id__in=q_order)
                                      .select_subclasses(),
                key=lambda q: q_order.index(q.id))



        else:
            results['previous'] = self.previous

        del self.request.session[self.quiz.anon_q_data()]

        return render(self.request, 'result.html', results)


def anon_session_score(session, to_add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and
    return session score.

    examples:
        anon_session_score(1, 1) will add 1 out of a possible 1
        anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score() will return the session score
                                    without modification

    Left this as an individual function for unit testing
    """
    if "session_score" not in session:
        session["session_score"], session["session_score_possible"] = 0, 0

    if possible > 0:
        session["session_score"] += to_add
        session["session_score_possible"] += possible

    return session["session_score"], session["session_score_possible"]
