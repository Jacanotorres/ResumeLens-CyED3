"""Stage 2 - Qualification normalization with finite-state transducers (pyformlang).

Each transducer reads a raw skill string character by character and emits its
canonical token, e.g. ``"React.js" -> "REACT"``. The normalized tokens are then
sorted in the canonical order of a given profile.
"""

from __future__ import annotations

from functools import lru_cache

from pyformlang.fst import FST

from resumelens.profiles import Profile


SKILL_VARIANTS: dict[str, str] = {
    "javascript": "JAVASCRIPT",
    "java script": "JAVASCRIPT",
    "js": "JAVASCRIPT",
    "typescript": "TYPESCRIPT",
    "type script": "TYPESCRIPT",
    "ts": "TYPESCRIPT",
    "python": "PYTHON",
    "java": "JAVA",
    "scala": "SCALA",
    "bash": "BASH",
    "react": "REACT",
    "react.js": "REACT",
    "react js": "REACT",
    "react. js": "REACT",
    "react .js": "REACT",
    "react . js": "REACT",
    "reactjs": "REACT",
    "angular": "ANGULAR",
    "angular.js": "ANGULAR",
    "angular js": "ANGULAR",
    "angular. js": "ANGULAR",
    "angular .js": "ANGULAR",
    "angular . js": "ANGULAR",
    "angularjs": "ANGULAR",
    "vue": "VUE",
    "vue.js": "VUE",
    "vue js": "VUE",
    "vue. js": "VUE",
    "vue .js": "VUE",
    "vue . js": "VUE",
    "vuejs": "VUE",
    "node": "NODE_JS",
    "node.js": "NODE_JS",
    "node js": "NODE_JS",
    "node. js": "NODE_JS",
    "node .js": "NODE_JS",
    "node . js": "NODE_JS",
    "nodejs": "NODE_JS",
    "express": "EXPRESS",
    "express.js": "EXPRESS",
    "express js": "EXPRESS",
    "express. js": "EXPRESS",
    "express .js": "EXPRESS",
    "express . js": "EXPRESS",
    "django": "DJANGO",
    "flask": "FLASK",
    "spring boot": "SPRING_BOOT",
    "spring-boot": "SPRING_BOOT",
    "rest api": "REST_API",
    "rest apis": "REST_API",
    "restful api": "REST_API",
    "restful apis": "REST_API",
    "graphql": "GRAPHQL",
    "pandas": "PANDAS",
    "numpy": "NUMPY",
    "scikit-learn": "SCIKIT_LEARN",
    "scikit learn": "SCIKIT_LEARN",
    "sklearn": "SCIKIT_LEARN",
    "tensorflow": "TENSORFLOW",
    "tensor flow": "TENSORFLOW",
    "pytorch": "PYTORCH",
    "py torch": "PYTORCH",
    "keras": "KERAS",
    "machine learning model development": "ML_MODEL_DEVELOPMENT",
    "ml model development": "ML_MODEL_DEVELOPMENT",
    "predictive model": "ML_MODEL_DEVELOPMENT",
    "predictive models": "ML_MODEL_DEVELOPMENT",
    "postgres": "POSTGRESQL",
    "postgresql": "POSTGRESQL",
    "mysql": "MYSQL",
    "my sql": "MYSQL",
    "sqlite": "SQLITE",
    "sql": "SQL",
    "mongodb": "MONGODB",
    "mongo db": "MONGODB",
    "redis": "REDIS",
    "git": "GIT",
    "docker": "DOCKER",
    "kubernetes": "KUBERNETES",
    "k8s": "KUBERNETES",
    "jenkins": "JENKINS",
    "github actions": "GITHUB_ACTIONS",
    "githubactions": "GITHUB_ACTIONS",
    "gitlab ci": "GITLAB_CI",
    "gitlab-ci": "GITLAB_CI",
    "gitlabci": "GITLAB_CI",
    "gitlab": "GITLAB_CI",
    "terraform": "TERRAFORM",
    "ansible": "ANSIBLE",
    "linux": "LINUX",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "AZURE",
    "gcp": "GCP",
    "google cloud": "GCP",
    "spark": "APACHE_SPARK",
    "apache spark": "APACHE_SPARK",
    "hadoop": "HADOOP",
    "kafka": "APACHE_KAFKA",
    "apache kafka": "APACHE_KAFKA",
    "airflow": "APACHE_AIRFLOW",
    "apache airflow": "APACHE_AIRFLOW",
    "dbt": "DBT",
    "snowflake": "SNOWFLAKE",
    "bigquery": "BIGQUERY",
    "big query": "BIGQUERY",
}


def build_transducer(variants: dict[str, str]) -> FST:
    """Build an FST from a ``{surface form: canonical token}`` table.

    Surface forms are case-folded before building the transducer; callers must
    case-fold input strings before translating them.
    Input:  mapping of accepted surface forms to canonical tokens.
    Output: a pyformlang ``FST`` M = (Q, Σ, Γ, δ, ω, q0, F).
    """
    transducer = FST()
    transducer.add_start_state(0)
    next_state = 1
    normalized_variants: dict[str, str] = {}

    for surface, canonical in variants.items():
        normalized_surface = surface.strip().casefold()
        if not normalized_surface:
            raise ValueError("surface forms must not be empty")
        if not canonical:
            raise ValueError(f"canonical token for {surface!r} must not be empty")
        existing = normalized_variants.get(normalized_surface)
        if existing is not None and existing != canonical:
            raise ValueError(f"conflicting canonical tokens for {surface!r}")
        if existing is not None:
            continue
        normalized_variants[normalized_surface] = canonical

        state = 0
        for index, symbol in enumerate(normalized_surface):
            destination = next_state
            next_state += 1
            output = [canonical] if index == len(normalized_surface) - 1 else []
            transducer.add_transition(state, symbol, destination, output)
            state = destination
        transducer.add_final_state(state)

    return transducer


@lru_cache(maxsize=1)
def _skill_transducer() -> FST:
    return build_transducer(SKILL_VARIANTS)


def normalize(raw_skill: str) -> str | None:
    """Translate one raw skill string into its canonical token.

    Returns ``None`` when no transducer accepts the string.
    """
    surface = raw_skill.strip().casefold()
    if not surface:
        return None

    outputs = list(_skill_transducer().translate(surface))
    if not outputs:
        return None
    return next(iter(outputs))[0]


def normalize_all(raw_skills: list[str]) -> list[str]:
    """Normalize a list of raw skills, dropping unknown ones and duplicates."""
    normalized: list[str] = []
    seen: set[str] = set()
    for raw_skill in raw_skills:
        token = normalize(raw_skill)
        if token is not None and token not in seen:
            seen.add(token)
            normalized.append(token)
    return normalized


def sort_for_profile(tokens: list[str], profile: Profile) -> list[str]:
    """Keep the tokens that belong to ``profile`` and sort them by its category order.

    Example (Full Stack): [GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT]
                       -> [JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]
    """
    category_order = {
        token: index
        for index, category in enumerate(profile.categories)
        for token in category.tokens
    }
    return sorted(
        (token for token in tokens if token in category_order),
        key=category_order.__getitem__,
    )
