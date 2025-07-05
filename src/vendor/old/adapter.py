from typing import Any

from src.collaboration_document_generator import (
    Deliverable,
    DeliverableMetadata,
    DeliverableRequirement,
)


def dict_to_deliverable(data: dict[str, Any]) -> Deliverable:
    metadata = DeliverableMetadata(**data.get("output_metadata", {}))
    requirements = DeliverableRequirement(**data.get("requirements", {}))
    return Deliverable(
        id=data["id"],
        name=data["name"],
        stage=data["stage"],
        role=data["role"],
        output_type=data["output_type"],
        output_format=data["output_format"],
        output_filename=data["output_filename"],
        output_metadata=metadata,
        requirements=requirements,
    )
