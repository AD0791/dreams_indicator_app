from pandas import DataFrame
from active import actif_served as AGYW_ACTIF


class Preventive:
    """A class with properties and methods in DATIM format evidence-based intervention focused on preventing violence within the reporting period."""
    __who_am_I = "PREV"
    __title = "Number of AGYW that received an evidence-based intervention focused on preventing violence within the reporting period."

    def __repr__(self):
        return f"<Preventive {self.__i_am}>"

    def __str__(self):
        return f"<Preventive {self.__i_am}>"

    @classmethod
    def title(cls):
        return cls.__title

    def __init__(self, commune=None):
        self.__commune = commune
        self.__i_am = f"{Preventive.__who_am_I}"
        self.__data = AGYW_ACTIF
        if self.__commune == None:
            self.__dreams_valid = self.__data[(self.__data.age_range != "not_valid_age") & (
                self.__data.age_range != "25-29")]
        else:
            self.__dreams_valid = self.__data[(self.__data.age_range != "not_valid_age") & (
                self.__data.age_range != "25-29") & (self.__data.commune == f"{self.__commune}")]
        self.__total_dreams_valid = self.__dreams_valid.id_patient.count()
        self.__preventive_violence = self.__dreams_valid[self.__dreams_valid.has_preventive_vbg=="yes"]
        self.__total_preventive_violence = self.__preventive_violence.id_patient.count()
        
    @property
    def who_am_i(self):
        return self.__i_am
    
    @property
    def data_mastersheet(self):
        return self.__data


    @property
    def data_dreams_valid(self):
        return self.__dreams_valid

    @property
    def total_dreams_valid(self):
        return self.__total_dreams_valid

    @property
    def data_preventive_violence(self):
        return self.__preventive_violence

    @property
    def total_preventive_violence(self):
        return self.__total_preventive_violence

    
    __PERIOD_DATIM = sorted(list(AGYW_ACTIF.month_in_program_range.unique()))
    __PERIOD_DATIM.append("Total")
    __AGE_DATIM = sorted(list(AGYW_ACTIF.age_range.unique())[0:3])

    def datim_preventive_violence(self):
        try:
            pivotableI = self.__preventive_violence.rename(
                columns={"age_range": "Age", "month_in_program_range": "Time"})
            preventive_pivot = pivotableI.pivot_table(index="Age", columns="Time", values="id_patient",
                                                      aggfunc="count", fill_value=0, margins=True, margins_name="Total", dropna=False)[:-1]
            columns_pivotI = list(preventive_pivot.columns)
            indexes_pivotI = list(preventive_pivot.index)
            for period in Preventive.__PERIOD_DATIM:
                if period not in columns_pivotI:
                    preventive_pivot[period] = 0
            for age in Preventive.__AGE_DATIM:
                if age not in indexes_pivotI:
                    preventive_pivot.loc[age] = 0
            preventive_pivot = preventive_pivot.reindex(
                index=Preventive.__AGE_DATIM, columns=Preventive.__PERIOD_DATIM)
            preventive_pivot_final = preventive_pivot.reset_index().rename_axis(None, axis=1)
            preventive_results_final = DataFrame(
                preventive_pivot_final.to_records(index=False))
        except ValueError:
            preventive_results_final = DataFrame({"Age": ["10-14", "15-19",
                                                          "20-24"],
                                                  "0-6 months": [0, 0, 0],
                                                  "07-12 months": [0, 0, 0],
                                                  "13-24 months": [0, 0, 0],
                                                  "25+ months": [0, 0, 0],
                                                  "Total": [0, 0, 0]
                                                  })
        return preventive_results_final


class PreventiveCommune(Preventive):
    """A class that extend Preventive Class by commune"""
    __who_am_I = "PREV"

    def __init__(self, name):
        self.__name = name
        self.__i_am = f"{PreventiveCommune.__who_am_I} {self.__name}"
        super().__init__(self.__name)

    @property
    def who_am_i(self):
        return self.__i_am

    def __repr__(self):
        return f"<PreventiveCommune {self.__i_am}>"

    def __str__(self):
        return f"<PreventiveCommune {self.__i_am}>"
