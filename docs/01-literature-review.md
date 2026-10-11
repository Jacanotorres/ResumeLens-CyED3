# 1. Literature review

## Topics to cover

- Résumé parsing and information extraction (rule-based vs ML-based approaches)
- Regular expressions for information extraction
- Finite-state transducers in text normalization (e.g. spelling and abbreviation normalization in NLP)
- Finite automata for pattern recognition
- Domain-specific languages and context-free grammars (textX, Xtext)
- Skill taxonomies (ESCO, O*NET) and skill normalization

## Sources

| # | Reference | Key idea | How it informs ResumeLens |
|---|-----------|----------|---------------------------|
| 1 | Hopcroft, Motwani & Ullman, *Introduction to Automata Theory, Languages, and Computation* | | |
| 2 | Mohri, "Finite-State Transducers in Language and Speech Processing", *Computational Linguistics* 23(2), 1997 | | |
| 3 | Dejanović et al., "TextX: A Python tool for Domain-Specific Languages implementation", *Knowledge-Based Systems*, 115, 1-4, 2017 | textX builds a parser and a meta-model from a single grammar (on top of the Arpeggio PEG parser) and returns the parsed text as a Python object graph. | It implements and validates the candidate profile DSL (`candidate.tx`); the object graph it returns is what `render_html` reads. |
| 4 | Mernik, Heering & Sloane, "When and how to develop domain-specific languages", *ACM Computing Surveys*, 37(4), 316-344, 2005 | A DSL tailored to a narrow domain offers more expressiveness and ease of use than a general-purpose language in that domain; the paper identifies patterns for the decision, analysis, design and implementation phases. | It supports defining a small DSL for the candidate profile and structuring Stage 4 as analysis (what data to represent), design (grammar) and implementation (textX). |

## Summary

_TODO_

### Stage 4 - Candidate profile language

The DSL literature (Mernik et al., 2005) argues that a language tailored to a narrow domain is easier to write, read and validate than a general-purpose data format. textX (Dejanović et al., 2017) fits this stage because a single grammar file yields both the validator (the parser) and the object model consumed by the HTML renderer, so no parser or parse-tree transformer has to be written by hand. textX grammars are based on parsing expression grammars (PEG), where alternatives are tried in order, which differs from a pure context-free grammar in how ambiguity is resolved. Our grammar is not affected by this difference because every alternative starts with a distinct keyword or literal.