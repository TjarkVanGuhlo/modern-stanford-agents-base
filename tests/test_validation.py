"""Test suite for Django POST endpoint input validation (Issue #60)."""

import sys
from pathlib import Path

import pytest

# Add the frontend server to the path for imports
FRONTEND_SERVER_PATH = Path(__file__).parent.parent / "environment" / "frontend_server"
sys.path.insert(0, str(FRONTEND_SERVER_PATH))

from translator.validation import (  # noqa: E402
    COMPRESSED_STORAGE_ROOT,
    STORAGE_ROOT,
    TEMP_STORAGE_ROOT,
    ValidationError,
    safe_storage_path,
    validate_camera_data,
    validate_environment_request,
    validate_sim_code,
    validate_step,
    validate_update_request,
)


class TestValidateSimCode:
    """Test validate_sim_code function."""

    def test_valid_alphanumeric(self):
        """Valid alphanumeric sim codes should pass."""
        assert validate_sim_code("base_the_ville_isabella") is True
        assert validate_sim_code("test123") is True
        assert validate_sim_code("SimulationCode") is True

    def test_valid_with_underscores(self):
        """Valid sim codes with underscores should pass."""
        assert validate_sim_code("base_the_ville_isabella_maria_klaus") is True
        assert validate_sim_code("test_simulation_001") is True

    def test_valid_with_hyphens(self):
        """Valid sim codes with hyphens should pass."""
        assert validate_sim_code("test-simulation-001") is True
        assert validate_sim_code("my-sim") is True

    def test_valid_mixed(self):
        """Valid sim codes with mixed characters should pass."""
        assert validate_sim_code("base_the-ville_test123") is True

    def test_invalid_path_traversal(self):
        """Path traversal attempts should fail."""
        assert validate_sim_code("../etc/passwd") is False
        assert validate_sim_code("..") is False
        assert validate_sim_code("../") is False
        assert validate_sim_code("foo/../bar") is False

    def test_invalid_with_slashes(self):
        """Sim codes with slashes should fail."""
        assert validate_sim_code("sim/code") is False
        assert validate_sim_code("path/to/sim") is False
        assert validate_sim_code("test\\code") is False

    def test_invalid_special_characters(self):
        """Sim codes with special characters should fail."""
        assert validate_sim_code("sim code") is False  # Space
        assert validate_sim_code("sim.code") is False  # Dot
        assert validate_sim_code("sim@code") is False  # At
        assert validate_sim_code("sim!code") is False  # Exclamation
        assert validate_sim_code("sim#code") is False  # Hash
        assert validate_sim_code("sim$code") is False  # Dollar

    def test_invalid_empty_and_none(self):
        """Empty strings and None should fail."""
        assert validate_sim_code("") is False
        assert validate_sim_code(None) is False

    def test_invalid_types(self):
        """Non-string types should fail."""
        assert validate_sim_code(123) is False
        assert validate_sim_code([]) is False
        assert validate_sim_code({}) is False


class TestValidateStep:
    """Test validate_step function."""

    def test_valid_integers(self):
        """Valid non-negative integers should return the integer."""
        assert validate_step(0) == 0
        assert validate_step(1) == 1
        assert validate_step(100) == 100
        assert validate_step(999999) == 999999

    def test_valid_string_integers(self):
        """String representations of non-negative integers should work."""
        assert validate_step("0") == 0
        assert validate_step("1") == 1
        assert validate_step("100") == 100
        assert validate_step("999999") == 999999

    def test_invalid_negative(self):
        """Negative integers should return None."""
        assert validate_step(-1) is None
        assert validate_step(-100) is None
        assert validate_step("-1") is None

    def test_invalid_non_numeric(self):
        """Non-numeric strings should return None."""
        assert validate_step("abc") is None
        assert validate_step("12.5") is None  # Float strings
        assert validate_step("") is None

    def test_invalid_types(self):
        """Invalid types should return None."""
        assert validate_step(None) is None
        assert validate_step([]) is None
        assert validate_step({}) is None


class TestSafeStoragePath:
    """Test safe_storage_path function."""

    def test_valid_simple_path(self):
        """Simple valid paths should return resolved Path."""
        result = safe_storage_path("test_sim", "environment", "0.json")
        assert result is not None
        assert result.name == "0.json"
        assert "test_sim" in str(result)
        assert "environment" in str(result)

    def test_valid_storage_types(self):
        """Different storage types should use correct roots."""
        storage_path = safe_storage_path("sim", "file.json", storage_type="storage")
        assert storage_path is not None
        assert str(STORAGE_ROOT.resolve()) in str(storage_path)

        compressed_path = safe_storage_path(
            "sim", "file.json", storage_type="compressed"
        )
        assert compressed_path is not None
        assert str(COMPRESSED_STORAGE_ROOT.resolve()) in str(compressed_path)

        temp_path = safe_storage_path("sim", "file.json", storage_type="temp")
        assert temp_path is not None
        assert str(TEMP_STORAGE_ROOT.resolve()) in str(temp_path)

    def test_invalid_storage_type(self):
        """Invalid storage type should return None."""
        assert safe_storage_path("sim", "file.json", storage_type="invalid") is None

    def test_invalid_sim_code(self):
        """Invalid sim_code should return None."""
        assert safe_storage_path("../etc/passwd", "file.json") is None
        assert safe_storage_path("", "file.json") is None
        assert safe_storage_path("sim/code", "file.json") is None

    def test_path_traversal_in_parts(self):
        """Path traversal in path parts should return None."""
        assert safe_storage_path("test_sim", "..", "etc", "passwd") is None
        assert safe_storage_path("test_sim", ".", "file.json") is None
        assert safe_storage_path("test_sim", "path/to/file.json") is None
        assert safe_storage_path("test_sim", "path\\to\\file.json") is None

    def test_deeply_nested_path(self):
        """Deeply nested paths should work if valid."""
        result = safe_storage_path("test_sim", "environment", "subdir", "0.json")
        assert result is not None
        assert result.name == "0.json"


class TestValidateEnvironmentRequest:
    """Test validate_environment_request function."""

    def test_valid_request(self):
        """Valid request data should return parsed values."""
        data = {
            "step": 0,
            "sim_code": "test_sim",
            "environment": {"agents": {}},
        }
        step, sim_code, environment = validate_environment_request(data)
        assert step == 0
        assert sim_code == "test_sim"
        assert environment == {"agents": {}}

    def test_valid_request_string_step(self):
        """String step values should be converted to int."""
        data = {
            "step": "100",
            "sim_code": "test_sim",
            "environment": {},
        }
        step, sim_code, environment = validate_environment_request(data)
        assert step == 100

    def test_missing_step(self):
        """Missing step field should raise ValidationError."""
        data = {"sim_code": "test_sim", "environment": {}}
        with pytest.raises(ValidationError) as exc_info:
            validate_environment_request(data)
        assert exc_info.value.field == "step"

    def test_missing_sim_code(self):
        """Missing sim_code field should raise ValidationError."""
        data = {"step": 0, "environment": {}}
        with pytest.raises(ValidationError) as exc_info:
            validate_environment_request(data)
        assert exc_info.value.field == "sim_code"

    def test_missing_environment(self):
        """Missing environment field should raise ValidationError."""
        data = {"step": 0, "sim_code": "test_sim"}
        with pytest.raises(ValidationError) as exc_info:
            validate_environment_request(data)
        assert exc_info.value.field == "environment"

    def test_invalid_step(self):
        """Invalid step should raise ValidationError."""
        data = {"step": -1, "sim_code": "test_sim", "environment": {}}
        with pytest.raises(ValidationError) as exc_info:
            validate_environment_request(data)
        assert exc_info.value.field == "step"

    def test_invalid_sim_code(self):
        """Invalid sim_code should raise ValidationError."""
        data = {"step": 0, "sim_code": "../etc/passwd", "environment": {}}
        with pytest.raises(ValidationError) as exc_info:
            validate_environment_request(data)
        assert exc_info.value.field == "sim_code"

    def test_invalid_environment_type(self):
        """Non-dict environment should raise ValidationError."""
        data = {"step": 0, "sim_code": "test_sim", "environment": "not a dict"}
        with pytest.raises(ValidationError) as exc_info:
            validate_environment_request(data)
        assert exc_info.value.field == "environment"


class TestValidateUpdateRequest:
    """Test validate_update_request function."""

    def test_valid_request(self):
        """Valid request data should return parsed values."""
        data = {"step": 0, "sim_code": "test_sim"}
        step, sim_code = validate_update_request(data)
        assert step == 0
        assert sim_code == "test_sim"

    def test_missing_step(self):
        """Missing step field should raise ValidationError."""
        data = {"sim_code": "test_sim"}
        with pytest.raises(ValidationError) as exc_info:
            validate_update_request(data)
        assert exc_info.value.field == "step"

    def test_missing_sim_code(self):
        """Missing sim_code field should raise ValidationError."""
        data = {"step": 0}
        with pytest.raises(ValidationError) as exc_info:
            validate_update_request(data)
        assert exc_info.value.field == "sim_code"

    def test_invalid_step(self):
        """Invalid step should raise ValidationError."""
        data = {"step": "abc", "sim_code": "test_sim"}
        with pytest.raises(ValidationError) as exc_info:
            validate_update_request(data)
        assert exc_info.value.field == "step"

    def test_invalid_sim_code(self):
        """Invalid sim_code should raise ValidationError."""
        data = {"step": 0, "sim_code": "sim/code"}
        with pytest.raises(ValidationError) as exc_info:
            validate_update_request(data)
        assert exc_info.value.field == "sim_code"


class TestValidateCameraData:
    """Test validate_camera_data function."""

    def test_valid_camera_data(self):
        """Valid camera data should return the camera dict."""
        data = {"camera": {"x": 100, "y": 200, "zoom": 1.0}}
        camera = validate_camera_data(data)
        assert camera == {"x": 100, "y": 200, "zoom": 1.0}

    def test_empty_camera_dict(self):
        """Empty camera dict should be valid."""
        data = {"camera": {}}
        camera = validate_camera_data(data)
        assert camera == {}

    def test_missing_camera(self):
        """Missing camera field should raise ValidationError."""
        data = {}
        with pytest.raises(ValidationError) as exc_info:
            validate_camera_data(data)
        assert exc_info.value.field == "camera"

    def test_invalid_camera_type(self):
        """Non-dict camera should raise ValidationError."""
        data = {"camera": "not a dict"}
        with pytest.raises(ValidationError) as exc_info:
            validate_camera_data(data)
        assert exc_info.value.field == "camera"

        data = {"camera": [1, 2, 3]}
        with pytest.raises(ValidationError) as exc_info:
            validate_camera_data(data)
        assert exc_info.value.field == "camera"


class TestValidationError:
    """Test ValidationError exception."""

    def test_with_field(self):
        """ValidationError with field should store field name."""
        error = ValidationError("test message", field="test_field")
        assert error.message == "test message"
        assert error.field == "test_field"
        assert str(error) == "test message"

    def test_without_field(self):
        """ValidationError without field should work."""
        error = ValidationError("test message")
        assert error.message == "test message"
        assert error.field is None
