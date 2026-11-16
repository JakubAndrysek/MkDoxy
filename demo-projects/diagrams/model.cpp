#include "model.h"

namespace gallery {

int Input::read() { return 42; }

int Renderer::draw(int value) { return value * 2; }

void DocumentBuilder::build() {
    int value = input_.read();
    renderer_.draw(value);
}

int read_value() { return 42; }

int render_value(int value) { return value * 2; }

void run_build(DocumentBuilder &builder) {
    int value = read_value();
    render_value(value);
    builder.build();
}

} // namespace gallery
