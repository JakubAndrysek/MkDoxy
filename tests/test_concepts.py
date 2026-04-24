"""Tests for C++20 concept support in MkDoxy."""
import os
import tempfile
import shutil
import pytest

from mkdoxy.cache import Cache
from mkdoxy.constants import Kind
from mkdoxy.doxygen import Doxygen
from mkdoxy.doxyrun import DoxygenRun
from mkdoxy.finder import Finder
from mkdoxy.generatorBase import GeneratorBase
from mkdoxy.node import Node
from mkdoxy.utils import recursive_find
from mkdoxy.xml_parser import XmlParser


CONCEPT_HEADER = r"""
#ifndef EXAMPLE_CONCEPTS_H
#define EXAMPLE_CONCEPTS_H

#include <type_traits>
#include <concepts>
#include <string>

/**
 * @brief Concept that checks if a type is an animal.
 * @details This concept verifies that a type T has the required
 * interface to be considered an animal.
 * @tparam T The type to check
 */
template <typename T>
concept Animal = requires(T a) {
    { a.name() } -> std::convertible_to<std::string>;
    { a.legs() } -> std::convertible_to<int>;
};

/**
 * @brief Concept for numeric types.
 * @tparam T The type to check
 */
template <typename T>
concept Numeric = std::is_arithmetic_v<T>;

/**
 * @brief A simple function constrained by a concept.
 * @tparam T An Animal type
 * @param animal The animal input
 * @return description string
 */
template <Animal T>
std::string describe(const T& animal) {
    return animal.name();
}

#endif
"""


@pytest.fixture(scope="module")
def doxygen_output():
    """Generate Doxygen XML output from a concept header file."""
    tmpdir = tempfile.mkdtemp(prefix="mkdoxy_concept_test_")
    src_dir = os.path.join(tmpdir, "src")
    os.makedirs(src_dir)

    # Write concept header
    with open(os.path.join(src_dir, "concepts.h"), "w") as f:
        f.write(CONCEPT_HEADER)

    # Run Doxygen
    doxy_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource=src_dir,
        tempDoxyFolder=tmpdir,
        doxyCfgNew={},
    )
    doxy_run.checkAndRun()

    xml_dir = doxy_run.getOutputFolder()
    yield xml_dir

    # Cleanup
    shutil.rmtree(tmpdir)


@pytest.fixture(scope="module")
def doxygen_parsed(doxygen_output):
    """Parse Doxygen XML output."""
    cache = Cache()
    parser = XmlParser(cache=cache, debug=False)
    doxygen = Doxygen(doxygen_output, parser=parser, cache=cache)
    return doxygen


class TestKindConcept:
    """Test that Kind.CONCEPT is properly defined."""

    def test_concept_kind_exists(self):
        assert Kind.CONCEPT.value == "concept"

    def test_concept_is_language(self):
        assert Kind.CONCEPT.is_language()

    def test_concept_is_parent(self):
        assert Kind.CONCEPT.is_parent()

    def test_concept_from_str(self):
        assert Kind.from_str("concept") == Kind.CONCEPT

    def test_concept_is_concept(self):
        assert Kind.CONCEPT.is_concept()

    def test_concept_is_not_class(self):
        assert not Kind.CONCEPT.is_class()

    def test_concept_is_not_class_or_struct(self):
        assert not Kind.CONCEPT.is_class_or_struct()


class TestConceptParsing:
    """Test that concepts are parsed from Doxygen XML."""

    def test_concepts_list_not_empty(self, doxygen_parsed):
        """Concepts should be collected into the concepts list."""
        concepts = doxygen_parsed.concepts.children
        assert len(concepts) > 0, "Expected at least one concept to be parsed"

    def test_animal_concept_found(self, doxygen_parsed):
        """The Animal concept should be found."""
        concept_names = [c.name for c in doxygen_parsed.concepts.children]
        assert "Animal" in concept_names, f"Expected 'Animal' in {concept_names}"

    def test_numeric_concept_found(self, doxygen_parsed):
        """The Numeric concept should be found."""
        concept_names = [c.name for c in doxygen_parsed.concepts.children]
        assert "Numeric" in concept_names, f"Expected 'Numeric' in {concept_names}"

    def test_concept_kind_is_correct(self, doxygen_parsed):
        """All concept nodes should have Kind.CONCEPT."""
        for concept in doxygen_parsed.concepts.children:
            assert concept.kind == Kind.CONCEPT, f"Expected {concept.name} to have Kind.CONCEPT, got {concept.kind}"

    def test_concept_has_brief(self, doxygen_parsed):
        """Concepts should have brief descriptions."""
        for concept in doxygen_parsed.concepts.children:
            assert concept.has_brief, f"Expected {concept.name} to have a brief description"

    def test_concept_has_details(self, doxygen_parsed):
        """The Animal concept should have detailed description."""
        animal = None
        for c in doxygen_parsed.concepts.children:
            if c.name == "Animal":
                animal = c
                break
        assert animal is not None
        assert animal.has_details, "Expected Animal concept to have details"

    def test_concept_has_templateparams(self, doxygen_parsed):
        """Concepts should have template parameters."""
        for concept in doxygen_parsed.concepts.children:
            assert concept.has_templateparams, f"Expected {concept.name} to have template parameters"

    def test_concept_is_concept_property(self, doxygen_parsed):
        """Node.is_concept should return True for concept nodes."""
        for concept in doxygen_parsed.concepts.children:
            assert concept.is_concept, f"Expected {concept.name}.is_concept to be True"

    def test_concept_is_parent_property(self, doxygen_parsed):
        """Node.is_parent should return True for concept nodes."""
        for concept in doxygen_parsed.concepts.children:
            assert concept.is_parent, f"Expected {concept.name}.is_parent to be True"


class TestConceptFinder:
    """Test that concepts can be found via the Finder."""

    def test_finder_finds_concept(self, doxygen_parsed):
        doxygen_dict = {"test": doxygen_parsed}
        finder = Finder(doxygen_dict)
        result = finder.doxyConcept("test", "Animal")
        assert isinstance(result, Node), f"Expected Node, got {type(result)}: {result}"
        assert result.name == "Animal"

    def test_finder_returns_list_for_unknown(self, doxygen_parsed):
        doxygen_dict = {"test": doxygen_parsed}
        finder = Finder(doxygen_dict)
        result = finder.doxyConcept("test", "NonExistent")
        assert isinstance(result, list), f"Expected list of suggestions, got {type(result)}"


class TestConceptCodeblock:
    """Test that concept codeblocks are generated correctly."""

    def test_concept_codeblock_contains_concept_keyword(self, doxygen_parsed):
        """The codeblock should contain the 'concept' keyword."""
        for concept in doxygen_parsed.concepts.children:
            codeblock = concept.codeblock
            assert "concept" in codeblock, f"Expected 'concept' in codeblock, got: {codeblock}"

    def test_concept_codeblock_contains_name(self, doxygen_parsed):
        """The codeblock should contain the concept name."""
        for concept in doxygen_parsed.concepts.children:
            codeblock = concept.codeblock
            assert concept.name in codeblock, f"Expected '{concept.name}' in codeblock, got: {codeblock}"


class TestConceptGeneratorBase:
    """Test that GeneratorBase can render concept pages."""

    def test_concepts_template_exists(self):
        """The concepts template should be loaded."""
        gen = GeneratorBase()
        assert "concepts" in gen.templates, "Expected 'concepts' template to be loaded"

    def test_concepts_renders(self, doxygen_parsed):
        """The concepts method should return non-empty output."""
        gen = GeneratorBase()
        nodes = doxygen_parsed.concepts.children
        output = gen.concepts(nodes)
        assert len(output) > 0, "Expected non-empty concepts output"
        assert "Concept List" in output, f"Expected 'Concept List' header in output"

    def test_concepts_contains_concept_names(self, doxygen_parsed):
        """The concepts output should contain concept names."""
        gen = GeneratorBase()
        nodes = doxygen_parsed.concepts.children
        output = gen.concepts(nodes)
        assert "Animal" in output, f"Expected 'Animal' in concepts output"
        assert "Numeric" in output, f"Expected 'Numeric' in concepts output"


class TestConceptUrls:
    """Test that concept nodes have correct URL properties."""

    def test_concept_base_url(self, doxygen_parsed):
        """Concepts should link to concepts.md as their base."""
        for concept in doxygen_parsed.concepts.children:
            assert "concepts.md" in concept.base_url, (
                f"Expected 'concepts.md' in base_url, got: {concept.base_url}"
            )

    def test_concept_base_name(self, doxygen_parsed):
        """Concepts should have 'Concept List' as base_name."""
        for concept in doxygen_parsed.concepts.children:
            assert concept.base_name == "Concept List", (
                f"Expected 'Concept List', got: {concept.base_name}"
            )
