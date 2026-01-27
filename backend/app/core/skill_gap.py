def compute_skill_gap(industry_demand: dict, learner_belief: dict):
#Gap(s) = Demand(s) * (1 - Belief(s))
    gap_scores = {}
    for skill, demand_score in industry_demand.items():
        belief = learner_belief.get(skill, 0.1)  # unseen skills = low belief
        gap = demand_score * (1 - belief)

        if gap > 0:
            gap_scores[skill] = gap

    return dict(sorted(gap_scores.items(), key=lambda x: x[1], reverse=True))
