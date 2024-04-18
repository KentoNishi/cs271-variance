from PIL import Image

def overlay_images(background_path, overlay_path, output_path, position=(0, 0), transparency=0.5):
    """
    Overlay an image onto another image with transparency.

    Args:
    - background_path (str): Path to the background image.
    - overlay_path (str): Path to the overlay image.
    - output_path (str): Path where the resultant image will be saved.
    - position (tuple, optional): The position (x, y) where the overlay image will be placed on the background. Defaults to (0, 0).
    - transparency (float, optional): The transparency level of the overlay image. 1.0 is fully opaque, 0.0 is fully transparent. Defaults to 0.5.
    """
    # Open the background and overlay images
    background = Image.open(background_path).convert("RGBA")
    overlay = Image.open(overlay_path).convert("RGBA")

    # Resize overlay image to match the background image size
    # If your images are of different sizes, consider resizing or adjusting them appropriately
    # overlay = overlay.resize(background.size)

    # Apply transparency to overlay
    overlay_with_transparency = overlay.copy()
    if transparency < 1.0:
        for x in range(overlay.width):
            for y in range(overlay.height):
                r, g, b, a = overlay_with_transparency.getpixel((x, y))
                overlay_with_transparency.putpixel((x, y), (r, g, b, int(a * transparency)))

    # Composite the images
    combined = Image.alpha_composite(background, overlay_with_transparency)

    # Save the result
    combined.save(output_path, format="PNG")
    print(f"Image saved to {output_path}")
    
# Get all the PNG files in the current directory, except for overlay.png
import os
png_files = ['./time/' + file for file in os.listdir("./time") if file.endswith(".png") and file != "overlay.png"]
for file in png_files:
    overlay_images(file, "overlay.png", file, transparency=0.45)

png_files = ['./confidence/' + file for file in os.listdir("./confidence") if file.endswith(".png") and file != "overlay.png"]
for file in png_files:
    overlay_images(file, "overlay.png", file, transparency=0.45)  


