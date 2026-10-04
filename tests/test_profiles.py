import re

from resumelens.profiles import PROFILES, get_profile

CANONICAL = re.compile(r"^[A-Z][A-Z0-9_]*$")


def test_four_profiles_two_per_area():
    assert len(PROFILES) == 4
    areas = [p.area for p in PROFILES]
    assert areas.count("software") == 2
    assert areas.count("ai_data") == 2


def test_tokens_are_canonical_identifiers():
    for profile in PROFILES:
        for token in profile.alphabet:
            assert CANONICAL.match(token), (profile.key, token)


def test_token_belongs_to_one_category_per_profile():
    for profile in PROFILES:
        seen = set()
        for category in profile.categories:
            assert not (seen & category.tokens), (profile.key, category.name)
            seen |= category.tokens


def test_every_profile_has_a_required_category():
    for profile in PROFILES:
        assert any(c.required for c in profile.categories)


def test_get_profile():
    assert get_profile("FULL_STACK_DEVELOPER").title == "Full Stack Developer"
