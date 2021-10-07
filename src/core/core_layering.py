from typing import TypeVar
from pydantic.dataclasses import dataclass as pdt
from dataclasses import dataclass
from agyw import AgywPrev
from sys import path
path.insert(0, '../static')

DF = TypeVar('pandas.core.frame.DataFrame')

base = AgywPrev().data_dreams_valid


@dataclass(frozen=True)
class LayerServicesData:
    """convey the proper services data given for the time"""
    base1014: DF = base[base.age_range == "10-14"]
    base1519: DF = base[base.age_range == "15-19"]
    base2024: DF = base[base.age_range == "20-24"]
    # CURRICULUM
    curriculum_1014: int = base1014[(
        base1014.curriculum == "yes")].id_patient.count()
    curriculum_1519: int = base1519[(
        base1519.curriculum == "yes")].id_patient.count()
    curriculum_2024: int = base2024[(
        base2024.curriculum == "yes")].id_patient.count()
    # CONDOM
    condom_1014: int = base1014[(base1014.condom == "yes")].id_patient.count()
    condom_1519: int = base1519[(base1519.condom == "yes")].id_patient.count()
    condom_2024: int = base2024[(base2024.condom == "yes")].id_patient.count()
    # HTS
    hts_1014: int = base1014[(base1014.hts == "yes")].id_patient.count()
    hts_1519: int = base1519[(base1519.hts == "yes")].id_patient.count()
    hts_2024: int = base2024[(base2024.hts == "yes")].id_patient.count()
    # vbg
    vbg_1014: int = base1014[(base1014.vbg == "yes")].id_patient.count()
    vbg_1519: int = base1519[(base1519.vbg == "yes")].id_patient.count()
    vbg_2024: int = base2024[(base2024.vbg == "yes")].id_patient.count()
    # gynecologique
    gyneco_1014: int = base1014[(base1014.gyneco == "yes")].id_patient.count()
    gyneco_1519: int = base1519[(base1519.gyneco == "yes")].id_patient.count()
    gyneco_2024: int = base2024[(base2024.gyneco == "yes")].id_patient.count()
    # Post care Violence
    post_violence_care_1014: int = base1014[(
        base1014.post_violence_care == "yes")].id_patient.count()
    post_violence_care_1519: int = base1519[(
        base1519.post_violence_care == "yes")].id_patient.count()
    post_violence_care_2024: int = base2024[(
        base2024.post_violence_care == "yes")].id_patient.count()
    # socio eco approche
    socioeco_app_1014: int = base1014[(
        base1014.socioeco_app == "yes")].id_patient.count()
    socioeco_app_1519: int = base1519[(
        base1519.socioeco_app == "yes")].id_patient.count()
    socioeco_app_2024: int = base2024[(
        base2024.socioeco_app == "yes")].id_patient.count()
    # prep
    prep_1014: int = base1014[(base1014.prep == "yes")].id_patient.count()
    prep_1519: int = base1519[(base1519.prep == "yes")].id_patient.count()
    prep_2024: int = base2024[(base2024.prep == "yes")].id_patient.count()
    # primary
    ps_1014: int = base1014[(base1014.ps_1014 == "primary")].id_patient.count()
    ps_1519: int = base1519[(base1519.ps_1519 == "primary")].id_patient.count()
    ps_2024: int = base2024[(base2024.ps_2024 == "primary")].id_patient.count()

    # schooling
    # base1014[(base1014.schooling=="yes")].id_patient.count()
    schooling_1014: None = None
    # base1519[(base1519.schooling=="yes")].id_patient.count()
    schooling_1519: None = None
    # base2024[(base2024.schooling=="yes")].id_patient.count()
    schooling_2024: None = None
    # contraception
    contraceptive_1014: int = base1014[(
        base1014.contraceptive == "yes")].id_patient.count()
    contraceptive_1519: int = base1519[(
        base1519.contraceptive == "yes")].id_patient.count()
    contraceptive_2024: int = base2024[(
        base2024.contraceptive == "yes")].id_patient.count()
    # Parenting
    parenting_1014: int = base1014[(
        base1014.parenting == "yes")].id_patient.count()
    parenting_1519: int = base1519[(
        base1519.parenting == "yes")].id_patient.count()
    parenting_2024: int = base2024[(
        base2024.parenting == "yes")].id_patient.count()


@pdt(frozen=True)
class LayerServicesElements:
    """ convey the elements for the build of the table"""
    who_am_i: str = "Layering Table of Services"
    age1014: str = "Aged 10-14"
    age1519: str = "Aged 15-19"
    age2024: str = "Aged 20-24"
    # served or intervention
    status_served: str = "# served"
    status_int: str = "Intervention"
    # type intervention
    primary_intervention: str = "Primary Individual Interventions"
    secondary_intervention: str = "Secondary Individual Interventions"
    # packages
    curriculum: str = "Social Asset Building and Community-based HIV & Violence Prevention"
    condoms: str = "Condoms"
    hts: str = "HTS"
    vbg: str = "VBG"
    gyneco: str = "Gynecologique"
    post_care_violence: str = "Post-Violence-Care"
    schooling: str = "Education Subsidies"
    parenting: str = "Parenting/Caregiver Programming"
    socioeco: str = "Combination Socio-Economic Approaches"
    prep: str = "PREP"
    contraceptive: str = "Contraceptive-Mix"
    # primary package
    ps1519: str = "Social Asset Building and Community-based HIV & Violence Prevention & condoms"
    ps2024: str = "Social Asset Building and Community-based HIV & Violence Prevention & condoms"
