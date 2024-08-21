from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import Truncator

from awl.admintools import admin_obj_link, fancy_modeladmin
from awl.rankedmodel.admintools import admin_move_links

from core.models import (Survey, Page, Question, QuestionTypes, AnswerGroup,
    Answer)

# ===========================================================================

admin.site.unregister(Group)

# ===========================================================================

base = fancy_modeladmin('id', 'name')
base.add_fk_link('page_set', Page, 'survey', display='{{obj.count}} Pages')
base.add_displays('show_questions', 'show_survey', 'show_results',
    'show_duplicate')

@admin.register(Survey)
class SurveyAdmin(base):
    prepopulated_fields = {"slug": ["name"]}

    def show_questions(self, obj):
        questions = Question.objects.filter(page__survey=obj)
        count = questions.count()
        plural = "s" if count > 1 else ""

        text = f"{count} question{plural}"

        url = reverse('admin:core_question_changelist')
        url += '?id__in=' + ','.join([str(q.id) for q in questions])

        return format_html('<a href="{}">{}</a>', url, text)
    show_questions.short_description = "Questions"

    def show_survey(self, obj):
        url = reverse('start_quiz', args=(obj.slug, ))

        return format_html('<a href="{}">Take <i>{}</i></a>', url, obj.name)
    show_survey.short_description = "Do Survey"

    def show_results(self, obj):
        url = reverse('result_page', args=(obj.id, obj.token))

        return format_html('<a href="{}">View <i>{}</i></a>', url, obj.name)
    show_results.short_description = "Results"

    def show_duplicate(self, obj):
        url = reverse('duplicate', args=(obj.id, ))

        return format_html('<a href="{}">Duplicate <i>{}</i></a>', url,
            obj.name)
    show_duplicate.short_description = "Duplicate"


base = fancy_modeladmin('id')
base.add_link('survey', 'Survey', '{{obj.name}}')
base.add_fk_link('question_set', Question, 'page',
    display='{{obj.count}} Questions')
base.add_displays('show_move_rank')

@admin.register(Page)
class PageAdmin(base):

    def show_move_rank(self, obj):
        return admin_move_links(obj)
    show_move_rank.short_description = "Rank"


base = fancy_modeladmin('id', 'question_type', 'short_text')
base.add_link('page__survey', 'Survey', '{{obj.page.survey.name}}')
base.add_link('page', 'Page', 'Page #{{obj.rank}}')
base.add_fk_link('answer_set', Answer, 'question',
    display='{{obj.count}} Answers')
base.add_displays('show_move_rank', 'show_graph')

@admin.register(Question)
class QuestionAdmin(base):

    def show_move_rank(self, obj):
        return admin_move_links(obj)
    show_move_rank.short_description = "Rank"

    def show_graph(self, obj):
        if obj.answer_set.count() == 0:
            return format_html('<i> No answers </i>')

        url = reverse('result_question', args=(obj.id, ))
        return format_html('<a href="{}">Graph</a>', url)


base = fancy_modeladmin('id')
base.add_link('survey', 'Survey', '{{obj.name}}')
base.add_link('page', 'Page', 'Page #{{obj.rank}}')
base.add_displays('token')

@admin.register(AnswerGroup)
class AnswerGroupAdmin(base):
    pass


base = fancy_modeladmin('id')
base.add_link('question', 'Question', '{{obj.short_text}}')
base.add_displays('show_type', 'show_answer')
base.add_link('answer_group', 'AnswerGroup')

@admin.register(Answer)
class AnswerAdmin(base):

    def show_answer(self, obj):
        if obj.question.question_type == QuestionTypes.TEXT:
            return Truncator(obj.text_answer).words(5, truncate=' ...')

        return obj.get_value()
    show_answer.short_description = "Answer"

    def show_type(self, obj):
        return QuestionTypes(obj.question.question_type).name
    show_type.short_description = "Type"
