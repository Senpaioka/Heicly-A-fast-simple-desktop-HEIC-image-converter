"""Image processing engine powered by pillow-heif and Pillow."""

import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pillow_heif  # type: ignore[import-untyped]
from PIL import Image, ImageOps

from app.core.types import ConversionOptions, ConversionResult, ExifData, ImageDimensions
from app.utils.logger import get_logger

logger = get_logger()

# Register HEIF opener with Pillow so Image.open works seamlessly with HEIC files
pillow_heif.register_heif_opener()


class ImageProcessor:
    """Handles HEIC decoding, metadata extraction, transformations, and encoding."""

    def __init__(self) -> None:
        pass

    def get_image_info(self, file_path: Path) -> Tuple[ImageDimensions, ExifData]:
        """Read HEIC image dimensions and EXIF metadata without full pixel decoding when possible."""
        try:
            heif_file = pillow_heif.read_heif(str(file_path))
            width: int = heif_file.size[0]
            height: int = heif_file.size[1]
            dims = ImageDimensions(width=width, height=height)

            orientation: int = 1
            raw_exif: Optional[bytes] = None

            if heif_file.info and "exif" in heif_file.info:
                raw_exif = heif_file.info["exif"]

            # Check orientation in metadata
            if heif_file.info and "orientation" in heif_file.info:
                try:
                    orientation = int(heif_file.info["orientation"])
                except (ValueError, TypeError):
                    orientation = 1

            exif_data = ExifData(raw_data=raw_exif, orientation=orientation)
            return dims, exif_data
        except Exception as err:
            logger.warning(f"Could not read fast metadata for {file_path}: {err}")
            # Fall back to standard Pillow open
            with Image.open(file_path) as raw_img:
                dims = ImageDimensions(width=raw_img.width, height=raw_img.height)
                exif_data = ExifData(raw_data=raw_img.info.get("exif"), orientation=1)
                return dims, exif_data

    def composite_background(
        self, img: Image.Image, bg_color: Tuple[int, int, int, int]
    ) -> Image.Image:
        """Composite image with alpha channel over a solid background color."""
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            converted_img = img.convert("RGBA")
            bg = Image.new("RGBA", converted_img.size, bg_color)
            composite = Image.alpha_composite(bg, converted_img)
            return composite.convert("RGB")
        return img.convert("RGB") if img.mode != "RGB" else img

    def resize_image(
        self,
        img: Image.Image,
        target_w: Optional[int],
        target_h: Optional[int],
        keep_aspect: bool = True,
    ) -> Image.Image:
        """Resize image to target width/height using high-quality LANCZOS resampling."""
        if not target_w and not target_h:
            return img

        orig_w, orig_h = img.size

        if keep_aspect:
            if target_w and target_h:
                # Calculate constrained dimensions
                ratio = min(target_w / orig_w, target_h / orig_h)
                new_w = max(1, int(orig_w * ratio))
                new_h = max(1, int(orig_h * ratio))
            elif target_w:
                ratio = target_w / orig_w
                new_w = target_w
                new_h = max(1, int(orig_h * ratio))
            else:
                assert target_h is not None
                ratio = target_h / orig_h
                new_w = max(1, int(orig_w * ratio))
                new_h = target_h
        else:
            new_w = target_w if target_w else orig_w
            new_h = target_h if target_h else orig_h

        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def convert(self, input_path: Path, output_path: Path, options: ConversionOptions) -> ConversionResult:
        """Convert a HEIC image file according to given options and save to output_path."""
        start_time: float = time.time()

        if not input_path.exists():
            return ConversionResult(
                input_path=input_path,
                output_path=None,
                status="error",
                message=f"Input file does not exist: {input_path}",
                duration_sec=0.0,
            )

        try:
            # Ensure target parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(input_path) as raw_image:
                processed_img: Image.Image = raw_image
                # 1. Apply Orientation if required
                if options.preserve_orientation:
                    try:
                        processed_img = ImageOps.exif_transpose(processed_img)
                    except Exception as ex_err:
                        logger.debug(f"exif_transpose failed for {input_path}: {ex_err}")

                # 2. Resize image if target dimensions provided
                processed_img = self.resize_image(
                    processed_img,
                    target_w=options.resize_width,
                    target_h=options.resize_height,
                    keep_aspect=options.preserve_aspect,
                )

                # 3. Target Format & Color Mode handling
                fmt: str = options.output_format.upper()
                if fmt == "JPEG":
                    fmt = "JPG"

                save_kwargs: Dict[str, Any] = {}

                # Format specific settings
                if fmt in ("JPG", "JPEG"):
                    processed_img = self.composite_background(processed_img, options.bg_color)
                    save_kwargs["quality"] = options.quality
                    save_kwargs["optimize"] = True
                    save_format = "JPEG"
                elif fmt == "PNG":
                    if processed_img.mode not in ("RGB", "RGBA"):
                        processed_img = processed_img.convert("RGBA")
                    save_kwargs["optimize"] = True
                    save_format = "PNG"
                elif fmt == "WEBP":
                    if processed_img.mode not in ("RGB", "RGBA"):
                        processed_img = processed_img.convert("RGBA")
                    save_kwargs["quality"] = options.quality
                    save_kwargs["method"] = 6
                    save_format = "WEBP"
                else:
                    raise ValueError(f"Unsupported output format: {fmt}")

                # Preserve EXIF data if present and requested
                if options.preserve_exif and "exif" in raw_image.info:
                    save_kwargs["exif"] = raw_image.info["exif"]

                # Save converted image
                processed_img.save(output_path, format=save_format, **save_kwargs)

            elapsed: float = time.time() - start_time
            return ConversionResult(
                input_path=input_path,
                output_path=output_path,
                status="success",
                message="Converted successfully",
                duration_sec=elapsed,
            )

        except Exception as err:
            elapsed = time.time() - start_time
            logger.error(f"Failed converting {input_path}: {err}", exc_info=True)
            return ConversionResult(
                input_path=input_path,
                output_path=output_path,
                status="error",
                message=str(err),
                duration_sec=elapsed,
            )
