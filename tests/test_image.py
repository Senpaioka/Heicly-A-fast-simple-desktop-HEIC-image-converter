"""Unit tests for ImageProcessor logic."""

from PIL import Image
from app.core.image import ImageProcessor


def test_resize_image_aspect_ratio() -> None:
    processor = ImageProcessor()
    img = Image.new("RGB", (1000, 500))  # 2:1 aspect ratio

    resized = processor.resize_image(img, target_w=500, target_h=500, keep_aspect=True)
    # Width 500, height should be 250 to keep 2:1 ratio
    assert resized.size == (500, 250)


def test_resize_image_fixed() -> None:
    processor = ImageProcessor()
    img = Image.new("RGB", (1000, 500))

    resized = processor.resize_image(img, target_w=300, target_h=300, keep_aspect=False)
    assert resized.size == (300, 300)


def test_composite_background() -> None:
    processor = ImageProcessor()
    # Image with semi-transparent alpha
    img_rgba = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    bg_color = (0, 255, 0, 255)  # Green background

    composite = processor.composite_background(img_rgba, bg_color)
    assert composite.mode == "RGB"
    assert composite.size == (100, 100)
