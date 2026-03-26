from PIL import Image
from glob import glob

import argparse
import os


def create_gif(image_folder: str, output_path: str, fps:int=30, loop: int=0):
    """
    Create a GIF from images in a directory.
    
    Parameters:
    -----------
    image_folder : str
        Path to the folder containing images
    output_path : str
        Path for the output GIF file
    duration : int or list
        Duration for each frame in milliseconds
        - Single value: same duration for all frames
        - List: individual duration for each frame
    loop : int
        Number of times to loop (0 = infinite loop)
    """
        # Get list of image files
    image_files = [f for f in glob(f"{image_folder}/*.png")]

    def get_image_no(x):
        _x = x.split(image_folder)[-1].split("_")[0].replace("\\", "").strip()
        return int(_x)
    image_files.sort(key=lambda x: get_image_no(x))

    duration = int(1000 / fps)

    print(f"Found {len(image_files)} images")
    
    # Load images
    images = []
    for image_file in image_files:
        img = Image.open(image_file)
        images.append(img)
    
    # Save as GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop,
        optimize=True
    )
    
    print(f"GIF saved to {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="The input _folder_")
    parser.add_argument("--output", required=True, help="The output path")
    parser.add_argument("--fps", default=24, type=int, required=False, help="FPS for the gif")
    parser.add_argument("--loop", default=0, type=int, required=False, help="zero (always) or k times")

    args = parser.parse_args()

    _ = create_gif(image_folder=args.input, output_path=args.output, fps=args.fps, loop=args.loop)

