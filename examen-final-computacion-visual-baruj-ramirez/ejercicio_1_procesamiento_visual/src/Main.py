"""
Pipeline de procesamiento de imágenes con técnicas clásicas de visión por
computador.

Pasos implementados:
    1. Carga de una imagen
    2. Conversión a escala de grises
    3. Conversión a un segundo espacio de color (HSV o LAB)
    4. Suavizado (Gaussian Blur)
    5. Detección de bordes (Canny o Sobel)
    6. Segmentación / detección de objetos
         - Técnica clásica: umbralización de Otsu + contornos
         - Modelo preentrenado: detector de rostros Haar Cascade (incluido
           con OpenCV, no requiere descargas adicionales)
    7. Guardado de todos los resultados + una imagen de comparación final

Uso:
    python pipeline_imagenes.py --image ruta/a/imagen.jpg

Argumentos opcionales:
    --output        carpeta donde se guardan los resultados (default: resultados)
    --colorspace    HSV o LAB (default: HSV)
    --edge          canny o sobel (default: canny)
    --blur-ksize    tamaño del kernel de suavizado, debe ser impar (default: 5)
"""

import argparse
import os

import cv2
import numpy as np
import matplotlib

matplotlib.use("Agg")  # permite generar imágenes sin necesidad de pantalla
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Paso 1: Carga de imagen
# ---------------------------------------------------------------------------
def load_image(path: str) -> np.ndarray:
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(
            f"No se pudo cargar la imagen en '{path}'. Verifica la ruta."
        )
    return img


# ---------------------------------------------------------------------------
# Paso 2: Escala de grises
# ---------------------------------------------------------------------------
def to_grayscale(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# ---------------------------------------------------------------------------
# Paso 3: Segundo espacio de color
# ---------------------------------------------------------------------------
def to_other_colorspace(img: np.ndarray, space: str = "HSV") -> np.ndarray:
    space = space.upper()
    if space == "HSV":
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    elif space == "LAB":
        return cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    raise ValueError("El espacio de color debe ser 'HSV' o 'LAB'.")


# ---------------------------------------------------------------------------
# Paso 4: Suavizado
# ---------------------------------------------------------------------------
def apply_smoothing(img: np.ndarray, ksize: int = 5) -> np.ndarray:
    if ksize % 2 == 0:
        ksize += 1  # GaussianBlur requiere kernel impar
    return cv2.GaussianBlur(img, (ksize, ksize), 0)


# ---------------------------------------------------------------------------
# Paso 5: Detección de bordes
# ---------------------------------------------------------------------------
def detect_edges(gray_img: np.ndarray, method: str = "canny") -> np.ndarray:
    method = method.lower()
    if method == "canny":
        return cv2.Canny(gray_img, 100, 200)
    elif method == "sobel":
        sobel_x = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(sobel_x, sobel_y)
        return cv2.convertScaleAbs(magnitude)
    raise ValueError("El método de bordes debe ser 'canny' o 'sobel'.")


# ---------------------------------------------------------------------------
# Paso 6a: Segmentación clásica (Otsu + contornos)
# ---------------------------------------------------------------------------
def segment_classic(img: np.ndarray, gray_img: np.ndarray):
    _, thresh = cv2.threshold(
        gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=15)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    result = img.copy()
    for c in contours:
        if cv2.contourArea(c) > 200:  # filtra ruido pequeño
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return result, mask


# ---------------------------------------------------------------------------
# Paso 6b: Detección con modelo preentrenado (Haar Cascade)
# ---------------------------------------------------------------------------
def detect_objects_pretrained(img: np.ndarray):
    gray = to_grayscale(img)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    result = img.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)

    return result, len(faces)


# ---------------------------------------------------------------------------
# Utilidades de guardado / comparación
# ---------------------------------------------------------------------------
def save_image(img: np.ndarray, path: str) -> None:
    cv2.imwrite(path, img)


def build_comparison_grid(images: dict, output_path: str) -> None:
    n = len(images)
    cols = 3
    rows = (n + cols - 1) // cols

    plt.figure(figsize=(cols * 4, rows * 4))
    for i, (title, img) in enumerate(images.items()):
        plt.subplot(rows, cols, i + 1)
        if img.ndim == 2:
            plt.imshow(img, cmap="gray")
        else:
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(title, fontsize=10)
        plt.axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# Paso 7 + orquestación general
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de procesamiento de imágenes (escala de grises, "
        "espacios de color, bordes, segmentación)."
    )
    parser.add_argument("--image", required=True, help="Ruta a la imagen de entrada")
    parser.add_argument("--output", default="resultados", help="Carpeta de salida")
    parser.add_argument(
        "--colorspace", default="HSV", choices=["HSV", "LAB"],
        help="Segundo espacio de color a generar",
    )
    parser.add_argument(
        "--edge", default="canny", choices=["canny", "sobel"],
        help="Método de detección de bordes",
    )
    parser.add_argument(
        "--blur-ksize", type=int, default=5, help="Tamaño del kernel de suavizado"
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("Paso 1/7: Cargando imagen...")
    img = load_image(args.image)
    save_image(img, os.path.join(args.output, "original.png"))

    print("Paso 2/7: Generando escala de grises...")
    gray = to_grayscale(img)
    save_image(gray, os.path.join(args.output, "grises.png"))

    print(f"Paso 3/7: Convirtiendo a espacio de color {args.colorspace}...")
    other_space = to_other_colorspace(img, args.colorspace)
    save_image(
        other_space, os.path.join(args.output, f"{args.colorspace.lower()}.png")
    )

    print("Paso 4/7: Aplicando suavizado (Gaussian Blur)...")
    smoothed = apply_smoothing(img, args.blur_ksize)
    save_image(smoothed, os.path.join(args.output, "suavizado.png"))
    smoothed_gray = apply_smoothing(gray, args.blur_ksize)

    print(f"Paso 5/7: Detectando bordes con {args.edge}...")
    edges = detect_edges(smoothed_gray, args.edge)
    save_image(edges, os.path.join(args.output, f"bordes_{args.edge}.png"))

    print("Paso 6/7: Segmentando / detectando objetos...")
    seg_classic, mask = segment_classic(img, gray)
    save_image(seg_classic, os.path.join(args.output, "segmentacion_clasica.png"))
    save_image(mask, os.path.join(args.output, "mascara_otsu.png"))

    seg_pretrained, n_faces = detect_objects_pretrained(img)
    save_image(
        seg_pretrained,
        os.path.join(args.output, "deteccion_modelo_preentrenado.png"),
    )
    print(f"   -> El modelo preentrenado (Haar Cascade) detectó {n_faces} rostro(s).")

    print("Paso 7/7: Guardando comparación final...")
    comparison = {
        "Original": img,
        "Escala de grises": gray,
        args.colorspace: other_space,
        "Suavizado": smoothed,
        f"Bordes ({args.edge})": edges,
        "Segmentacion clasica": seg_classic,
        "Deteccion preentrenada": seg_pretrained,
    }
    build_comparison_grid(
        comparison, os.path.join(args.output, "comparacion_final.png")
    )

    print(f"\nProceso completo. Resultados guardados en: {args.output}/")


if __name__ == "__main__":
    main()
