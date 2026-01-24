from pytrends.request import TrendReq
import time

def fetch_trend_scores(skills, geo=""):
# Fetch Google Trends interest scores for skills. Returns normalized scores in [0,1].
    pytrends = TrendReq(hl="en-US", tz=360)
    trend_scores = {}

    for skill in skills:
        try:
            pytrends.build_payload(
                [skill],
                timeframe="today 12-m",
                geo=geo
            )
            data = pytrends.interest_over_time()
            if not data.empty:
                score = data[skill].mean()
                trend_scores[skill] = score
            else:
                trend_scores[skill] = 0.0
            time.sleep(1) 

        except Exception:
            trend_scores[skill] = 0.0

    max_score = max(trend_scores.values()) or 1
    for k in trend_scores:
        trend_scores[k] = trend_scores[k] / max_score

    return trend_scores
