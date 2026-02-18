#!/usr/bin/env python3
"""
Verification script for Dockerfile path support.
Tests real builds with Docker and Podman (if available).
"""

import sys
from pathlib import Path
import shutil
import tempfile
from container_manager import ContainerEngineFactory, BuildContext, ContainerRuntime

def verify_engine(runtime_name: str, command: str):
    print(f"\n=== Verifying {runtime_name} ({command}) ===")
    
    try:
        if runtime_name == "Docker":
            engine = ContainerEngineFactory.create_docker(command)
        else:
            engine = ContainerEngineFactory.create_podman(command)
            
        if not engine.is_available():
            print(f"❌ {runtime_name} is not available (command: {command})")
            return

        print(f"✅ {runtime_name} is available: {engine.version()}")
        
        # Test 1: String Build
        print(f"\n[Test 1] Building from String Content...")
        context_str = BuildContext(
            dockerfile="FROM alpine:latest\nRUN echo 'String Build' > /test.txt"
        )
        try:
            img_id = engine.images.build(context_str, f"test-{command}-string")
            print(f"✅ Built image: {img_id}")
            engine.images.remove(img_id, force=True)
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 2: File Path Build
        print(f"\n[Test 2] Building from File Path...")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create Dockerfile/Containerfile
            filename = "Containerfile" if runtime_name == "Podman" else "Dockerfile"
            dockerfile = tmp_path / filename
            dockerfile.write_text("FROM alpine:latest\nRUN echo 'File Build' > /test.txt")
            
            context_path = BuildContext(
                dockerfile=dockerfile
            )
            
            try:
                img_id = engine.images.build(context_path, f"test-{command}-file")
                print(f"✅ Built image: {img_id}")
                engine.images.remove(img_id, force=True)
            except Exception as e:
                print(f"❌ Failed: {e}")

    except Exception as e:
        print(f"❌ Error initializing engine: {e}")

def main():
    # Verify Docker
    verify_engine("Docker", "docker")
    
    # Verify Podman
    # Check if podman is installed first to avoid noise
    if shutil.which("podman"):
        verify_engine("Podman", "podman")
    else:
        print("\n=== Podman not found, skipping ===")

if __name__ == "__main__":
    main()
