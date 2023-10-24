def ovc_age(age):
    return '18+' if age>=18 else '18+'

def age_to_correct(age):
    return 'aCorrige' if age == -1 else 'normal'

def gender(gender):
    if gender == 'fanm':
        return "Female"
    elif gender == 'gason':
        return 'Male'