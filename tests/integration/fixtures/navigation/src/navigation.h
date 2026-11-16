/** @defgroup top_module Top module
 *  Top-level documentation group.
 */
/** @defgroup nested_module Nested module
 *  @ingroup top_module
 *  Nested documentation group.
 */
/** @page overview Overview
 *  Navigation fixture page.
 */
/** Outer namespace. */
namespace outer {
/** Namespace enumeration. */
enum NamespaceMode { namespace_value };
/** Inner namespace. */
namespace inner {
/** Container class. */
class Container {
public:
    /** Class enumeration. */
    enum ClassMode { class_value };
    /** Nested class. */
    class Nested {};
};
}
}
