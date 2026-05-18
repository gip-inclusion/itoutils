from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=5, primary_key=True, serialize=False)),
                ("department", models.CharField(db_index=True, max_length=3)),
            ],
            options={
                "verbose_name": "commune",
                "verbose_name_plural": "communes",
            },
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=3, primary_key=True, serialize=False)),
                ("region", models.CharField(db_index=True, max_length=3)),
            ],
            options={
                "verbose_name": "département",
                "verbose_name_plural": "départements",
            },
        ),
        migrations.CreateModel(
            name="EPCI",
            fields=[
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=9, primary_key=True, serialize=False)),
            ],
            options={
                "verbose_name": "EPCI",
                "verbose_name_plural": "EPCI",
            },
        ),
        migrations.CreateModel(
            name="Region",
            fields=[
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=3, primary_key=True, serialize=False)),
            ],
            options={
                "verbose_name": "région",
                "verbose_name_plural": "régions",
            },
        ),
    ]
