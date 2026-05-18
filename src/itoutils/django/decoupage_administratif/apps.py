from django.apps import AppConfig


class DecoupageAdministratifConfig(AppConfig):
    # L'objectif de cette app est uniquement de pouvoir :
    #   - analyser un code géographique via get_division_info_for_division_code()
    #   - convertir une liste de codes géographiques en noms en français via get_division_label()
    # Les données géographiques importées de l'API Découpage Administratif servent uniquement à cet usage
    # et n'ont pas pour objectif de constituer une base de référence.
    # Nous sommes conscients de la duplication de code avec sync_cities, à corriger à l'avenir.
    name = "itoutils.django.decoupage_administratif"
    verbose_name = "Découpage administratif"
