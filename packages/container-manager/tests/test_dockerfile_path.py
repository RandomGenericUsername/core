"""Tests for Dockerfile path support."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from container_manager.core.types import BuildContext
from container_manager.implementations.docker.image import DockerImageManager


@pytest.fixture
def mock_run_command():
    """Mock run_docker_command."""
    with patch(
        "container_manager.implementations.docker.image.run_docker_command"
    ) as mock:
        mock.return_value.stdout = b"Successfully built 1234567890ab\n"
        yield mock


@pytest.fixture
def image_manager():
    """Create DockerImageManager instance."""
    return DockerImageManager()


def test_build_with_path(image_manager, mock_run_command, tmp_path):
    """Test building with Dockerfile path."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM alpine")
    
    context = BuildContext(dockerfile=dockerfile)
    
    image_manager.build(context, "test-image")
    
    # Verify command
    args, kwargs = mock_run_command.call_args
    cmd = args[0]
    
    assert "-f" in cmd
    assert str(dockerfile) in cmd
    assert str(dockerfile.parent) in cmd  # Context should be parent dir
    assert kwargs["input_data"] is None  # No stdin input


def test_build_with_path_and_context(image_manager, mock_run_command, tmp_path):
    """Test building with Dockerfile path and explicit context."""
    dockerfile = tmp_path / "other" / "Dockerfile"
    dockerfile.parent.mkdir()
    dockerfile.write_text("FROM alpine")
    
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    
    context = BuildContext(
        dockerfile=dockerfile,
        context_path=context_dir
    )
    
    image_manager.build(context, "test-image")
    
    args, kwargs = mock_run_command.call_args
    cmd = args[0]
    
    assert str(dockerfile) in cmd
    assert str(context_dir) in cmd
    assert kwargs["input_data"] is None


def test_build_with_string_and_context(image_manager, mock_run_command, tmp_path):
    """Test building with string content and explicit context."""
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    
    context = BuildContext(
        dockerfile="FROM alpine",
        context_path=context_dir
    )
    
    image_manager.build(context, "test-image")
    
    args, kwargs = mock_run_command.call_args
    cmd = args[0]
    
    # Should have written Dockerfile to context dir
    expected_dockerfile = context_dir / "Dockerfile"
    assert expected_dockerfile.exists()
    assert expected_dockerfile.read_text() == "FROM alpine"
    
    assert "-f" in cmd
    assert str(expected_dockerfile) in cmd
    assert str(context_dir) in cmd
    assert kwargs["input_data"] is None


def test_build_legacy_string(image_manager, mock_run_command):
    """Test legacy build with string content (tarball)."""
    context = BuildContext(dockerfile="FROM alpine")
    
    image_manager.build(context, "test-image")
    
    args, kwargs = mock_run_command.call_args
    cmd = args[0]
    
    assert "-" in cmd  # Stdin
    assert kwargs["input_data"] is not None  # Tarball data provided


def test_build_with_extra_files_path_mode(image_manager, mock_run_command, tmp_path):
    """Test writing extra files in path mode."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM alpine")
    
    context = BuildContext(
        dockerfile=dockerfile,
        files={"extra.txt": b"content"}
    )
    
    image_manager.build(context, "test-image")
    
    # Should have written extra file to parent dir
    extra_file = dockerfile.parent / "extra.txt"
    assert extra_file.exists()
    assert extra_file.read_bytes() == b"content"
