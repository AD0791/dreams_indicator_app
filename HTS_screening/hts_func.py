def hts_eligible(score):
    return 'yes' if score >= FSCREENS.total_score.mean().round() else 'no'
