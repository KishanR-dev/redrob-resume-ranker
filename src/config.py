from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass(frozen=True)
class RankingConfig:
    target_role_keywords: Set[str] = field(
        default_factory=lambda: {
            "ai engineer",
            "ml engineer",
            "machine learning engineer",
            "nlp engineer",
            "search engineer",
            "recommendation systems engineer",
            "applied ml engineer",
            "ranking engineer",
            "retrieval engineer",
            "relevance engineer",
            "search relevance engineer",
            "recommender systems engineer",
        }
    )
    title_tier_gold: Set[str] = field(
        default_factory=lambda: {
            "ranking engineer",
            "search engineer",
            "retrieval engineer",
            "relevance engineer",
            "recommendation systems engineer",
            "recommender systems engineer",
            "search relevance engineer",
        }
    )
    title_tier_strong: Set[str] = field(
        default_factory=lambda: {
            "ai engineer",
            "ml engineer",
            "machine learning engineer",
            "applied ml engineer",
            "nlp engineer",
            "ml scientist",
            "data scientist",
        }
    )
    title_tier_adjacent: Set[str] = field(
        default_factory=lambda: {
            "backend engineer",
            "software engineer",
            "data engineer",
            "analytics engineer",
            "platform engineer",
            "sde",
        }
    )
    title_tier_risky_ai: Set[str] = field(
        default_factory=lambda: {
            "genai intern",
            "prompt engineer",
            "llm trainer",
            "ai content",
            "ai evangelist",
        }
    )
    title_tier_off_target: Set[str] = field(
        default_factory=lambda: {
            "marketing manager",
            "graphic designer",
            "civil engineer",
            "accountant",
            "hr manager",
            "content writer",
            "operations manager",
            "sales executive",
            "customer support",
            "business development",
            "recruiter",
        }
    )
    positive_skill_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "embeddings": 1.0,
            "vector search": 1.0,
            "information retrieval": 1.0,
            "ranking": 0.9,
            "learning-to-rank": 1.0,
            "ndcg": 0.8,
            "map": 0.8,
            "mrr": 0.8,
            "ab testing": 0.8,
            "evaluation": 0.7,
            "sentence transformers": 0.9,
            "faiss": 0.8,
            "pinecone": 0.8,
            "qdrant": 0.8,
            "milvus": 0.8,
            "opensearch": 0.8,
            "elasticsearch": 0.8,
            "bm25": 0.7,
            "python": 0.7,
            "xgboost": 0.6,
            "lightgbm": 0.6,
            "feature engineering": 0.6,
            "mlops": 0.5,
            "rag": 0.4,
        }
    )
    negative_title_keywords: Set[str] = field(
        default_factory=lambda: {
            "marketing manager",
            "graphic designer",
            "civil engineer",
            "accountant",
            "hr manager",
            "content writer",
            "operations manager",
            "sales executive",
            "customer support",
        }
    )
    preferred_locations_strong: Set[str] = field(default_factory=lambda: {"pune", "noida"})
    preferred_locations_secondary: Set[str] = field(
        default_factory=lambda: {
            "bangalore",
            "bengaluru",
            "hyderabad",
            "gurgaon",
            "delhi ncr",
            "new delhi",
            "mumbai",
            "chennai",
            "kolkata",
            "ahmedabad",
            "remote india",
            "india",
        }
    )
    non_preferred_global_locations: Set[str] = field(
        default_factory=lambda: {
            "london",
            "singapore",
            "berlin",
            "seattle",
            "new york",
            "austin",
            "toronto",
            "sydney",
            "san francisco",
            "vancouver",
            "dublin",
        }
    )
    consulting_companies: Set[str] = field(
        default_factory=lambda: {
            "tcs",
            "infosys",
            "wipro",
            "accenture",
            "cognizant",
            "capgemini",
            "hcl",
            "tech mahindra",
            "mindtree",
        }
    )
    preferred_industries: Set[str] = field(
        default_factory=lambda: {
            "software",
            "ai/ml",
            "fintech",
            "food delivery",
            "e-commerce",
            "transportation",
            "internet",
            "saas",
        }
    )
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "jd_fit": 0.33,
            "title_quality": 0.24,
            "location": 0.14,
            "skills": 0.02,
            "experience": 0.05,
            "behavior": 0.18,
            "reliability": 0.04,
        }
    )
