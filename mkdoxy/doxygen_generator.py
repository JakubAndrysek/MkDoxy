import hashlib
import logging
import os
import shutil
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Optional

from mkdocs import exceptions

log: logging.Logger = logging.getLogger("mkdocs")


class DoxygenGenerator:
    """! Class for running Doxygen.
    @details This class is used to run Doxygen and parse the XML output.
    """

    def __init__(
        self,
        doxygen_bin_path: Path,
        doxygen_source_dirs: str,
        temp_doxy_folder: Path,
        doxy_config_file: Optional[str] = None,
        doxy_config_dict: dict = {},
    ):
        """! Constructor.
        Default Doxygen config options:

        - INPUT: <doxygenSource>
        - OUTPUT_DIRECTORY: <tempDoxyFolder>
        - DOXYFILE_ENCODING: UTF-8
        - GENERATE_XML: YES
        - RECURSIVE: YES
        - EXAMPLE_PATH: examples
        - SHOW_NAMESPACES: YES
        - GENERATE_HTML: NO
        - GENERATE_LATEX: NO

        @details
        @param doxygen_bin_path: (str) Path to the Doxygen binary.
        @param doxygen_source_dirs: (str) Source files for Doxygen.
        @param temp_doxy_folder: (str) Temporary folder for Doxygen.
        @param doxy_config_file: (str) Custom Doxygen config file.
        @param doxy_config_dict: (dict) New Doxygen config options that will be added to the default config (new options will overwrite default options)
        """  # noqa: E501

        if not self.is_doxygen_valid_path(doxygen_bin_path):
            raise DoxygenBinPathNotValid(
                f"Invalid Doxygen binary path: {doxygen_bin_path}\n"
                f"Make sure Doxygen is installed and the path is correct.\n"
                f"Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/#configure-custom-doxygen-binary."
            )

        self.doxygen_bin_path: Path = doxygen_bin_path
        self.doxygen_source_dirs: str = doxygen_source_dirs
        self.temp_doxy_folder: Path = temp_doxy_folder
        self.doxy_config_file: Optional[str] = doxy_config_file
        self.hash_file_name: Path = Path("mkdoxy_hash.txt")
        self.doxy_cfg: dict = self.set_doxy_config(doxy_config_dict)

    def set_doxy_config(self, doxyCfgNew: dict) -> dict:
        """! Set the Doxygen configuration.
        @details If a custom Doxygen config file is provided, it will be used. Otherwise, default options will be used.
        @details Order of application of parameters:
        @details 1. Custom Doxygen config file
        @details 2. If not provided, default options - in documentation
        @details 3. New Doxygen config options from mkdocs.yml
        @details 3. Overwrite INPUT and OUTPUT_DIRECTORY with the provided values for correct plugin operation.

        @details Overwrite options description:
        @details - INPUT: <doxygenSource>
        @details - OUTPUT_DIRECTORY: <tempDoxyFolder>

        @details Default Doxygen config options:
        @details - DOXYFILE_ENCODING: UTF-8
        @details - GENERATE_XML: YES
        @details - RECURSIVE: YES
        @details - EXAMPLE_PATH: examples
        @details - SHOW_NAMESPACES: YES
        @details - GENERATE_HTML: NO
        @details - GENERATE_LATEX: NO
        @param doxyCfgNew: (dict) New Doxygen config options that will be
         added to the default config (new options will overwrite default options)
        @return: (dict) Doxygen configuration.
        """
        doxy_config = {}

        if self.doxy_config_file is not None and self.doxy_config_file != "":
            try:
                with open(self.doxy_config_file, "r") as file:
                    doxy_config.update(self.str2dox_dict(file.read()))
            except FileNotFoundError as e:
                raise DoxygenCustomConfigNotFound(
                    f"Custom Doxygen config file not found: {self.doxy_config_file}\n"
                    f"Make sure the path is correct."
                    f"Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/#configure-custom-doxygen-configuration-file."
                ) from e
        else:
            doxy_config = {
                "DOXYFILE_ENCODING": "UTF-8",
                "GENERATE_XML": "YES",
                "RECURSIVE": "YES",
                "EXAMPLE_PATH": "examples",
                "SHOW_NAMESPACES": "YES",
                "GENERATE_HTML": "NO",
                "GENERATE_LATEX": "NO",
            }

        doxy_config.update(doxyCfgNew)
        doxy_config["INPUT"] = self.doxygen_source_dirs
        doxy_config["OUTPUT_DIRECTORY"] = str(self.temp_doxy_folder)
        return doxy_config

    @staticmethod
    def is_doxygen_valid_path(doxygen_bin_path: Path) -> bool:
        """! Check if the Doxygen binary path is valid.
        @details Accepts a full path or just 'doxygen' if it exists in the system's PATH.
        @param doxygen_bin_path: (str) The path to the Doxygen binary or just 'doxygen'.
        @return: (bool) True if the Doxygen binary path is valid, False otherwise.
        """
        # If the path is just 'doxygen', search for it in the system's PATH
        if str(doxygen_bin_path) == "doxygen":
            return shutil.which("doxygen") is not None

        # Use pathlib to check if the provided full path is a file and executable
        return doxygen_bin_path.is_file() and os.access(doxygen_bin_path, os.X_OK)

    # Source of dox_dict2str: https://xdress-fabio.readthedocs.io/en/latest/_modules/xdress/doxygen.html#XDressPlugin
    @staticmethod
    def dox_dict2str(dox_dict: dict) -> str:
        """! Convert a dictionary to a string that can be written to a doxygen config file.
        @details
        @param dox_dict: (dict) Dictionary to convert.
        @return: (str) String that can be written to a doxygen config file.
        """
        string = ""
        new_line = "{option} = {value}\n"
        for key, value in dox_dict.items():
            if value is True:
                value_transformed = "YES"
            elif value is False:
                value_transformed = "NO"
            else:
                value_transformed = value

            string += new_line.format(option=key.upper(), value=value_transformed)

        # Don't need an empty line at the end
        return string.strip()

    def str2dox_dict(self, dox_str: str) -> dict:
        """! Convert a string from a doxygen config file to a dictionary.
        @details
        @param dox_str: (str) String from a doxygen config file.
        @return: (dict) Dictionary.
        """
        doxy_dict = {}
        try:
            for line in dox_str.split("\n"):
                if line.strip() == "":
                    continue
                key, value = line.split(" = ")
                if value == "YES":
                    doxy_dict[key] = True
                elif value == "NO":
                    doxy_dict[key] = False
                else:
                    doxy_dict[key] = value
        except ValueError as e:
            raise DoxygenCustomConfigNotValid(
                f"Invalid custom Doxygen config file: {self.doxy_config_file}\n"
                f"Make sure the file is in standard Doxygen format."
                f"Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/."
            ) from e
        return doxy_dict

    def hash_write(self, file_name: Path, hash_key: str):
        with open(file_name, "w") as hash_file:
            hash_file.write(hash_key)

    def hash_read(self, file_name: Path) -> str:
        with open(file_name, "r") as hash_file:
            return str(hash_file.read())

    def has_changes(self) -> bool:
        """! Check if the source files have changed since the last run.
        @details
        @return: (bool) True if the source files have changed since the last run.
        """
        sha1 = hashlib.sha1()
        sources = self.doxygen_source_dirs.split(" ")
        for source in sources:
            for path in Path(source).rglob("*.*"):
                # Code from https://stackoverflow.com/a/22058673/15411117
                BUF_SIZE = 65536  # let's read stuff in 64kb chunks!
                if path.is_file():
                    with open(path, "rb") as file:
                        while True:
                            data = file.read(BUF_SIZE)
                            if not data:
                                break
                            sha1.update(data)

        hash_new = sha1.hexdigest()
        hash_file_path = Path.joinpath(self.temp_doxy_folder, self.hash_file_name)
        if hash_file_path.is_file():
            hash_old = self.hash_read(hash_file_path)
            if hash_new == hash_old:
                return False  # No changes in the source files

        self.hash_write(hash_file_path, hash_new)
        return True

    def run(self) -> None:
        """! Run Doxygen with the current configuration using the Popen class.
        @details
        """
        doxy_builder = Popen(
            [self.doxygen_bin_path, "-"],
            stdout=PIPE,
            stdin=PIPE,
            stderr=PIPE,
        )
        doxy_str = self.dox_dict2str(self.doxy_cfg).encode("utf-8")
        stdout_data, stderr_data = doxy_builder.communicate(doxy_str)
        if doxy_builder.returncode != 0:
            log.error(f"Error running Doxygen: {stderr_data.decode('utf-8')}")
            raise Exception("Error running Doxygen")

    def get_output_xml_folder(self) -> Path:
        """! Get the path to the XML output folder.
        @details
        @return: (Path) Path to the XML output folder.
        """
        return Path.joinpath(self.temp_doxy_folder, Path("xml"))

    def get_output_html_folder(self) -> Path:
        """! Get the path to the HTML output folder.
        @details
        @return: (Path) Path to the HTML output folder.
        """
        return Path.joinpath(self.temp_doxy_folder, Path("html"))


# not valid path exception
class DoxygenBinPathNotValid(exceptions.PluginError):
    pass


class DoxygenCustomConfigNotFound(exceptions.PluginError):
    pass


class DoxygenCustomConfigNotValid(exceptions.PluginError):
    pass
