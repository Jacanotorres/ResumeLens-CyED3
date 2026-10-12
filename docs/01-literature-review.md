# 1. Literature review

## Scope of review

- Résumé parsing and information extraction (rule-based vs ML-based approaches)
- Regular expressions for information extraction
- Finite-state transducers in text normalization (e.g. spelling and abbreviation normalization in NLP)
- Finite automata for pattern recognition
- Domain-specific languages and context-free grammars (textX, Xtext)
- Skill taxonomies (ESCO, O*NET) and skill normalization

## Sources

| # | Reference | Key idea | How it informs ResumeLens |
|---|-----------|----------|---------------------------|
| 1 | Hopcroft, J. E., Motwani, R., & Ullman, J. D. *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. Pearson, 2006. | Presents regular languages, finite automata, and the relationships between automaton models. | Provides the theoretical basis for recognizing ordered qualification-category patterns with finite automata. |
| 2 | Mohri, M. “Finite-State Transducers in Language and Speech Processing.” *Computational Linguistics*, 23(2), 269–311, 1997. [ACL Anthology](https://aclanthology.org/J97-2003/). | Surveys finite-state transducer representations, algorithms, and applications to language and speech processing. | Motivates modeling skill spelling and abbreviation variants as input-to-canonical-output mappings. |
| 3 | Dejanović et al., "TextX: A Python tool for Domain-Specific Languages implementation", *Knowledge-Based Systems*, 115, 1-4, 2017 | textX builds a parser and a meta-model from a single grammar (on top of the Arpeggio PEG parser) and returns the parsed text as a Python object graph. | It implements and validates the candidate profile DSL (`candidate.tx`); the object graph it returns is what `render_html` reads. |
| 4 | Mernik, Heering & Sloane, "When and how to develop domain-specific languages", *ACM Computing Surveys*, 37(4), 316-344, 2005 | A DSL tailored to a narrow domain offers more expressiveness and ease of use than a general-purpose language in that domain; the paper identifies patterns for the decision, analysis, design and implementation phases. | It supports defining a small DSL for the candidate profile and structuring Stage 4 as analysis (what data to represent), design (grammar) and implementation (textX). |

### Implementation and occupational references

| # | Reference | Key idea | How it informs ResumeLens |
|---|-----------|----------|---------------------------|
| 5 | Python Software Foundation. "[`re` — Regular expression operations](https://docs.python.org/3/library/re.html)." Python documentation. | Documents Python's regular-expression syntax, matching operations, and compiled patterns. | Serves as the implementation reference for Stage 1 extraction and its use of raw-string patterns, boundaries, and matching operations. |
| 6 | European Commission. "[What is ESCO?](https://esco.ec.europa.eu/en/about-esco/what-esco)." European Skills, Competences, Qualifications and Occupations. | ESCO provides a multilingual classification and common vocabulary for occupations and skills, with links between them. | Provides context for skill normalization and occupation/qualification vocabularies. ResumeLens currently uses its own small variant table and does not import ESCO data. |
| 7 | National Center for O*NET Development. "[O*NET Content Model](https://www.onetcenter.org/content.html)." | Organizes occupation-related information into a structured model of worker and job attributes. | Offers a reference point for organizing profile requirements. ResumeLens defines four project-specific profiles and does not integrate O*NET data. |

## Summary

The literature connects the project's four processing stages to complementary
formal-language models. Regular expressions provide a direct, inspectable way
to identify known surface patterns in résumé text; Python's `re` module
supplies the matching operations used by the extractor. Finite-state
transducers model the next step: mapping recognized spelling variants and
abbreviations to canonical skill tokens. Finite automata then recognize
sequences of those tokens that satisfy the ordered category patterns defined
for each profile. Finally, a domain-specific grammar describes the structure
of the generated candidate record, and textX parses that representation into
the model used by the HTML renderer.

This sequence is a deliberate rule-based design, not a machine-learning résumé
parser. Its patterns, skill variants, and profile requirements are explicit
and can be tested, but their coverage depends on the dictionaries and
qualification rules maintained by the team. A phrase that is absent from
those definitions may not be recognized even if a person considers it
equivalent. Similarly, an accepted sequence means only that the résumé
contains the modeled tokens in the required category order; it is not a
measure of candidate quality and does not make a hiring decision.

ESCO and O*NET illustrate how larger occupational vocabularies can structure
skills and profile information. They inform the problem framing, but are not
data sources used by the current implementation. Integrating a maintained
taxonomy, extending supported variants, and comparing rule-based extraction
with a learned method on an annotated résumé set are possible future
improvements; such a comparison would require data and evaluation beyond this
project's current scope.

### Stage 4 — Candidate profile language

The DSL literature (Mernik et al., 2005) describes how a language tailored to
a narrow domain can make domain concepts explicit. textX (Dejanović et al.,
2017) fits this stage because a single grammar file defines the parser and
produces the object model consumed by the HTML renderer. textX uses parsing
expression grammars (PEGs), in which ordered alternatives differ from
unrestricted CFG ambiguity resolution. The project grammar avoids ambiguous
alternatives by beginning each choice with a distinct keyword or literal.
Parsing checks the written structure; additional semantic rules, such as
uniqueness of profile results, remain outside the grammar.
