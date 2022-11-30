def hts_eligible(score):
    return 'yes' if score >= FSCREENS.total_score.mean().round() else 'no'


def fy22_eligible(score):
    return 'yes' if score >= fy22.total_score.mean().round() else 'no'
