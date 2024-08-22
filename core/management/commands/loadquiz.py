import json
from argparse import RawTextHelpFormatter
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.urls import reverse

from core.models import Survey, Page, Question, QuestionTypes

HELP = """\
Creates a quiz based on a JSON file spec.

{
    "name": "Survey name",
    "slug": "Survey slug",
    "intro": "Optional introduction string",
    "outro": "Optional goodbye string",
    "pages": [
        {
            "intro": "Optional page introduction",
            "questions": [
                {
                    "type": "Question type: BOOLEAN, STAR, NUM, TEXT, CHOICE",
                    "text": "Question text as string, or a list to create
                             multiple questions of the same type",
                    "min": 1, # optional min value for NUM type
                    "max": 10, # optional max value for NUM type
                    "choices": ["apple", "pear"], # values for CHOICE type

                    "choices_blank_allowed": True, # True if empty choice
                                                      allowed, defaults to
                                                      False
                }
            ]
        }
    ]
}
"""

class Command(BaseCommand):
    help = HELP

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str, help="JSON file")

    def handle(self, *args, **options):
        path = Path(options['filename'])
        content = json.loads(path.read_text())

        # Wrap the creation in a transaction so it is all or nothing
        with transaction.atomic():
            kwargs = {
                "name": content["name"],
                "slug": content["slug"],
            }

            if "intro" in content:
                kwargs["intro"] = content["intro"]
            if "outro" in content:
                kwargs["outro"] = content["intro"]

            survey = Survey.objects.create(**kwargs)
            for c_page in content["pages"]:
                kwargs = {
                    "survey": survey,
                }

                if "intro" in c_page:
                    kwargs["intro"] = c_page["intro"]

                page = Page.objects.create(**kwargs)

                # Create questions
                for cq in c_page["questions"]:
                    kwargs = {
                        "page": page,
                        "question_type": getattr(QuestionTypes,
                            cq["type"].upper()),
                    }

                    for attr in ["min", "max", "choices",
                            "choices_blank_allowed",]:
                        if attr in cq:
                            kwargs[attr] = cq[attr]

                    if isinstance(cq["text"], str):
                        kwargs["question_text"] = cq["text"]

                        Question.objects.create(**kwargs)
                    else:
                        # Text is an iterable, create multiple
                        for text in cq["text"]:
                            kwargs["question_text"] = text
                            Question.objects.create(**kwargs)

        # Report on what we did
        print(f"Created survey id={survey.id}")
        pcount = Page.objects.filter(survey=survey).count()
        qcount = Question.objects.filter(page__survey=survey).count()
        print(f"Num pages: {pcount}, num questions: {qcount}")

        url = reverse("start_quiz", args=(survey.slug, ))
        print(f"Take survey: {url}")
        url = reverse("result_page", args=(survey.id, survey.token))
        print(f"Result report: {url}")
