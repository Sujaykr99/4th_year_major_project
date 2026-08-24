#!/usr/bin/env python3
"""
Placement Readiness Scorer
Separate from Career Model - uses academic + experience features
Outputs: Readiness Score (0-100) + Readiness Level
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import warnings
warnings.filterwarnings("ignore")


class ReadinessLevel(Enum):
    NOT_READY = "Not Ready"
    NEEDS_IMPROVEMENT = "Needs Improvement"
    MODERATELY_READY = "Moderately Ready"
    READY = "Ready"
    HIGHLY_READY = "Highly Ready"


@dataclass
class ReadinessResult:
    score: float  # 0-100
    level: ReadinessLevel
    breakdown: Dict[str, float]
    recommendations: list


class ReadinessScorer:
    """
    Calculates placement readiness based on academic + experience profile.
    Independent of career prediction model.
    """

    # Weights for each component (must sum to 1.0)
    WEIGHTS = {
        "academic": 0.25,       # CGPA, backlogs
        "technical_skills": 0.20,   # Skill breadth/depth
        "projects": 0.20,         # Quantity + relevance
        "experience": 0.15,       # Internships, work exp
        "soft_skills": 0.10,      # Communication, leadership
        "achievements": 0.10,     # Certs, hackathons, GitHub
    }

    def __init__(self):
        self.feature_ranges = {
            "cgpa": (5.0, 10.0),
            "backlogs": (0, 5),
            "total_projects": (0, 15),
            "web_projects": (0, 8),
            "ai_ml_projects": (0, 5),
            "mobile_projects": (0, 4),
            "internship_count": (0, 4),
            "internship_duration_months": (0, 12),
            "certifications": (0, 8),
            "hackathons": (0, 6),
            "github_repos": (0, 30),
            "communication": (0, 100),
            "aptitude": (0, 100),
            "problem_solving": (0, 100),
            "leadership": (0, 100),
        }

    def _normalize(self, value: float, min_val: float, max_val: float, invert: bool = False) -> float:
        """Normalize value to 0-100 scale."""
        if max_val == min_val:
            return 50.0
        normalized = (value - min_val) / (max_val - min_val) * 100
        normalized = np.clip(normalized, 0, 100)
        return 100 - normalized if invert else normalized

    def _academic_score(self, features: Dict[str, Any]) -> float:
        """Academic component: CGPA (positive) + Backlogs (negative)."""
        cgpa = features.get("cgpa", 7.0)
        backlogs = features.get("backlogs", 0)

        cgpa_score = self._normalize(cgpa, 5.0, 10.0)
        backlog_score = self._normalize(backlogs, 0, 5, invert=True)

        # Weight: 80% CGPA, 20% backlogs
        return 0.8 * cgpa_score + 0.2 * backlog_score

    def _technical_skills_score(self, features: Dict[str, Any]) -> float:
        """Technical skills: breadth (count of skills > 50) + depth (avg score)."""
        skill_keys = [k for k in features.keys() if k.startswith("skill_")]
        if not skill_keys:
            return 30.0  # Default if no skill data

        skill_scores = [features[k] for k in skill_keys]
        avg_score = np.mean(skill_scores)
        skill_count = sum(1 for s in skill_scores if s > 50)

        # Depth (avg score) + Breadth (count)
        depth_score = avg_score  # Already 0-100
        breadth_score = self._normalize(skill_count, 0, 20)  # Max 20 skills

        return 0.6 * depth_score + 0.4 * breadth_score

    def _projects_score(self, features: Dict[str, Any]) -> float:
        """Projects: total + domain relevance."""
        total = features.get("total_projects", 0)
        web = features.get("web_projects", 0)
        ai_ml = features.get("ai_ml_projects", 0)
        mobile = features.get("mobile_projects", 0)

        total_score = self._normalize(total, 0, 15)
        diversity_score = self._normalize(web + ai_ml + mobile, 0, 10)

        return 0.7 * total_score + 0.3 * diversity_score

    def _experience_score(self, features: Dict[str, Any]) -> float:
        """Experience: internships + duration."""
        count = features.get("internship_count", 0)
        duration = features.get("internship_duration_months", 0)

        count_score = self._normalize(count, 0, 4)
        duration_score = self._normalize(duration, 0, 12)

        return 0.6 * count_score + 0.4 * duration_score

    def _soft_skills_score(self, features: Dict[str, Any]) -> float:
        """Soft skills: average of 4 dimensions."""
        comm = features.get("communication", 50)
        apt = features.get("aptitude", 50)
        prob = features.get("problem_solving", 50)
        lead = features.get("leadership", 50)

        return np.mean([comm, apt, prob, lead])

    def _achievements_score(self, features: Dict[str, Any]) -> float:
        """Achievements: certs + hackathons + GitHub."""
        certs = features.get("certifications", 0)
        hacks = features.get("hackathons", 0)
        repos = features.get("github_repos", 0)

        cert_score = self._normalize(certs, 0, 8)
        hack_score = self._normalize(hacks, 0, 6)
        repo_score = self._normalize(repos, 0, 30)

        return 0.4 * cert_score + 0.3 * hack_score + 0.3 * repo_score

    def calculate(self, features: Dict[str, Any]) -> ReadinessResult:
        """Calculate overall readiness score."""
        # Component scores
        components = {
            "academic": self._academic_score(features),
            "technical_skills": self._technical_skills_score(features),
            "projects": self._projects_score(features),
            "experience": self._experience_score(features),
            "soft_skills": self._soft_skills_score(features),
            "achievements": self._achievements_score(features),
        }

        # Weighted total
        total_score = sum(
            components[comp] * self.WEIGHTS[comp]
            for comp in self.WEIGHTS
        )

        # Determine level
        if total_score >= 80:
            level = ReadinessLevel.HIGHLY_READY
        elif total_score >= 65:
            level = ReadinessLevel.READY
        elif total_score >= 50:
            level = ReadinessLevel.MODERATELY_READY
        elif total_score >= 35:
            level = ReadinessLevel.NEEDS_IMPROVEMENT
        else:
            level = ReadinessLevel.NOT_READY

        # Generate recommendations
        recommendations = self._generate_recommendations(components, features)

        return ReadinessResult(
            score=round(total_score, 1),
            level=level,
            breakdown={k: round(v, 1) for k, v in components.items()},
            recommendations=recommendations
        )

    def _generate_recommendations(self, components: Dict[str, float],
                                   features: Dict[str, Any]) -> list:
        """Generate actionable recommendations based on weak areas."""
        recs = []

        # Sort components by score (ascending)
        sorted_components = sorted(components.items(), key=lambda x: x[1])

        # Top 2 weakest areas
        for comp, score in sorted_components[:2]:
            if comp == "academic":
                if features.get("cgpa", 7) < 7.5:
                    recs.append("Focus on improving CGPA - target 8.0+ for top companies")
                if features.get("backlogs", 0) > 0:
                    recs.append("Clear all backlogs before placement season")

            elif comp == "technical_skills":
                skill_keys = [k for k in features.keys() if k.startswith("skill_")]
                weak_skills = [k.replace("skill_", "") for k in skill_keys if features[k] < 40]
                if weak_skills:
                    recs.append(f"Strengthen core skills: {', '.join(weak_skills[:3])}")

            elif comp == "projects":
                recs.append("Build 2-3 more substantial projects with deployment")
                if features.get("web_projects", 0) == 0:
                    recs.append("Add a full-stack web project to portfolio")
                if features.get("ai_ml_projects", 0) == 0:
                    recs.append("Consider an ML project to demonstrate applied skills")

            elif comp == "experience":
                recs.append("Secure at least 1 internship before graduation")
                recs.append("Contribute to open source for practical experience")

            elif comp == "soft_skills":
                weak = []
                if features.get("communication", 50) < 60:
                    weak.append("communication")
                if features.get("leadership", 50) < 55:
                    weak.append("leadership")
                if weak:
                    recs.append(f"Improve soft skills: {', '.join(weak)}")

            elif comp == "achievements":
                if features.get("certifications", 0) < 2:
                    recs.append("Earn 1-2 relevant certifications (AWS, Azure, etc.)")
                if features.get("hackathons", 0) == 0:
                    recs.append("Participate in 1-2 hackathons")
                if features.get("github_repos", 0) < 5:
                    recs.append("Build GitHub portfolio with 5+ quality repositories")

        return recs[:5]  # Top 5 recommendations


def score_from_student_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for API integration."""
    scorer = ReadinessScorer()
    result = scorer.calculate(profile)
    return {
        "readiness_score": result.score,
        "readiness_level": result.level.value,
        "component_breakdown": result.breakdown,
        "recommendations": result.recommendations
    }


if __name__ == "__main__":
    # Demo with sample profiles
    scorer = ReadinessScorer()

    # Strong candidate
    strong = {
        "cgpa": 8.8, "backlogs": 0,
        "skill_python": 90, "skill_java": 75, "skill_javascript": 85,
        "skill_react": 88, "skill_nodejs": 80, "skill_sql": 82,
        "skill_aws": 70, "skill_docker": 75, "skill_git": 90,
        "total_projects": 6, "web_projects": 3, "ai_ml_projects": 2,
        "internship_count": 2, "internship_duration_months": 8,
        "certifications": 3, "hackathons": 2, "github_repos": 12,
        "communication": 85, "aptitude": 80, "problem_solving": 88, "leadership": 75
    }

    # Average candidate
    average = {
        "cgpa": 7.2, "backlogs": 1,
        "skill_python": 65, "skill_java": 55, "skill_javascript": 60,
        "skill_react": 50, "skill_nodejs": 45, "skill_sql": 55,
        "skill_aws": 30, "skill_docker": 35, "skill_git": 60,
        "total_projects": 3, "web_projects": 1, "ai_ml_projects": 0,
        "internship_count": 1, "internship_duration_months": 3,
        "certifications": 1, "hackathons": 0, "github_repos": 4,
        "communication": 65, "aptitude": 60, "problem_solving": 65, "leadership": 50
    }

    # Weak candidate
    weak = {
        "cgpa": 6.0, "backlogs": 2,
        "skill_python": 40, "skill_java": 35, "skill_javascript": 30,
        "skill_react": 20, "skill_nodejs": 15, "skill_sql": 25,
        "skill_aws": 10, "skill_docker": 10, "skill_git": 30,
        "total_projects": 1, "web_projects": 0, "ai_ml_projects": 0,
        "internship_count": 0, "internship_duration_months": 0,
        "certifications": 0, "hackathons": 0, "github_repos": 1,
        "communication": 45, "aptitude": 40, "problem_solving": 40, "leadership": 35
    }

    for name, profile in [("Strong Candidate", strong), ("Average Candidate", average), ("Weak Candidate", weak)]:
        result = scorer.calculate(profile)
        print(f"\n{'='*50}")
        print(f"{name}")
        print(f"{'='*50}")
        print(f"Readiness Score: {result.score}/100")
        print(f"Level: {result.level.value}")
        print(f"Breakdown: {result.breakdown}")
        print(f"Recommendations:")
        for i, r in enumerate(result.recommendations, 1):
            print(f"  {i}. {r}")

    # Save scorer config
    config = {
        "weights": scorer.WEIGHTS,
        "feature_ranges": {k: list(v) for k, v in scorer.feature_ranges.items()},
        "levels": [l.value for l in ReadinessLevel]
    }
    with open("readiness_scorer_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("\nConfig saved to readiness_scorer_config.json")