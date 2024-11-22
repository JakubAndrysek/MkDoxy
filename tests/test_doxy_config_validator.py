# import pytest
#
# from mkdoxy.doxy_config_validator import validate_diagram_type
#
#
# def test_returns_dot_when_input_is_dot():
#     assert validate_diagram_type("dot") == "dot"
#
#
# def test_raises_value_error_for_empty_string():
#     with pytest.raises(ValueError, match="Invalid diagram type:  - must be one of \['dot', 'uml'\]"):
#         validate_diagram_type("")
