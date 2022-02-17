# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Generate API documentation."""
import argparse
import subprocess
from pathlib import Path

_APIDOC_OPTS = ["--force", "--module-first", "--separate"]

# sphinx-apidoc --o %SOURCEDIR%/api %APIDOC_OPTS% ../msticpy ../msticpy/sectools


def run_sphinx_apidoc(script_args):
    """Run sphinx-apidoc to generate new docs."""
    print("Generating API files....")
    Path(script_args.temp).mkdir(exist_ok=True)
    apidoc_args = ["sphinx-apidoc", "--o", script_args.temp]
    apidoc_args.extend(_APIDOC_OPTS)
    apidoc_args.append(script_args.source)
    apidoc_args.extend(script_args.ignore)
    subprocess.run(apidoc_args, capture_output=True, check=True)


def check_paths(script_args):
    """Check parameter paths are valid."""
    if not Path(script_args.api_path).is_dir():
        raise FileNotFoundError(
            f"API target path {script_args.api_path} does not exist.",
            "Please specify using --api_path parameter.",
        )
    if not Path(script_args.source).is_dir():
        raise FileNotFoundError(
            f"Source path {script_args.source} does not exist.",
            "Please specify using --source parameter.",
        )


def update_api_files(script_args):
    """Update any out-of-date API files."""
    src_files = {file.name: file for file in Path(script_args.temp).glob("*.rst")}
    if "modules.rst" in src_files:
        del src_files["modules.rst"]
    dest_files = {file.name: file for file in Path(script_args.api_path).glob("*.rst")}
    actions = []
    for name, src_file in src_files.items():
        src_text = src_file.read_text()

        if name in dest_files and src_text == dest_files[name].read_text():
            # if the file hasn't changed, skip it
            continue
        # Otherwise replace the target with the source file
        src_file.replace(Path(script_args.api_path).joinpath(name))
        actions.append(f"{name} updated.")

    # check for dest files that are no longer in the source
    for name, src_file in dest_files.items():
        if name not in src_files:
            src_file.unlink()
            actions.append(f"{name} removed. No longer valid.")
    if not actions:
        print("No changes made")
    else:
        print("Updates were made:")
        print("\n".join(actions))


def _add_script_args():
    """Create argparse arguments."""
    parser = argparse.ArgumentParser(description="Generate changed/new API docs.")
    parser.add_argument(
        "--source",
        "-s",
        default="../msticpy",
        type=str,
        help="Path to source files.",
    )
    parser.add_argument(
        "--temp",
        "-t",
        default="source/.api_tmp",
        type=str,
        help="Path to write temp files.",
    )
    parser.add_argument(
        "--api_path",
        "-a",
        default="source/api",
        type=str,
        help="Destination path to API document RST files.",
    )
    parser.add_argument(
        "--ignore",
        "-i",
        default=["../msticpy/sectools"],
        type=list,
        help="Paths to ignore.",
    )
    return parser


# pylint: disable=invalid-name
if __name__ == "__main__":
    arg_parser = _add_script_args()
    args = arg_parser.parse_args()

    check_paths(args)
    run_sphinx_apidoc(args)
    update_api_files(args)

    # remove temp folder
    for file in list(Path(args.temp).glob("*.rst")):
        file.unlink()
    Path(args.temp).rmdir()
