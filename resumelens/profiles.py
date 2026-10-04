"""Professional profile definitions.

Every profile is plain data: an ordered tuple of categories, each one listing the
canonical tokens (output of the normalization stage) that belong to it.
The same generic code (sorting, automaton construction, classification) is used
for all four profiles, as required by the assignment.

The order of ``categories`` is the profile's canonical order (stage 2 sorting)
and also the order in which the recognizing automaton expects them (stage 3).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    tokens: frozenset[str]
    required: bool = True


@dataclass(frozen=True)
class Profile:
    key: str
    title: str
    area: str  # "software" | "ai_data"
    categories: tuple[Category, ...]

    @property
    def alphabet(self) -> frozenset[str]:
        """All canonical tokens this profile cares about (automaton alphabet Σ)."""
        return frozenset().union(*(c.tokens for c in self.categories))

    def category_of(self, token: str) -> Category | None:
        for category in self.categories:
            if token in category.tokens:
                return category
        return None


def _cat(name: str, *tokens: str, required: bool = True) -> Category:
    return Category(name, frozenset(tokens), required)


FULL_STACK_DEVELOPER = Profile(
    key="FULL_STACK_DEVELOPER",
    title="Full Stack Developer",
    area="software",
    categories=(
        _cat("Frontend language", "JAVASCRIPT", "TYPESCRIPT"),
        _cat("Frontend framework", "REACT", "ANGULAR", "VUE"),
        _cat("Backend", "NODE_JS", "EXPRESS", "DJANGO", "FLASK", "SPRING_BOOT"),
        _cat("Database", "POSTGRESQL", "MYSQL", "SQLITE", "SQL", "MONGODB", "REDIS"),
        _cat("API", "REST_API", "GRAPHQL", required=False),
        _cat("Version control", "GIT"),
    ),
)

MACHINE_LEARNING_ENGINEER = Profile(
    key="MACHINE_LEARNING_ENGINEER",
    title="Machine Learning Engineer",
    area="ai_data",
    categories=(
        _cat("Language", "PYTHON"),
        _cat("Data processing", "PANDAS", "NUMPY"),
        _cat("ML library", "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS"),
        _cat("ML practice", "ML_MODEL_DEVELOPMENT", required=False),
        _cat("Database", "SQL", "POSTGRESQL", "MYSQL"),
        _cat("Version control", "GIT"),
    ),
)

# Team-defined profiles (proposal, can be replaced once the official
# requirements are published).
DEVOPS_ENGINEER = Profile(
    key="DEVOPS_ENGINEER",
    title="DevOps Engineer",
    area="software",
    categories=(
        _cat("Operating system", "LINUX"),
        _cat("Scripting", "BASH", "PYTHON"),
        _cat("Containers", "DOCKER"),
        _cat("Orchestration", "KUBERNETES", required=False),
        _cat("CI/CD", "JENKINS", "GITHUB_ACTIONS", "GITLAB_CI"),
        _cat("Cloud", "AWS", "AZURE", "GCP"),
        _cat("Infrastructure as code", "TERRAFORM", "ANSIBLE", required=False),
        _cat("Version control", "GIT"),
    ),
)

DATA_ENGINEER = Profile(
    key="DATA_ENGINEER",
    title="Data Engineer",
    area="ai_data",
    categories=(
        _cat("Language", "PYTHON", "SCALA", "JAVA"),
        _cat("Database", "SQL", "POSTGRESQL", "MYSQL", "MONGODB"),
        _cat("Big data", "APACHE_SPARK", "HADOOP", "APACHE_KAFKA"),
        _cat("Orchestration", "APACHE_AIRFLOW", "DBT"),
        _cat("Cloud / warehouse", "AWS", "GCP", "AZURE", "SNOWFLAKE", "BIGQUERY", required=False),
        _cat("Version control", "GIT"),
    ),
)

PROFILES: tuple[Profile, ...] = (
    FULL_STACK_DEVELOPER,
    MACHINE_LEARNING_ENGINEER,
    DEVOPS_ENGINEER,
    DATA_ENGINEER,
)


def get_profile(key: str) -> Profile:
    for profile in PROFILES:
        if profile.key == key:
            return profile
    raise KeyError(f"Unknown profile: {key}")
