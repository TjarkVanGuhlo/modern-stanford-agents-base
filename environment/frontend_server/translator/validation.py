"""Input validation utilities for Django POST endpoints.

This module provides security functions to prevent path traversal and
other input validation vulnerabilities in the frontend server.
"""

import re
from pathlib import Path

# Root directories for storage operations
FRONTEND_ROOT = Path(__file__).parent.parent
STORAGE_ROOT = FRONTEND_ROOT / "storage"
COMPRESSED_STORAGE_ROOT = FRONTEND_ROOT / "compressed_storage"
TEMP_STORAGE_ROOT = FRONTEND_ROOT / "temp_storage"

# Pattern for valid simulation codes: alphanumeric, underscore, hyphen only
SIM_CODE_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_sim_code(sim_code: str) -> bool:
    """Validate that a simulation code contains only safe characters.

    A valid sim_code consists only of alphanumeric characters, underscores,
    and hyphens. This prevents path traversal attacks using sequences like
    '../' or other special characters.

    Args:
        sim_code: The simulation code to validate.

    Returns:
        True if the sim_code is valid, False otherwise.

    Examples:
        >>> validate_sim_code("base_the_ville_isabella")
        True
        >>> validate_sim_code("test-simulation-001")
        True
        >>> validate_sim_code("../etc/passwd")
        False
        >>> validate_sim_code("sim/code")
        False
    """
    if not sim_code or not isinstance(sim_code, str):
        return False
    return bool(SIM_CODE_PATTERN.match(sim_code))


def validate_step(step: int | str) -> int | None:
    """Validate that step is a non-negative integer.

    Args:
        step: The step value to validate (can be int or string representation).

    Returns:
        The validated step as an integer, or None if invalid.

    Examples:
        >>> validate_step(0)
        0
        >>> validate_step(100)
        100
        >>> validate_step("50")
        50
        >>> validate_step(-1)
        None
        >>> validate_step("abc")
        None
    """
    try:
        step_int = int(step)
        if step_int < 0:
            return None
        return step_int
    except (ValueError, TypeError):
        return None


def safe_storage_path(
    sim_code: str,
    *path_parts: str,
    storage_type: str = "storage",
) -> Path | None:
    """Build a safe path within storage directories, preventing traversal.

    This function constructs a path within the storage directory hierarchy
    and verifies that the resolved path stays within the allowed root.
    This prevents path traversal attacks.

    Args:
        sim_code: The simulation code (must pass validate_sim_code).
        *path_parts: Additional path components (e.g., "environment", "0.json").
        storage_type: One of "storage", "compressed", or "temp".

    Returns:
        The safe resolved Path if valid, None if path would escape root
        or sim_code is invalid.

    Examples:
        >>> safe_storage_path("test_sim", "environment", "0.json")
        PosixPath('.../storage/test_sim/environment/0.json')
        >>> safe_storage_path("../evil", "file.json") is None
        True
        >>> safe_storage_path("test_sim", "..", "..", "etc", "passwd") is None
        True
    """
    if not validate_sim_code(sim_code):
        return None

    # Select the appropriate root directory
    root_map = {
        "storage": STORAGE_ROOT,
        "compressed": COMPRESSED_STORAGE_ROOT,
        "temp": TEMP_STORAGE_ROOT,
    }
    root = root_map.get(storage_type)
    if root is None:
        return None

    # Build the path
    path = root / sim_code
    for part in path_parts:
        # Reject parts that could be path traversal
        if part in (".", "..") or "/" in part or "\\" in part:
            return None
        path = path / part

    # Resolve to absolute path and verify it's within root
    try:
        resolved = path.resolve()
        root_resolved = root.resolve()

        # Check the path starts with the root (prevent traversal)
        if (
            not str(resolved).startswith(str(root_resolved) + "/")
            and resolved != root_resolved
        ):
            return None

        return resolved
    except (OSError, ValueError):
        return None


class ValidationError(Exception):
    """Exception raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_environment_request(data: dict) -> tuple[int, str, dict]:
    """Validate a process_environment request payload.

    Args:
        data: The JSON request data containing step, sim_code, and environment.

    Returns:
        A tuple of (step, sim_code, environment) if valid.

    Raises:
        ValidationError: If any field is invalid or missing.
    """
    # Validate required fields exist
    if "step" not in data:
        raise ValidationError("Missing required field", field="step")
    if "sim_code" not in data:
        raise ValidationError("Missing required field", field="sim_code")
    if "environment" not in data:
        raise ValidationError("Missing required field", field="environment")

    # Validate step
    step = validate_step(data["step"])
    if step is None:
        raise ValidationError("Must be a non-negative integer", field="step")

    # Validate sim_code
    sim_code = data["sim_code"]
    if not validate_sim_code(sim_code):
        raise ValidationError(
            "Must contain only alphanumeric characters, underscores, and hyphens",
            field="sim_code",
        )

    # Validate environment is a dict
    environment = data["environment"]
    if not isinstance(environment, dict):
        raise ValidationError("Must be a JSON object", field="environment")

    return step, sim_code, environment


def validate_update_request(data: dict) -> tuple[int, str]:
    """Validate an update_environment request payload.

    Args:
        data: The JSON request data containing step and sim_code.

    Returns:
        A tuple of (step, sim_code) if valid.

    Raises:
        ValidationError: If any field is invalid or missing.
    """
    # Validate required fields exist
    if "step" not in data:
        raise ValidationError("Missing required field", field="step")
    if "sim_code" not in data:
        raise ValidationError("Missing required field", field="sim_code")

    # Validate step
    step = validate_step(data["step"])
    if step is None:
        raise ValidationError("Must be a non-negative integer", field="step")

    # Validate sim_code
    sim_code = data["sim_code"]
    if not validate_sim_code(sim_code):
        raise ValidationError(
            "Must contain only alphanumeric characters, underscores, and hyphens",
            field="sim_code",
        )

    return step, sim_code


def validate_camera_data(data: dict) -> dict:
    """Validate path_tester_update request payload.

    Args:
        data: The JSON request data containing camera information.

    Returns:
        The camera dict if valid.

    Raises:
        ValidationError: If camera field is invalid or missing.
    """
    if "camera" not in data:
        raise ValidationError("Missing required field", field="camera")

    camera = data["camera"]
    if not isinstance(camera, dict):
        raise ValidationError("Must be a JSON object", field="camera")

    return camera
