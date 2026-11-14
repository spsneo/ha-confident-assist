"""Question and answer types that every decision provider maps to.

The core uses only these types. A provider maps them to and from its own API, so
nothing outside a provider's module knows which API it talks to.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from homeassistant.exceptions import HomeAssistantError


@dataclass(frozen=True, slots=True)
class Noul:
    """A yes or no question, answered with a probability between 0 and 1."""

    question: str


@dataclass(frozen=True, slots=True)
class Choice:
    """Pick one of the options, answered with a confidence."""

    question: str
    options: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Score:
    """A number on a scale."""

    question: str
    low: float
    high: float


type Question = Noul | Choice | Score


@dataclass(frozen=True, slots=True)
class NoulAnswer:
    noul: float


@dataclass(frozen=True, slots=True)
class ChoiceAnswer:
    choice: str
    confidence: float
    distribution: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ScoreAnswer:
    score: float
    confidence: float


type Answer = NoulAnswer | ChoiceAnswer | ScoreAnswer


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True, slots=True)
class Decision:
    """The answers to one request, with what it cost."""

    answers: dict[str, Answer]
    usage: Usage
    model: str | None = None


class ProviderError(HomeAssistantError):
    """A provider could not answer."""


class ProviderAuthError(ProviderError):
    """The provider rejected the credentials."""


class ProviderUnavailableError(ProviderError):
    """The provider did not answer, or answered with an error."""
