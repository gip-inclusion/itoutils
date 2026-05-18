from django.db import models


class AdminDivisionType(models.TextChoices):
    CITY = ("city", "Commune")
    EPCI = ("epci", "Intercommunalité (EPCI)")
    DEPARTMENT = ("department", "Département")
    REGION = ("region", "Région")
    COUNTRY = ("country", "France entière")


class AdminDivision(models.Model):
    """Base model for administrative divisions."""

    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class City(AdminDivision):
    code = models.CharField(max_length=5, primary_key=True)
    department = models.CharField(max_length=3, db_index=True)

    class Meta:
        verbose_name = "commune"
        verbose_name_plural = "communes"


class Department(AdminDivision):
    code = models.CharField(max_length=3, primary_key=True)
    region = models.CharField(max_length=3, db_index=True)

    class Meta:
        verbose_name = "département"
        verbose_name_plural = "départements"


class EPCI(AdminDivision):
    code = models.CharField(max_length=9, primary_key=True)

    class Meta:
        verbose_name = "EPCI"
        verbose_name_plural = "EPCI"


class Region(AdminDivision):
    code = models.CharField(max_length=3, primary_key=True)

    class Meta:
        verbose_name = "région"
        verbose_name_plural = "régions"
