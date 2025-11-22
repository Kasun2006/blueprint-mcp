from enum import Enum


class DiagramType(str, Enum):
    ARCHITECTURE = "architecture"
    FLOWCHART = "flowchart"
    DATA_FLOW = "data_flow"
    SEQUENCE = "sequence"
    INFOGRAPHIC = "infographic"
    GENERIC = "generic"


class AspectRatio(str, Enum):
    SQUARE = "1:1"
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    WIDE = "21:9"
    VERTICAL_PORTRAIT = "3:4"
    HORIZONTAL_LANDSCAPE = "4:3"


class ImageSize(str, Enum):
    STANDARD = "1K"
    HIGH = "2K"


def optimize_prompt_for_nano_banana(
    base_prompt: str,
    diagram_type: DiagramType,
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
    image_size: ImageSize = ImageSize.HIGH,
    emphasis_on_text: bool = True
) -> str:
    requirements = []
    
    if emphasis_on_text:
        requirements.append(
            "All text must be crystal clear and perfectly legible. "
            "Ensure proper contrast between text and background."
        )
    
    requirements.append(f"Use {aspect_ratio.value} aspect ratio.")
    requirements.append(f"Generate at {image_size.value} resolution.")
    
    if diagram_type == DiagramType.ARCHITECTURE:
        requirements.append("Use standard architecture diagram notation.")
    elif diagram_type == DiagramType.FLOWCHART:
        requirements.append("Use standard flowchart symbols.")
    elif diagram_type == DiagramType.SEQUENCE:
        requirements.append("Use standard UML sequence notation.")
    
    optimized = base_prompt.strip()
    if requirements:
        optimized += "\n\n" + " ".join(requirements)
    
    return optimized
