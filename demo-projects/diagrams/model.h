#pragma once

namespace gallery {

/** Supplies a value to the documentation builder. */
class Input {
public:
    /** Read the next input value. */
    int read();
};

/** Converts a value to a rendered representation. */
class Renderer {
public:
    /** Render the supplied value. */
    int draw(int value);
};

/** Common interface for documentation builders. */
class BaseBuilder {
public:
    /** Build documentation. */
    virtual void build() = 0;
};

/**
 * Uses Input and Renderer to build documentation.
 * Doxygen derives inheritance, collaboration and call graphs from this code.
 */
class DocumentBuilder : public BaseBuilder {
    Input input_;
    Renderer renderer_;

public:
    /** Read the input, then render its value.
     * @callgraph
     * @callergraph
     */
    void build() override;
};

/** Read a value for the standalone build entry point. */
int read_value();

/** Render a value for the standalone build entry point. */
int render_value(int value);

/** Entry point used to demonstrate caller graphs. */
void run_build(DocumentBuilder &builder);

} // namespace gallery
