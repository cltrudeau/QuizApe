import string
import secrets
from datetime import datetime
from functools import cached_property

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import Truncator

import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from awl.absmodels import TimeTrackModel
from awl.rankedmodel.models import RankedModel

# ===========================================================================

ALPHABET = string.ascii_letters + string.digits
matplotlib.use('agg')  # force non-interactive backend
#matplotlib.rcParams['figure.dpi'] = 200   # increase image DPI

# ===========================================================================

class Survey(TimeTrackModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(blank=True, null=True)
    editable = models.BooleanField(default=False)
    token = models.CharField(default='', max_length=20, db_index=True)

    intro = models.TextField()
    outro = models.TextField()

    def __str__(self):
        return f"Survey(id={self.id}, {self.name})"

    def save(self, *args, **kwargs):
        just_created = self.pk is None
        super().save(*args, **kwargs)
        if just_created:
            self.token = ''.join(secrets.choice(ALPHABET) for _ in range(18))
            self.save()


class Page(RankedModel, TimeTrackModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    intro = models.TextField()

    def grouped_filter(self):
        return Page.objects.filter(survey=self.survey)

    @cached_property
    def next_page(self):
        try:
            return Page.objects.get(survey=self.survey, rank=self.rank + 1)
        except Page.DoesNotExist:
            return None

    @cached_property
    def prev_page(self):
        try:
            return Page.objects.get(survey=self.survey, rank=self.rank - 1)
        except Page.DoesNotExist:
            return None

    def __str__(self):
        return f"Page(id={self.id}, survey={self.survey.name}, #{self.rank})"


class QuestionTypes(models.TextChoices):
    BOOLEAN = "B"
    NUM = "N"
    STAR = "S"
    TEXT = "T"
    CHOICE = "C"


class Question(RankedModel, TimeTrackModel):
    question_type = models.CharField(max_length=1, choices=QuestionTypes)
    question_text = models.TextField()
    required = models.BooleanField(default=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    choices = models.JSONField(blank=True, null=True)
    choices_blank_allowed = models.BooleanField(default=False)

    num_answer_min = models.IntegerField(blank=True, null=True)
    num_answer_max = models.IntegerField(blank=True, null=True)

    COLOURS = (
        # Red        green      blue        purple     orange     yellow
        "#de324c", "#95cf92", "#369acc",  "#9656a2", "#f4895f", "#f8e16f",
    )

    def __str__(self):
        return f"Question(id={self.id}, '{self.short_text}')"

    @property
    def short_text(self):
        return Truncator(self.question_text).words(5, truncate=' ...')

    @property
    def answers(self):
        return Answer.objects.filter(answer_group__survey=self.page.survey,
            question=self)

    # --- Graph generating methods
    def generate_graph(self, survey, survey_dir):
        now = int(datetime.now().timestamp())
        file = survey_dir / f"q-{self.id}-{now}.svg"

        # Check that there are answers at all
        if self.answer_set.count() == 0:
            return None

        if self.question_type == QuestionTypes.BOOLEAN:
            return self._generate_boolean(survey, file)
        elif self.question_type == QuestionTypes.NUM:
            return self._generate_num(survey, file)
        elif self.question_type == QuestionTypes.STAR:
            return self._generate_star(survey, file)
        elif self.question_type == QuestionTypes.CHOICE:
            return self._generate_choice(survey, file)

    def _generate_boolean(self, survey, file):
        total = AnswerGroup.objects.filter(survey=survey).count()
        total_true = Answer.objects.filter(answer_group__survey=survey,
            question=self, bool_answer=True).count()
        total_false = Answer.objects.filter(answer_group__survey=survey,
            question=self, bool_answer=False).count()

        dna = total - (total_true + total_false)

        data = (total_true, total_false, dna)

        fig, axis = plt.subplots()
        axis.bar( ("True", "False", "None"), data, color=self.COLOURS)
        fig.savefig(file, format="svg")
        return file

    def _generate_num(self, survey, file):
        total = AnswerGroup.objects.filter(survey=survey).count()

        if self.num_answer_min is not None:
            bottom = self.num_answer_min
        else:
            bottom = Answer.objects.filter(answer_group__survey=survey,
                    question=self).exclude(num_answer=None).aggregate(
                        num_answer=models.Min("num_answer"))["num_answer"]

        if self.num_answer_max is not None:
            top = self.num_answer_max
        else:
            top = Answer.objects.filter(answer_group__survey=survey,
                    question=self).exclude(num_answer=None).aggregate(
                        num_answer=models.Max("num_answer"))["num_answer"]

        data = []
        labels = []
        for num in range(bottom, top + 1):
            value = Answer.objects.filter(answer_group__survey=survey,
                question=self, num_answer=num).count()
            data.append(value)
            labels.append(str(num))

        dna = total - sum(data)
        data.append(dna)
        labels.append("None")

        fig, axis = plt.subplots()
        axis.bar(labels, data, color=self.COLOURS)
        fig.savefig(file, format="svg")

        return file

    def _generate_star(self, survey, file):
        total = AnswerGroup.objects.filter(survey=survey).count()

        data = []
        labels = []
        for num in range(5, 0, -1):
            value = Answer.objects.filter(answer_group__survey=survey,
                question=self, star_answer=num).count()
            data.append(value)
            labels.append(str(num))

        dna = total - sum(data)
        data.append(dna)
        labels.append("None")

        fig, axis = plt.subplots()
        axis.bar(labels, data, color=self.COLOURS)
        fig.savefig(file, format="svg")

        return file

    def _generate_choice(self, survey, file):
        total = AnswerGroup.objects.filter(survey=survey).count()

        labels = []
        data = []
        for choice in self.choices:
            labels.append(choice[1])
            value = Answer.objects.filter(answer_group__survey=survey,
                question=self, choices_answer=choice[0]).count()
            data.append(value)

        labels.append("None")
        dna = total - sum(data)
        data.append(dna)

        fig, axis = plt.subplots()
        axis.bar( labels, data, color=self.COLOURS)
        fig.savefig(file, format="svg")

        return file

# ---------------------------------------------------------------------------

class AnswerGroup(TimeTrackModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, blank=True, null=True,
        on_delete=models.CASCADE)
    token = models.CharField(max_length=20, db_index=True)

    def __str__(self):
        return f"AnswerGroup(id={self.id})"

    @classmethod
    def factory(cls, slug):
        survey = Survey.objects.get(slug=slug)
        token = ''.join(secrets.choice(ALPHABET) for _ in range(18))
        page = Page.objects.get(survey=survey, rank=1)
        group = AnswerGroup.objects.create(survey=survey, page=page,
            token=token)

        return group

    def get_form(self, post=None):
        class BaseForm(forms.Form):
            pass

        fields = {}
        initial_values = {}
        for question in self.page.question_set.all():
            name = f"question-{question.id}"
            try:
                answer = Answer.objects.get(answer_group=self,
                    question=question)
                if answer.has_value():
                    initial_values[name] = answer.get_form_value()
            except Answer.DoesNotExist:
                pass

            kwargs = {
                "label": question.question_text,
                "required": question.required,
            }

            if question.question_type == QuestionTypes.BOOLEAN:
                field = forms.ChoiceField(choices=(("1", "1"), ("0", "0")),
                    **kwargs)
            elif question.question_type == QuestionTypes.NUM:
                if question.num_answer_min is not None:
                    kwargs['min_value'] = question.num_answer_min
                if question.num_answer_max is not None:
                    kwargs['max_value'] = question.num_answer_max

                field = forms.IntegerField(**kwargs)
            elif question.question_type == QuestionTypes.STAR:
                field = forms.IntegerField(widget=forms.RadioSelect(), **kwargs)
            elif question.question_type == QuestionTypes.TEXT:
                field = forms.CharField(widget=forms.Textarea(), **kwargs)
            elif question.question_type == QuestionTypes.CHOICE:
                field = forms.ChoiceField(choices=question.choices, **kwargs)
            else:
                raise RuntimeError(f"{question} has invalid type")

            fields[name] = field

        AGForm = type("AGForm", (BaseForm, ), fields)
        if post is None:
            return AGForm(initial=initial_values)

        return AGForm(post)

    def save_values(self, data):
        for question in self.page.question_set.all():
            name = f'question-{question.id}'
            if name not in data:
                continue

            try:
                answer = Answer.objects.get(answer_group=self,
                    question=question)
            except Answer.DoesNotExist:
                answer = Answer.objects.create(question=question,
                    answer_group=self)

            answer.set_value(data[name])


class Answer(TimeTrackModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_group = models.ForeignKey(AnswerGroup, on_delete=models.CASCADE)

    bool_answer = models.BooleanField(blank=True, null=True)
    num_answer = models.IntegerField(blank=True, null=True)
    star_answer = models.PositiveSmallIntegerField(blank=True, null=True,
        validators=(MinValueValidator(0), MaxValueValidator(5)))
    text_answer = models.TextField(blank=True, null=True)
    choices_answer = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Answer(id={self.id}, q={self.question.id})"

    def set_value(self, value):
        try:
            if self.question.question_type == QuestionTypes.BOOLEAN:
                if isinstance(value, str | int):
                    self.bool_answer = bool(int(value))
                else:
                    self.bool_answer = value
            elif self.question.question_type == QuestionTypes.NUM:
                if self.question.num_answer_min is not None and \
                    value < self.question.num_answer_min:
                        raise ValueError((f"Value {value} is below min "
                            "{self.question.num_answer_min}"))
                if self.question.num_answer_max is not None and \
                    value > self.question.num_answer_max:
                        raise ValueError((f"Value {value} is below max "
                            "{self.question.num_answer_max}"))

                self.num_answer = value
            elif self.question.question_type == QuestionTypes.STAR:
                self.star_answer = int(value)
            elif self.question.question_type == QuestionTypes.TEXT:
                self.text_answer = value
            elif self.question.question_type == QuestionTypes.CHOICE:
                self.choices_answer = value
            else:
                raise RuntimeError(f"{self.question} has invalid type")
        except:
            raise ValueError(f"Value *{value}* not valid for {self.question}")

        self.save()

    def get_form_value(self):
        if self.question.question_type == QuestionTypes.BOOLEAN:
            return "1" if self.bool_answer else "0"
        elif self.question.question_type == QuestionTypes.STAR:
            return f"{self.star_answer}"

        return self.get_value()

    def get_value(self):
        if self.question.question_type == QuestionTypes.BOOLEAN:
            return self.bool_answer
        elif self.question.question_type == QuestionTypes.NUM:
            return self.num_answer
        elif self.question.question_type == QuestionTypes.STAR:
            return self.star_answer
        elif self.question.question_type == QuestionTypes.TEXT:
            return self.text_answer
        elif self.question.question_type == QuestionTypes.CHOICE:
            return self.choices_answer

        raise RuntimeError(f"{question} has invalid type")

    def has_value(self):
        if self.question.question_type == QuestionTypes.BOOLEAN:
            return self.bool_answer is not None
        elif self.question.question_type == QuestionTypes.NUM:
            return self.num_answer is not None
        elif self.question.question_type == QuestionTypes.STAR:
            return self.star_answer is not None
        elif self.question.question_type == QuestionTypes.TEXT:
            return self.text_answer is not None
        elif self.question.question_type == QuestionTypes.CHOICE:
            return self.choices_answer is not None

        raise RuntimeError(f"{question} has invalid type")
