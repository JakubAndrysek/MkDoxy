class DoxyCall:
    def __init__(self) -> None:
        self.DOXY_CALL = {
            "class": self.doxy_class,
            "class.list": self.doxy_class_list,
        }

    def call_doxy_by_name(self, name: str, config: list) -> None:
        if name in self.DOXY_CALL:
            func_name = self.DOXY_CALL[name]
            func_name(config)

    def doxy_class(self, config: list) -> None:
        print("doxyClassasd", config)

    def doxy_class_list(self, config: list) -> None:
        print("doxyClassList", config)


if __name__ == "__main__":
    doxy_call = DoxyCall()
    doxy_call.call_doxy_by_name("class", ["asd"])
    doxy_call.call_doxy_by_name("class.list", ["list"])
