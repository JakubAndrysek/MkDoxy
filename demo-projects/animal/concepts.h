#ifndef EXAMPLE_CONCEPTS_H
#define EXAMPLE_CONCEPTS_H

#include <type_traits>
#include <concepts>
#include <string>

/**
 * @brief Concept that checks if a type is an animal.
 * @details This concept verifies that a type T has the required
 * interface to be considered an animal, including name(), legs(),
 * and sound() member functions.
 *
 * @tparam T The type to check
 */
template <typename T>
concept Animal = requires(T a) {
    { a.name() } -> std::convertible_to<std::string>;
    { a.legs() } -> std::convertible_to<int>;
    { a.sound() } -> std::convertible_to<std::string>;
};

/**
 * @brief Concept that checks if a type is printable.
 * @details This concept verifies that a type T can be converted
 * to a string representation via a print() method.
 *
 * @tparam T The type to check
 */
template <typename T>
concept Printable = requires(T a) {
    { a.print() } -> std::convertible_to<std::string>;
};

/**
 * @brief Concept requiring a type to be both an Animal and Printable.
 * @details A combined concept that requires a type to satisfy both
 * the Animal and Printable concepts.
 *
 * @tparam T The type to check
 */
template <typename T>
concept PrintableAnimal = Animal<T> && Printable<T>;

/**
 * @brief Concept for numeric types.
 * @details Checks that a type is either integral or floating point.
 *
 * @tparam T The type to check
 */
template <typename T>
concept Numeric = std::is_arithmetic_v<T>;

/**
 * @brief Concept for hashable types.
 * @details Checks that a type can be hashed using std::hash.
 *
 * @tparam T The type to check
 */
template <typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

/**
 * @brief Function constrained by the Animal concept.
 * @details This function can only be called with types that satisfy
 * the Animal concept.
 *
 * @tparam T An Animal type
 * @param animal The animal to describe
 * @return A string description of the animal
 */
template <Animal T>
std::string describe(const T& animal) {
    return animal.name() + " has " + std::to_string(animal.legs()) + " legs and says " + animal.sound();
}

#endif // EXAMPLE_CONCEPTS_H
