
from dataclasses import dataclass
from pydantic.dataclasses import dataclass as pdt
from typing import TypeVar
from agyw_path import *
from agyw import AgywPrev
from pandas import DataFrame


DF = TypeVar('pandas.core.frame.DataFrame')


base = AgywPrev().data_dreams_valid
base_table = base.pivot_table(index='age_range', values='id_patient', columns='departement', aggfunc='count', fill_value=0, margins=True,
                              margins_name="Total"
                              )[:-1]
base_table = base_table.reset_index().rename_axis(None, axis=1)
base_table = DataFrame(base_table.to_records(index=False))


@dataclass
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

    muso_1014: int = base1014[(
        base1014.muso == "yes")].id_patient.count()
    muso_1519: int = base1519[(
        base1519.muso == "yes")].id_patient.count()
    muso_2024: int = base2024[(
        base2024.muso == "yes")].id_patient.count()

    gardening_1014: int = base1014[(
        base1014.gardening == "yes")].id_patient.count()
    gardening_1519: int = base1519[(
        base1519.gardening == "yes")].id_patient.count()
    gardening_2024: int = base2024[(
        base2024.gardening == "yes")].id_patient.count()
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


@pdt
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
    muso: str = "Muso"
    gardening: str = "Gardening"
    # primary package
    ps1519: str = "Social Asset Building and Community-based HIV & Violence Prevention & condoms"
    ps2024: str = "Social Asset Building and Community-based HIV & Violence Prevention & condoms"
    package: str = "Primary package"


@dataclass
class Total(LayerServicesData):
    @property
    def package(self):
        if not self.ps_1014:
            self.ps_1014 = 0
        if not self.ps_1519:
            self.ps_1519 = 0
        if not self.ps_2024:
            self.ps_2024 = 0
        total = self.ps_1014 + self.ps_1519 + self.ps_2024
        return total if total else 0

    @property
    def curriculum(self):
        if not self.curriculum_1014:
            self.curriculum_1014 = 0
        if not self.curriculum_1519:
            self.curriculum_1519 = 0
        if not self.curriculum_2024:
            self.curriculum_2024 = 0
        total = self.curriculum_1014 + self.curriculum_1519 + self.curriculum_2024
        return total if total else 0

    @property
    def condoms(self):
        if not self.condom_1014:
            self.condom_1014 = 0
        if not self.condom_1519:
            self.condom_1519 = 0
        if not self.condom_2024:
            self.condom_2024 = 0
        total = self.condom_1014 + self.condom_1519 + self.condom_2024
        return total if total else 0

    @property
    def hts(self):
        if not self.hts_1014:
            self.hts_1014 = 0
        if not self.hts_1519:
            self.hts_1519 = 0
        if not self.hts_2024:
            self.hts_2024 = 0
        total = self.hts_1014 + self.hts_1519 + self.hts_2024
        return total if total else 0

    @property
    def schooling(self):
        if not self.schooling_1014:
            self.schooling_1014 = 0
        if not self.schooling_1519:
            self.schooling_1519 = 0
        if not self.schooling_2024:
            self.schooling_2024 = 0
        total = self.schooling_1014 + self.schooling_1519 + self.schooling_2024
        return total if total else 0

    @property
    def gardening(self):
        if not self.gardening_1014:
            self.gardening_1014 = 0
        if not self.gardening_1519:
            self.gardening_1519 = 0
        if not self.gardening_2024:
            self.gardening_2024 = 0
        total = self.gardening_1014 + self.gardening_1519 + self.gardening_2024
        return total if total else 0

    @property
    def muso(self):
        if not self.muso_1014:
            self.muso_1014 = 0
        if not self.muso_1519:
            self.muso_1519 = 0
        if not self.muso_2024:
            self.muso_2024 = 0
        total = self.muso_1014 + self.muso_1519 + self.muso_2024
        return total if total else 0

    @property
    def socioeco(self):
        if not self.socioeco_app_1014:
            self.socioeco_app_1014 = 0
        if not self.socioeco_app_1519:
            self.socioeco_app_1519 = 0
        if not self.socioeco_app_2024:
            self.socioeco_app_2024 = 0
        total = self.socioeco_app_1014 + self.socioeco_app_1519 + self.socioeco_app_2024
        return total if total else 0

    @property
    def contraceptive(self):
        if not self.contraceptive_1014:
            self.contraceptive_1014 = 0
        if not self.contraceptive_1519:
            self.contraceptive_1519 = 0
        if not self.contraceptive_2024:
            self.contraceptive_2024 = 0
        total = self.contraceptive_1014 + self.contraceptive_1519 + self.contraceptive_2024
        return total if total else 0

    @property
    def prep(self):
        if not self.prep_1014:
            self.prep_1014 = 0
        if not self.prep_1519:
            self.prep_1519 = 0
        if not self.prep_2024:
            self.prep_2024 = 0
        total = self.prep_1014 + self.prep_1519 + self.prep_2024
        return total if total else 0

    @property
    def vbg(self):
        if not self.vbg_1014:
            self.vbg_1014 = 0
        if not self.vbg_1519:
            self.vbg_1519 = 0
        if not self.vbg_2024:
            self.vbg_2024 = 0
        total = self.vbg_1014 + self.vbg_1519 + self.vbg_2024
        return total if total else 0

    @property
    def gyneco(self):
        if not self.gyneco_1014:
            self.gyneco_1014 = 0
        if not self.gyneco_1519:
            self.gyneco_1519 = 0
        if not self.gyneco_2024:
            self.gyneco_2024 = 0
        total = self.gyneco_1014 + self.gyneco_1519 + self.gyneco_2024
        return total if total else 0

    @property
    def parenting(self):
        if not self.parenting_1014:
            self.parenting_1014 = 0
        if not self.parenting_1519:
            self.parenting_1519 = 0
        if not self.parenting_2024:
            self.parenting_2024 = 0
        total = self.parenting_1014 + self.parenting_1519 + self.parenting_2024
        return total if total else 0
