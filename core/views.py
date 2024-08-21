import re
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Min, Max
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from core.models import (Survey, Page, AnswerGroup, Answer, QuestionTypes,
    Question)

# ===========================================================================

EPOCH_PART = re.compile(r"q-\d+-(\d+)\.svg")

# ===========================================================================

def home(request):
    if request.method == "POST":
        return redirect("start_quiz", slug=request.POST['start-slug'])

    return render(request, "home.html")


def start_quiz(request, slug):
    # check for a cookie to see if they've done this survey before
    token = request.COOKIES.get(slug, '')
    broken = False
    if token:
        try:
            group = AnswerGroup.objects.get(survey__slug=slug, token=token)
        except AnswerGroup.DoesNotExist:
            broken = True

    if not token or broken:
        # Starting a new survey
        group = AnswerGroup.factory(slug)
        data = {
            "group": group,
            "start_page": reverse("page", args=(group.survey.id, group.token,
                group.page.rank)),
        }
        response = render(request, "start.html", data)
        response.set_cookie(slug, group.token)
        return response

    # Existing survey
    if group.page:
        # Survey is in progress
        response = redirect("page", survey_id=group.survey.id,
            token=group.token, page_num=group.page.rank)
        response.set_cookie(slug, token)
    else:
        # Survey is done
        response = redirect("done", survey_id=group.survey.id,
            token=group.token)

    return response


def page(request, survey_id, token, page_num):
    group = get_object_or_404(AnswerGroup, survey__id=survey_id, token=token)
    page = get_object_or_404(Page, survey__id=survey_id, rank=page_num)

    # Update the group so the given page is the current one
    group.page = page
    group.save()

    questions = {}
    for question in group.page.question_set.all():
        questions[f"question-{question.id}"] = question

    if request.method == 'POST':
        form = group.get_form(request.POST)

        passed = form.is_valid()
        group.save_values(form.cleaned_data)

        if passed:
            if page.next_page:
                return redirect("page", survey_id=survey_id, token=token,
                    page_num=page.next_page.rank)

            # No next page
            group.page = None
            group.save()
            return redirect("done", survey_id=survey_id, token=token)
    else: # GET
        form = group.get_form()

    prev_url = ""
    if page.prev_page:
        prev_url = reverse("page", args=(survey_id, token, page.prev_page.rank))

    data = {
        "group": group,
        "questions": questions,
        "form": form,
        "QuestionTypes": QuestionTypes,
        "prev_url": prev_url,
    }

    return render(request, "fill_quiz.html", data)


def done(request, survey_id, token):
    group = get_object_or_404(AnswerGroup, survey__id=survey_id, token=token)

    page = Page.objects.filter(survey=group.survey).last()
    prev_url = reverse("page", args=(survey_id, token, page.rank))

    data = {
        "group": group,
        "prev_url": prev_url,
    }

    return render(request, "done.html", data)


@staff_member_required
def duplicate(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    count = Survey.objects.filter(slug__startswith=survey.slug).count() + 1

    new_survey = Survey.objects.create(name=survey.name, slug=survey.slug +
        str(count), logo=survey.logo, intro=survey.intro, outro=survey.outro)

    for page in survey.page_set.all():
        new_page = Page.objects.create(survey=new_survey, intro=page.intro)

        for question in page.question_set.all():
            Question.objects.create(question_type=question.question_type,
                question_text=question.question_text, page=new_page,
                required=question.required, choices=question.choices,
                choices_blank_allowed=question.choices_blank_allowed,
                num_answer_min=question.num_answer_min,
                num_answer_max=question.num_answer_max)

    # redirect to refresh page
    messages.add_message(request, messages.SUCCESS,
        f"Survey #{new_survey.id} created")
    return redirect('admin:core_survey_changelist')


def result_page(request, survey_id, token):
    if not token:
        raise Http404("Corrupted survey token")

    survey = get_object_or_404(Survey, id=survey_id, token=token)

    data = {
        "survey": survey,
    }
    return render(request, "result.html", data)


def result_question(request, q_id, token):
    if not token:
        raise Http404("Corrupted survey token")

    question = get_object_or_404(Question, id=q_id, page__survey__token=token)
    survey = question.page.survey

    survey_dir = Path(settings.MEDIA_ROOT) / f"s{survey.id}"
    survey_dir.mkdir(exist_ok=True)

    # graphs have a file name format of "q-Q_ID-EPOCH.svg", search for
    # anything that corresponds to this question
    files = list(survey_dir.glob(f'q-{question.id}-*.svg'))
    if len(files) >= 1:
        file = files[0]
        cached_url = settings.MEDIA_URL + f"s{survey.id}/{file.name}"

        # Check if graph is up to date
        latest = Answer.objects.filter(question=question
            ).order_by("-updated").first()

        if latest is None:
            # No Answers, but have a graph, must be a graph showing that there
            # are no answers, just show it
            return render(request, "snippets/graph.html", {"url":cached_url})

        # Have answers, check if they're more recent than the graph
        file_date = int(EPOCH_PART.match(file.name)[1])
        if latest.updated.timestamp() < file_date:
            # File was generated after most recent Answer
            return render(request, "snippets/graph.html", {"url":cached_url})

        # else: files are out of date, erase them before generating a new one
        for path in files:
            path.unlink()

    # Generate a new graph
    result = question.generate_graph(survey, survey_dir)
    url = None
    if result:
        url = settings.MEDIA_URL + f"s{survey.id}/{result.name}"

    return render(request, "snippets/graph.html", {"url":url})
