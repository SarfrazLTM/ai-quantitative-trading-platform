"""
Model registry.

Provides a lightweight registry for managing versioned model
artifacts used by the production inference pipeline.

The registry is intentionally separated from model training.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ModelArtifact:
    """Metadata describing a registered model artifact."""

    name: str
    version: str
    path: Path
    model_type: str
    status: str = "active"


class ModelRegistry:
    """
    Manage versioned model artifacts.

    The registry provides a simple abstraction that can later be
    backed by a database, object store, MLflow, or another model
    registry service.

    Example:

        registry = ModelRegistry("models/artifacts")

        artifact = registry.register(
            name="market_structure",
            version="1.0.0",
            model_type="xgboost",
        )

        active = registry.get_active("market_structure")
    """

    def __init__(
        self,
        root_path: str | Path,
    ) -> None:
        self.root_path = Path(root_path)

        self.root_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._artifacts: dict[
            tuple[str, str],
            ModelArtifact,
        ] = {}

    def register(
        self,
        name: str,
        version: str,
        model_type: str,
        status: str = "active",
    ) -> ModelArtifact:
        """
        Register a model artifact.

        The actual trained model file is intentionally handled
        separately from the registry metadata.
        """

        model_directory = (
            self.root_path
            / name
            / version
        )

        model_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifact = ModelArtifact(
            name=name,
            version=version,
            path=model_directory,
            model_type=model_type,
            status=status,
        )

        self._artifacts[(name, version)] = artifact

        return artifact

    def get(
        self,
        name: str,
        version: str,
    ) -> ModelArtifact:
        """Return a specific model version."""

        key = (name, version)

        try:
            return self._artifacts[key]
        except KeyError as exc:
            raise KeyError(
                f"Model '{name}' version '{version}' "
                "is not registered."
            ) from exc

    def get_active(
        self,
        name: str,
    ) -> ModelArtifact:
        """Return the active version of a model."""

        matches = [
            artifact
            for artifact in self._artifacts.values()
            if artifact.name == name
            and artifact.status == "active"
        ]

        if not matches:
            raise KeyError(
                f"No active model found for '{name}'."
            )

        if len(matches) > 1:
            raise RuntimeError(
                f"Multiple active versions found for '{name}'."
            )

        return matches[0]

    def activate(
        self,
        name: str,
        version: str,
    ) -> ModelArtifact:
        """Activate one model version."""

        target = self.get(name, version)

        for key, artifact in self._artifacts.items():
            if artifact.name == name:
                self._artifacts[key] = ModelArtifact(
                    name=artifact.name,
                    version=artifact.version,
                    path=artifact.path,
                    model_type=artifact.model_type,
                    status=(
                        "active"
                        if artifact.version == version
                        else "inactive"
                    ),
                )

        return target

    def list_models(self) -> tuple[ModelArtifact, ...]:
        """Return all registered model artifacts."""

        return tuple(self._artifacts.values())