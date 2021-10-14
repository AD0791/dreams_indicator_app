def test_indication(test):
    return "ni" if test == "0," else 'no'

def test_evaluation(test):
    if (test=="0,,2," or test=="2,"):
        return "negative"
    if test== "1,":
        return "positive"
    if test=="0,":
        return 'no'
    
def arv(test):
    return '---' if test == "1," else 'no'

#------------------------------------------------------------------------------------------------------------------------
def ovc_hivstat_children(index,positive,negative,on_arv,not_on_arv,not_indicated):
    """
    elif len(positive) == 0 and len(negative) == 0 and len(not_indicated)==0:
        ovc_hivstat_children = children_unknown_status
        ovc_hivstat_children = ovc_hivstat_children.sort_values('commune').reset_index(drop=True)
        ovc_hivstat_children[['positive','on arv', 'not on arv', 'negative','test not indicated']] = 0
        ovc_hivstat_children = ovc_hivstat_children.reindex(columns = index)
        return ovc_hivstat_children
    """
    if len(positive) != 0 and len(on_arv) != 0 and len(not_on_arv) != 0 and len(negative) != 0 and len(not_indicated)!=0:
        ovc_hivstat_children = positive.merge(on_arv, on = 'commune', how = 'outer').merge(not_on_arv, on = 'commune', how = 'outer').merge(negative, on = 'commune', how = 'outer').merge(not_indicated, on = 'commune', how = 'outer')
        ovc_hivstat_children = ovc_hivstat_children.sort_values('commune').reset_index(drop=True)
        ovc_hivstat_children['No HIV reported (Status Unknown)'] = 0
        ovc_hivstat_children = ovc_hivstat_children.reindex(columns = index)        
        return ovc_hivstat_children
    elif len(positive) != 0 and len(on_arv) == 0 and len(not_on_arv) != 0 and len(negative) != 0 and len(not_indicated)!=0:
        ovc_hivstat_children = positive.merge(not_on_arv, on = 'commune', how = 'outer').merge(negative, on = 'commune', how = 'outer').merge(not_indicated, on = 'commune', how = 'outer')
        ovc_hivstat_children = ovc_hivstat_children.sort_values('commune').reset_index(drop=True)
        ovc_hivstat_children['on_arv','No HIV reported (Status Unknown)'] = 0
        ovc_hivstat_children = ovc_hivstat_children.reindex(columns = index)        
        return ovc_hivstat_children
    elif len(positive) != 0 and len(on_arv) != 0 and len(not_on_arv) == 0 and len(negative) != 0 and len(not_indicated)!=0:
        ovc_hivstat_children = positive.merge(on_arv, on = 'commune', how = 'outer').merge(negative, on = 'commune', how = 'outer').merge(not_indicated, on = 'commune', how = 'outer')
        ovc_hivstat_children = ovc_hivstat_children.sort_values('commune').reset_index(drop=True)
        ovc_hivstat_children['not_on_arv','No HIV reported (Status Unknown)'] = 0
        ovc_hivstat_children = ovc_hivstat_children.reindex(columns = index)        
        return ovc_hivstat_children
    elif len(positive) == 0 and len(negative) != 0 and len(not_indicated)!=0:
        ovc_hivstat_children = negative.merge(not_indicated, on = 'commune', how = 'outer')
        ovc_hivstat_children = ovc_hivstat_children.sort_values('commune').reset_index(drop=True)
        ovc_hivstat_children[['positive','on arv', 'not on arv','No HIV reported (Status Unknown)']] = 0
        ovc_hivstat_children = ovc_hivstat_children.reindex(columns = index)
        return ovc_hivstat_children
    else:
        return 'HIV test data are not available right now!!'