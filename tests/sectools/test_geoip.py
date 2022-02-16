# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""GeoIP provider unit tests."""
import os
from pathlib import Path
import socket

import nbformat
import pytest
import pytest_check as check

from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

from msticpy.data.context.geoip import GeoLiteLookup, IPStackLookup

from ..unit_test_lib import custom_mp_config, get_test_data_path

_NB_FOLDER = "docs/notebooks"
_NB_NAME = "GeoIPLookups.ipynb"
_MP_CONFIG_PATH = get_test_data_path().parent.joinpath("msticpyconfig-test.yaml")


@pytest.mark.skipif(
    not os.environ.get("MSTICPY_TEST_NOSKIP"), reason="Skipped for local tests."
)
@pytest.mark.skipif(
    os.environ.get("MSTICPY_BUILD_SOURCE", "").casefold() == "fork",
    reason="External fork.",
)
def test_geoip_notebook():
    """Test geoip notebook."""
    nb_path = Path(_NB_FOLDER).joinpath(_NB_NAME)
    abs_path = Path(_NB_FOLDER).absolute()

    if not os.environ.get("MSTICPY_TEST_IPSTACK"):
        os.environ["MSTICPY_SKIP_IPSTACK_TEST"] = "1"
    with open(nb_path, "rb") as f:
        nb_bytes = f.read()
    nb_text = nb_bytes.decode("utf-8")
    nb = nbformat.reads(nb_text, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

    try:
        with custom_mp_config(_MP_CONFIG_PATH):
            ep.preprocess(nb, {"metadata": {"path": abs_path}})

    except CellExecutionError:
        nb_err = str(nb_path).replace(".ipynb", "-err.ipynb")
        msg = f"Error executing the notebook '{nb_path}'.\n"
        msg += f"See notebook '{nb_err}' for the traceback."
        print(msg)
        with open(nb_err, mode="w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        raise

    if os.environ.get("MSTICPY_SKIP_IPSTACK_TEST"):
        del os.environ["MSTICPY_SKIP_IPSTACK_TEST"]


@pytest.mark.skipif(
    not os.environ.get("MSTICPY_TEST_NOSKIP"), reason="Skipped for local tests."
)
@pytest.mark.skipif(
    os.environ.get("MSTICPY_BUILD_SOURCE", "").casefold() == "fork",
    reason="External fork.",
)
def test_geoiplite_download(tmp_path):
    """Test forced download of GeoIPLite DB."""
    test_folder = tmp_path / "test_geolite_data"
    tgt_folder = Path(test_folder).resolve()
    try:
        tgt_folder.mkdir(exist_ok=True)
        with pytest.warns(None) as warning_record:
            with custom_mp_config(_MP_CONFIG_PATH):
                ip_location = GeoLiteLookup(
                    db_folder=str(tgt_folder), force_update=True, debug=True
                )
                ip_location.close()
        if warning_record:
            print(f"{len(warning_record)} warnings recorded")
        for warning_item in warning_record:
            print(vars(warning_item))
        # Check that we don't have a warning from GeoIPLookup
        # (occasionally warnings are generated by the test infrastructure
        # that filter through to this test)
        check.is_false(
            any(
                isinstance(warn.message, str)
                and warn.message.startswith("GeoIpLookup:")
                for warn in warning_record.list
            )
        )
    finally:
        if tgt_folder.exists():
            for file in tgt_folder.glob("*"):
                file.unlink()
            tgt_folder.rmdir()


def test_geoiplite_lookup():
    """Test GeoLite lookups."""
    socket_info = socket.getaddrinfo("pypi.org", 0, 0, 0, 0)

    ips = [res[4][0] for res in socket_info]
    with custom_mp_config(_MP_CONFIG_PATH):
        ip_location = GeoLiteLookup()

        loc_result, ip_entities = ip_location.lookup_ip(ip_addr_list=ips)
        check.equal(len(ip_entities), len(ips))
        check.equal(len(loc_result), len(ips))
        for ip_entity in ip_entities:
            check.is_not_none(ip_entity.Location)


@pytest.mark.skipif(
    not os.environ.get("MSTICPY_TEST_IPSTACK"), reason="Skipped ip stack tests."
)
def test_ipstack_lookup():
    """Test IPStack lookups."""
    socket_info = socket.getaddrinfo("pypi.org", 0, 0, 0, 0)

    ips = [res[4][0] for res in socket_info]
    with custom_mp_config(_MP_CONFIG_PATH):
        ip_location = IPStackLookup()
        loc_result, ip_entities = ip_location.lookup_ip(ip_addr_list=ips)
        check.equal(len(ip_entities), len(ips))
        check.equal(len(loc_result), len(ips))
        for ip_entity in ip_entities:
            check.is_not_none(ip_entity.Location)
