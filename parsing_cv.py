import pytesseract
from PIL import Image
import aspose.words as aw
from pdf2image import convert_from_path
from striprtf.striprtf import rtf_to_text
import os

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='rus+eng')
        return text
    except Exception as e:
        return f"Ошибка при обработке изображения: {str(e)}"

def extract_text_from_pdf(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        for i, image in enumerate(images):
            temp_image_path = f"temp_page_{i+1}.jpg"
            image.save(temp_image_path, 'JPEG')
            text = extract_text_from_image(temp_image_path)
            full_text += f"\n--- Страница {i+1} ---\n{text}"
            os.remove(temp_image_path)
        return full_text
    except Exception as e:
        return f"Ошибка при обработке PDF: {str(e)}"

def extract_text_from_docx(docx_path):
    try:
        doc = aw.Document(docx_path)
        text = doc.get_text()
        return text
    except Exception as e:
        return f"Ошибка при обработке DOCX: {str(e)}"

def extract_text_from_pdf_asp(pdf_path):
    try:
        doc = aw.Document(pdf_path)
        text = doc.get_text()
        return text
    except Exception as e:
        return f"Ошибка при обработке PDF с помощью Aspose.Words: {str(e)}"

def extract_text_from_rtf(rtf_path):
    try:
        with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
            rtf_content = file.read()
        text = rtf_to_text(rtf_content)
        return text
    except Exception as e:
        return f"Ошибка при обработке RTF: {str(e)}"

def main(file_path):
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
        print(f"Обработка изображения: {file_path}")
        text = extract_text_from_image(file_path)
    elif file_ext == 'pdf':
        try:
            text = extract_text_from_pdf_asp(file_path)
            if text.strip():
                print(f"Обрабаботка PDF (текстовый слой) с помощью Aspose.Words: {file_path}")
            else:
                raise Exception("PDF не содержит текстового слоя.")
        except:
            print(f"Обрабатка PDF (скан) с помощью Tesseract OCR: {file_path}")
            text = extract_text_from_pdf(file_path)
    elif file_ext in ['docx', 'doc']:
        print(f"Обработка документ Word с помощью Aspose.Words: {file_path}")
        text = extract_text_from_docx(file_path)
    elif file_ext == 'rtf':
        print(f"Обработка RTF-документ с помощью striprtf: {file_path}")
        text = extract_text_from_rtf(file_path)
    else:
        text = "Неподдерживаемый формат файла."
    
    print("\nИзвлеченный текст:\n")
    print(text)
    return text

if __name__ == "__main__":
    file_path = input("путь к файлу: ")
    main(file_path)
    cv = main(file_path)