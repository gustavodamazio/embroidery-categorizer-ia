
"""
PyEmbroidery converter implementation.
"""
import tempfile
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw
import pyembroidery
from loguru import logger

from domain.repositories import ImageConverterRepository
from domain.value_objects import FilePath
from domain.exceptions import ConversionError


class PyEmbroideryConverter(ImageConverterRepository):
    """
    Converter implementation using pyembroidery and PIL.
    """
    
    def __init__(self, image_size: tuple = (800, 600), background_color: str = "white"):
        self.image_size = image_size
        self.background_color = background_color
    
    def convert_pes_to_jpg(self, pes_file_path: FilePath, output_path: FilePath) -> bool:
        """
        Converts a .PES file to JPG.
        """
        logger.info(f"Converting {pes_file_path.path.name} to JPG")
        
        try:
            # Load the embroidery pattern
            pattern = pyembroidery.read(str(pes_file_path))
            
            if not pattern.stitches:
                logger.warning(f"File {pes_file_path.path.name} contains no embroidery stitches")
                return False
            
            # Extract the stitches
            stitches = pattern.stitches
            
            # Calculate dimensions based on stitches
            x_coords = [stitch[0] for stitch in stitches if len(stitch) >= 2]
            y_coords = [stitch[1] for stitch in stitches if len(stitch) >= 2]
            
            if not x_coords or not y_coords:
                logger.warning(f"File {pes_file_path.path.name} contains no valid coordinates")
                return False
            
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
            
            # Calculate image size with padding
            padding = 50
            pattern_width = max_x - min_x
            pattern_height = max_y - min_y
            
            # Use configured size or calculate based on pattern
            if pattern_width > 0 and pattern_height > 0:
                scale_x = (self.image_size[0] - 2 * padding) / pattern_width
                scale_y = (self.image_size[1] - 2 * padding) / pattern_height
                scale = min(scale_x, scale_y, 1.0)  # Don't scale beyond original size
            else:
                scale = 1.0
            
            img_width = int(pattern_width * scale) + 2 * padding
            img_height = int(pattern_height * scale) + 2 * padding
            
            # Create the image
            img = Image.new('RGB', (img_width, img_height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Draw the stitches
            prev_point = None
            stitch_color = "black"
            
            for i, stitch in enumerate(stitches):
                if len(stitch) < 2:
                    continue
                
                x, y = stitch[0], stitch[1]
                command = stitch[2] if len(stitch) > 2 else pyembroidery.STITCH
                
                # Adjust coordinates
                adjusted_x = int((x - min_x) * scale) + padding
                adjusted_y = int((y - min_y) * scale) + padding
                current_point = (adjusted_x, adjusted_y)
                
                # Change color based on command
                if command == pyembroidery.COLOR_CHANGE:
                    # Alternate between colors for visualization
                    colors = ["black", "red", "blue", "green", "purple", "orange"]
                    color_index = (i // 100) % len(colors)
                    stitch_color = colors[color_index]
                    prev_point = current_point
                    continue
                elif command == pyembroidery.JUMP:
                    prev_point = current_point
                    continue
                elif command in [pyembroidery.TRIM, pyembroidery.STOP]:
                    prev_point = None
                    continue
                
                # Draw line from previous point to current
                if prev_point and command == pyembroidery.STITCH:
                    draw.line([prev_point, current_point], fill=stitch_color, width=2)
                
                prev_point = current_point
            
            # Ensure output directory exists
            output_path.path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the image
            img.save(str(output_path), "JPEG", quality=95)
            
            logger.info(f"Conversion completed: {output_path.path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting {pes_file_path.path.name}: {e}")
            raise ConversionError(f"Conversion error: {e}")
    
    def cleanup_temporary_images(self, image_paths: list[FilePath]) -> None:
        """
        Remove temporary images.
        """
        for image_path in image_paths:
            try:
                if image_path.exists():
                    image_path.path.unlink()
                    logger.debug(f"Temporary image removed: {image_path}")
            except Exception as e:
                logger.warning(f"Error removing temporary image {image_path}: {e}")
    
    def create_temp_jpg_path(self, pes_file_name: str) -> FilePath:
        """
        Creates a temporary path for the JPG image.
        """
        temp_dir = Path(tempfile.gettempdir()) / "embroidery_categorizer"
        temp_dir.mkdir(exist_ok=True)
        
        jpg_name = Path(pes_file_name).stem + ".jpg"
        temp_path = temp_dir / jpg_name
        
        return FilePath(temp_path)
