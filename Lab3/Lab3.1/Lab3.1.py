# -*- coding: cp1250 -*-

import time
from multiprocessing import Pool, cpu_count
import numpy as np
from PIL import Image
from scipy.ndimage import sobel
import cv2

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

def sobel_filter(image_chunk: np.ndarray) -> np.ndarray:
    if image_chunk.ndim == 3:
        gray = cv2.cvtColor(image_chunk, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_chunk.copy()

    grad_x = sobel(gray, axis=1)
    grad_y = sobel(gray, axis=0)

    #Obliczenie amplitudy i normalizacja
    magnitude = np.hypot(grad_x, grad_y)
    max_val = magnitude.max()
    if max_val > 0:
        magnitude = (magnitude / max_val) * 255.0

    return magnitude.astype(np.uint8)


def split_image(image: Image.Image, n_chunks: int) -> list[np.ndarray]:
    img_array = np.array(image)
    chunks = np.array_split(img_array, n_chunks, axis=0)
    return chunks


def merge_chunks(chunks: list[np.ndarray]) -> Image.Image:
    merged_array = np.vstack(chunks)
    return Image.fromarray(merged_array)


def main():
    image_path = "obraz.png"  # Ścieżka do pliku wejściowego
    output_path = "obrazsobel.png"

    # Pobieranie liczby rdzeni procesora (ilość chunków na które zostanie podzielony obraz)
    num_processes = cpu_count()
    print(f"Uruchamiono przetwarzanie dla {num_processes} procesów")

    try:
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        print(
            f"Nie znaleziono pliku '{image_path}'"
        )
        return

    start_time = time.time()

    fragments = split_image(image, num_processes)

    with Pool(processes=num_processes) as pool:
        processed_fragments = pool.map(sobel_filter, fragments)

    result_image = merge_chunks(processed_fragments)
    result_image.save(output_path)

    elapsed_time = time.time() - start_time
    print(
        f"Przetwarzanie zakończone w czasie: {elapsed_time:.4f} s"
    )


if __name__ == "__main__":
    main()
