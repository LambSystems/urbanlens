from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml


def resolve_path(path_value: str | Path, base_dir: str | Path) -> Path:
    path = Path(path_value)
    base_dir = Path(base_dir)
    return path if path.is_absolute() else (base_dir / path).resolve()


def resolve_repo_or_base_path(path_value: str | Path, repo_root: Path, base_dir: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] in {"backend", "docs", "frontend", "instructions"}:
        return (repo_root / path).resolve()
    return (base_dir / path).resolve()


def load_config(config_path: str | Path, project_root: str | Path) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    config_path = resolve_path(config_path, project_root)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Explicit roots
    project_dir = resolve_path(config.get("project_dir", project_root), project_root)
    dataset_dir = resolve_path(config.get("dataset_dir", project_dir), project_root)

    config["project_dir"] = str(project_dir)
    config["dataset_dir"] = str(dataset_dir)
    config["project_root"] = str(project_root)
    config["config_path"] = str(config_path)

    # Project resources folder (where project-specific files should live)
    project_resources_dir = project_dir / "resources"
    config["project_resources_dir"] = str(project_resources_dir)

    # --------
    # Resolve from DATASET DIR
    # --------
    dataset_keys = [
        "rgb_dir",
        "thermal_dir",
        "alphaearth_dir",
        "metadata_file",
        "train_split_file",
        "test_rgb_dir",
        "test_target_dir",
    ]

    for key in dataset_keys:
        if key in config and config[key] is not None:
            config[key] = str(resolve_path(config[key], dataset_dir))

    # --------
    # Resolve from PROJECT DIR
    # --------
    project_keys = [
        "src_dir",
    ]

    for key in project_keys:
        if key in config and config[key] is not None:
            config[key] = str(resolve_repo_or_base_path(config[key], project_root, project_dir))

    # --------
    # Resolve from PROJECT RESOURCES DIR
    # --------
    project_resources_keys = [
        "manifest_raw",
        "manifest_split",
        "manifest_file",
        "aligned_rgb_dir",
        "aligned_thermal_dir",
        "test_aligned_rgb_dir",
        "test_aligned_thermal_dir",
        "test_predict_dir",
        "checkpoint_dir",
        "prediction_dir",
        "metrics_dir",
        "log_dir",
    ]

    for key in project_resources_keys:
        if key in config and config[key] is not None:
            config[key] = str(resolve_repo_or_base_path(config[key], project_root, project_resources_dir))

    if "learning_rate" in config:
        config["learning_rate"] = float(config["learning_rate"])

    return config
