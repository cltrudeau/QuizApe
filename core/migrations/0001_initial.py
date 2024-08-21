# Generated by Django 5.1 on 2024-08-21 21:21

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('rank', models.PositiveSmallIntegerField(db_index=True)),
                ('intro', models.TextField()),
            ],
            options={
                'ordering': ['rank'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='')),
                ('editable', models.BooleanField(default=False)),
                ('token', models.CharField(db_index=True, default='', max_length=20)),
                ('intro', models.TextField()),
                ('outro', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AnswerGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('token', models.CharField(db_index=True, max_length=20)),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.page')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.survey')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('rank', models.PositiveSmallIntegerField(db_index=True)),
                ('question_type', models.CharField(choices=[('B', 'Boolean'), ('N', 'Num'), ('S', 'Star'), ('T', 'Text'), ('C', 'Choice')], max_length=1)),
                ('question_text', models.TextField()),
                ('required', models.BooleanField(default=True)),
                ('choices', models.JSONField(blank=True, null=True)),
                ('choices_blank_allowed', models.BooleanField(default=False)),
                ('num_answer_min', models.IntegerField(blank=True, null=True)),
                ('num_answer_max', models.IntegerField(blank=True, null=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.page')),
            ],
            options={
                'ordering': ['rank'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('bool_answer', models.BooleanField(blank=True, null=True)),
                ('num_answer', models.IntegerField(blank=True, null=True)),
                ('star_answer', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('text_answer', models.TextField(blank=True, null=True)),
                ('choices_answer', models.CharField(blank=True, max_length=50, null=True)),
                ('answer_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.answergroup')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.question')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='page',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.survey'),
        ),
    ]
