# Too Much Light Challenge

## Overview

The "Too Much Light" challenge presents participants with an image where a flag is hidden. The flag is almost indistinguishable from the background due to intense brightness. The challenge is to manipulate the image to reveal the hidden flag.

## Challenge Description

Participants are provided with an image that appears overwhelmingly bright, making it difficult to discern any details. The flag is hidden within this image, and the colors of the flag and the background are very similar, with only a slight difference.

The objective is to reveal the hidden flag by adjusting the brightness and contrast of the image.

## Solution Approach

To find the flag in the image, participants can follow these steps:

1. **Load the Image**: Use an image processing library such as PIL (Python Imaging Library) to load the provided image.
2. **Identify the Bright Pixels**: Detect pixels that have the maximum brightness values (e.g., (255, 255, 255)).
3. **Invert the Bright Pixels**: Change the color of the brightest pixels to a contrasting color, such as black (0, 0, 0). This will make the flag, which has slightly different brightness, stand out against the altered background.

### Example Code

Below is an example code snippet demonstrating how to reveal the flag using the PIL library. 

First, install the Pillow library:
```sh
pip install pillow
```

Next, use the following Python code to process the image:

```python
from PIL import Image
from os.path import abspath, dirname

def reveal_flag(image_path):
    directory_location = abspath(dirname(image_path))
    output_path = directory_location + "/TooMuchLight_revealed_flag_image.png"
    # Load the image
    im = Image.open(image_path)
    pixels = list(im.getdata())
    size = im.size

    # Process the pixels
    for i in range(len(pixels)):
        if pixels[i] == (255, 255, 255):
            pixels[i] = (0, 0, 0)

    # Create a new image with the processed pixels
    im = Image.new("RGB", size)
    im.putdata(pixels)
    im.save(output_path)
    return output_path

# Example usage
image_path = "path_to_image"
output_path = reveal_flag(image_path)
print("Flag revealed imaged generated at:", output_path)
```

### Explanation

1. **Loading the Image**: The `Image.open` function from PIL is used to load the input image.
2. **Processing the Pixels**: The image data is converted to a list of pixel values. Each pixel is checked to see if it has the maximum brightness value (255, 255, 255). If it does, the pixel's color is changed to black (0, 0, 0).
3. **Saving the Image**: A new image is created with the processed pixel data, and it is saved to the specified output path.

By following this approach, participants can effectively reveal the hidden flag in the overly bright image.

## Conclusion

The "Too Much Light" challenge is an exercise in image processing, where participants need to adjust the brightness of an image to reveal hidden details. By identifying and inverting the brightest pixels, the hidden flag can be made visible.
