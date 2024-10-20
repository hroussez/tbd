import cv2
import numpy as np

# Load the PNG image (with alpha channel)
image = cv2.imread('qr.png', cv2.IMREAD_UNCHANGED)

# Check if the image has an alpha channel
if image.shape[2] == 4:
    # Convert white (255, 255, 255) pixels to transparent (255, 255, 255, 0)
    white = np.array([255, 255, 255, 255])
    transparent = np.array([255, 255, 255, 0])

    # Create a mask where the white pixels are
    mask = np.all(image[:, :, :3] == white[:3], axis=-1)

    # Set the white pixels to transparent
    image[mask] = transparent

    # Save the result as a new PNG
    cv2.imwrite('qrt.png', image)
else:
    print("The image doesn't have an alpha channel.")