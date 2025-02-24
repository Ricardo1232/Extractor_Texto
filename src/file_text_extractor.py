import os
import cv2
import pytesseract
import fitz  # PyMuPDF
import numpy as np
from tqdm import tqdm
import logging
import sys
import easyocr
import language_tool_python
import spacy
import re

# Configuración de Tesseract (ajusta la ruta si es necesario)
pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

temp_image_folder = "processed_images"

# Crear la carpeta si no existe
if not os.path.exists(temp_image_folder):
    os.makedirs(temp_image_folder)

# Cargar spaCy para ingles
nlp = spacy.load('en_core_web_sm')

# Inicializar LanguageTool para corrección gramatical
tool = language_tool_python.LanguageTool('en')

# Inicializar EasyOCR
reader = easyocr.Reader(['es'])

def preprocess_image(image):
    try:
        # Aumento de resolución
        scale_factor = 2
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)
        logging.debug('Resolución de imagen aumentada.')

        # Conversión a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        logging.debug('Imagen convertida a escala de grises.')

        # Normalización de iluminación
        img_float = gray.astype(np.float32) / 255.0
        mean = cv2.blur(img_float, (50, 50))
        normalized = img_float / (mean + 1e-6)
        normalized = np.clip(normalized * 255, 0, 255).astype(np.uint8)
        logging.debug('Iluminación normalizada.')

        # Filtrado bilateral para eliminar ruido
        filtered = cv2.bilateralFilter(normalized, 9, 75, 75)
        logging.debug('Filtro bilateral aplicado.')

        # Umbralización adaptativa
        thresh = cv2.adaptiveThreshold(
            filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 10
        )
        logging.debug('Umbralización adaptativa aplicada.')

        # Operaciones morfológicas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        logging.debug('Operaciones morfológicas aplicadas.')

        return morph
    except Exception as e:
        logging.error(f'Error en preprocess_image: {e}')
        raise

def extract_text_from_image(image, page_number):
    try:
        logging.info(f'Procesando la página {page_number}')

        # Preprocesamiento de la imagen
        processed_image = preprocess_image(image)

        # Guardar imagen procesada para depuración en la carpeta temporal
        processed_image_path = os.path.join(temp_image_folder, f'processed_page_{page_number}.png')
        cv2.imwrite(processed_image_path, processed_image)
        logging.debug(f'Imagen procesada guardada como {processed_image_path}')

        # Extracción con Tesseract
        custom_config = r'--oem 3 --psm 6 -l spa'
        text_tesseract = pytesseract.image_to_string(processed_image, config=custom_config)
        logging.debug(f'Texto extraído con Tesseract de la página {page_number}.')

        # Extracción con EasyOCR
        result = reader.readtext(processed_image, detail=0, paragraph=True)
        text_easyocr = '\n'.join(result)
        logging.debug(f'Texto extraído con EasyOCR de la página {page_number}.')

        # Combinar textos usando algoritmo de votación
        combined_text = combine_texts(text_tesseract, text_easyocr)
        logging.debug(f'Texto combinado de la página {page_number}.')

        # Corrección ortográfica y gramatical
        corrected_text = correct_text(combined_text)
        logging.debug(f'Texto corregido de la página {page_number}.')

        # Eliminar la imagen procesada después de extraer el texto
        os.remove(processed_image_path)
        logging.debug(f'Imagen procesada eliminada: {processed_image_path}')

        return corrected_text
    except Exception as e:
        logging.error(f'Error al extraer texto de la página {page_number}: {e}')
        return ''  # Devolver cadena vacía si hay un error

def combine_texts(text1, text2):
    # Dividir textos en líneas
    lines1 = text1.strip().splitlines()
    lines2 = text2.strip().splitlines()

    # Asegurar que ambas listas tengan la misma longitud
    max_len = max(len(lines1), len(lines2))
    lines1.extend([''] * (max_len - len(lines1)))
    lines2.extend([''] * (max_len - len(lines2)))

    combined_lines = []
    for line1, line2 in zip(lines1, lines2):
        # Si las líneas son iguales, mantener una
        if line1.strip() == line2.strip():
            combined_lines.append(line1.strip())
        else:
            # Si no, elegir la línea con más palabras o caracteres
            if len(line1.strip()) > len(line2.strip()):
                combined_lines.append(line1.strip())
            else:
                combined_lines.append(line2.strip())

    combined_text = '\n'.join(combined_lines)
    return combined_text

def correct_text(text):
    # Limpieza básica del texto
    text = clean_text(text)
    # Corrección gramatical con LanguageTool
    corrected_text = tool.correct(text)
    return corrected_text

def clean_text(text):
    # Eliminar caracteres no deseados y normalizar espacios
    text = re.sub(r'[^\w\sÁÉÍÓÚáéíóúÑñ.,;:¡!¿?\'"-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path, output_txt_path):
    try:
        doc = fitz.open(pdf_path)
        num_pages = doc.page_count
        logging.info(f'Número total de páginas: {num_pages}')
    except Exception as e:
        logging.error(f'Error al abrir el PDF: {e}')
        sys.exit(1)

    full_text = ''

    # Utilizar tqdm para la barra de progreso
    for page_number, page in enumerate(tqdm(doc, desc='Procesando páginas', unit='pág'), start=1):
        try:
            pix = page.get_pixmap()
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

            if img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                logging.debug(f'Canal alfa detectado y eliminado en la página {page_number}.')

            text = extract_text_from_image(img, page_number)

            # Unificar texto manteniendo la estructura
            full_text += f'{text}\n\n'
        except Exception as e:
            logging.error(f'Error al procesar la página {page_number}: {e}')
            continue  # Continuar con la siguiente página

    # Escribir el texto extraído en el archivo de salida
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        logging.info(f'Texto extraído guardado en {output_txt_path}')
    except Exception as e:
        logging.error(f'Error al escribir el archivo de salida: {e}')
        sys.exit(1)

        
# Ejemplo de uso
if __name__ == '__main__':
    
    pdf_path = 'C:/Users/Fabian/Documents/Universidad/8 - Octavo semestre/Clasificacion inteligente de datos/Clasificación #20/Tricks And Tips/Python_Tricks_And_Tips_9th_Edition_2022.pdf'
    output_txt_path = 'salida.txt'
    import winsound
    import time
    inicio = time.time()

    try:
        # Intentar extraer el texto del PDF
        extract_text_from_pdf(pdf_path, output_txt_path)
    except Exception as e:
        # Si ocurre un error, emitir un sonido de error
        winsound.Beep(1500, 800)  # Sonido bajo en frecuencia
        winsound.Beep(1500, 800)  # Repetir para mayor claridad
        winsound.Beep(1500, 800)  # Repetir para mayor claridad
        print(f"Error: {e}")
    else:
        # Si el proceso es exitoso, emitir un sonido de éxito
        winsound.Beep(4500, 1000)  # Sonido de éxito

    # Mostrar el tiempo transcurrido
    tiempo_segundos = time.time() - inicio

    # Convertir el tiempo en minutos
    tiempo_minutos = tiempo_segundos / 60

    # Mostrar el tiempo transcurrido en minutos
    print(f'Tiempo transcurrido: {tiempo_minutos:.2f} minutos')