import shutil

import pytest
import yaml
from httpx import ConnectError
from orjson import orjson
from pydantic import ValidationError

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.common import library_config_dict
from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.generate_data import get_open_api
from openapi_python_generator.generate_data import write_data
from openapi_python_generator.language_converters.python.generator import generator
from tests.conftest import test_data_folder
from tests.conftest import test_data_path
from tests.conftest import test_result_path


def test_get_open_api(model_data):
    # Test JSON file
    assert get_open_api(test_data_path) == model_data

    # Create YAML version of the test file
    yaml_path = test_data_path.with_suffix('.yaml')
    with open(test_data_path) as f:
        json_content = orjson.loads(f.read())
    with open(yaml_path, 'w') as f:
        yaml.dump(json_content, f)

    # Test YAML file
    assert get_open_api(yaml_path) == model_data

    # Cleanup YAML file
    yaml_path.unlink()

    # Test remote file failure
    with pytest.raises(ConnectError):
        assert get_open_api("http://localhost:8080/api/openapi.json")

    # Test invalid OpenAPI spec
    with pytest.raises(ValidationError):
        assert get_open_api(test_data_folder / "failing_api.json")

    # Test non-existent file
    with pytest.raises(FileNotFoundError):
        assert get_open_api(test_data_folder / "file_does_not_exist.json")


def test_generate_data(model_data_with_cleanup):
    generate_data(test_data_path, test_result_path)
    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()


def test_write_data(model_data_with_cleanup):
    result = generator(model_data_with_cleanup, library_config_dict[HTTPLibrary.httpx])
    write_data(result, test_result_path)

    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()

    # delete test_result_path folder
    shutil.rmtree(test_result_path)

    model_data_copy = model_data_with_cleanup.copy()
    model_data_copy.components = None
    model_data_copy.paths = None

    result = generator(model_data_copy, library_config_dict[HTTPLibrary.httpx])
    write_data(result, test_result_path)

    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()
