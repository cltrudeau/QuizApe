import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import models

from core.models import (Survey, Page, Question, QuestionTypes, AnswerGroup,
    Answer)


class ColourChoices(models.TextChoices):
    RED = 'R'
    BLUE = 'B'
    GREEN = 'G'


class Command(BaseCommand):
    help = "Creates sample test data."

    def handle(self, *args, **options):
        # Admin Login
        User.objects.create_superuser("admin", password="admin")

        survey = Survey.objects.create(name="First Survey", slug="first1",
            intro="Welcome to the survey", logo="company_logo.png")
        page = Page.objects.create(survey=survey, intro="Page intro")

        Question.objects.create(
            question_type=QuestionTypes.BOOLEAN,
            question_text="Roses are red?",
            page=page)

        Question.objects.create(
            question_type=QuestionTypes.STAR,
            question_text="Rating?",
            page=page)

        Question.objects.create(
            question_type=QuestionTypes.NUM,
            question_text="Between 1 and 10?",
            num_answer_min=1,
            num_answer_max=10,
            page=page)

        page = Page.objects.create(survey=survey)

        Question.objects.create(
            question_type=QuestionTypes.TEXT,
            question_text="Comment?",
            page=page)

        Question.objects.create(
            question_type=QuestionTypes.CHOICE,
            question_text="Favourite colour?",
            choices=ColourChoices.choices,
            page=page)

        Question.objects.create(
            question_type=QuestionTypes.CHOICE,
            question_text="Favourite colour with blank?",
            choices=ColourChoices.choices,
            choices_blank_allowed=True,
            page=page)

        survey = Survey.objects.create(name="Second Survey", slug="second",
            editable=True)
        page = Page.objects.create(survey=survey)

        q1 = Question.objects.create(question_type=QuestionTypes.BOOLEAN,
            question_text="True?", page=page)

        q2 = Question.objects.create(question_type=QuestionTypes.STAR,
            question_text="Star?", page=page)

        q3 = Question.objects.create(question_type=QuestionTypes.NUM,
            question_text="1-10", page=page)

        q4 = Question.objects.create(question_type=QuestionTypes.TEXT,
            question_text="Text?", page=page)

        q5 = Question.objects.create(question_type=QuestionTypes.CHOICE,
            question_text="Colour?", choices=ColourChoices.choices,
            page=page)

        # Answers for Survey 2
        for _ in range(5):
            ag = AnswerGroup.factory(survey.slug)
            answer = Answer.objects.create(question=q1, answer_group=ag)
            answer.set_value(True)
            answer = Answer.objects.create(question=q2, answer_group=ag)
            answer.set_value(3)
            answer = Answer.objects.create(question=q3, answer_group=ag)
            answer.set_value(8)
            answer = Answer.objects.create(question=q4, answer_group=ag)
            answer.set_value("text")
            answer = Answer.objects.create(question=q5, answer_group=ag)
            answer.set_value(ColourChoices.RED)

        for _ in range(3):
            ag = AnswerGroup.factory(survey.slug)
            answer = Answer.objects.create(question=q1, answer_group=ag)
            answer.set_value(False)
            answer = Answer.objects.create(question=q2, answer_group=ag)
            answer.set_value(2)
            answer = Answer.objects.create(question=q3, answer_group=ag)
            answer.set_value(7)
            answer = Answer.objects.create(question=q4, answer_group=ag)
            answer.set_value("blah")
            answer = Answer.objects.create(question=q5, answer_group=ag)
            answer.set_value(ColourChoices.BLUE)

        # Empty Answers
        ag = AnswerGroup.factory(survey.slug)
        Answer.objects.create(question=q1, answer_group=ag)
        Answer.objects.create(question=q2, answer_group=ag)
        Answer.objects.create(question=q3, answer_group=ag)
        Answer.objects.create(question=q4, answer_group=ag)
        Answer.objects.create(question=q5, answer_group=ag)

        # Empty AnswerGroup
        AnswerGroup.factory(survey.slug)

        # Survey to test numbers historgrams
        survey = Survey.objects.create(name="Third Survey", slug="third")
        page = Page.objects.create(survey=survey)

        q1 = Question.objects.create(question_type=QuestionTypes.NUM,
            question_text="1-100", page=page)
        q2 = Question.objects.create(question_type=QuestionTypes.NUM,
            question_text="1-7", page=page, num_answer_min=1, num_answer_max=7)

        for _ in range(1, 10):
            for num in range(2, 8):
                ag = AnswerGroup.factory(survey.slug)
                Answer.objects.create(question=q1, answer_group=ag,
                    num_answer=num)
                Answer.objects.create(question=q2, answer_group=ag,
                    num_answer=num)
