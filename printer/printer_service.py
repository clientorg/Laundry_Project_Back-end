import win32print
import win32ui
from PIL import Image, ImageWin

import base64
import io
import os

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# -------------------------
# GET PRINTERS
# -------------------------
def get_printers():
    printers = win32print.EnumPrinters(2)
    return [p[2] for p in printers]


# -------------------------
# PRINT FUNCTION
# -------------------------
def print_image_pdf(data):

    try:
        image_data = data.get('image')
        printer_name = data.get('printer_name')
        print_type = data.get('print_type', 'invoice')
        file_name = data.get('file_name', 'print_file')

        if not image_data:
            return {"success": False, "message": "No image provided"}

        # Decode image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image_stream = io.BytesIO(image_bytes)

        # Save PDF
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        pdf_folder = os.path.join(BASE_DIR, "pdfs", print_type)
        os.makedirs(pdf_folder, exist_ok=True)

        file_path = os.path.join(pdf_folder, f"{file_name}.pdf")

        pil_image = Image.open(image_stream)
        img_width, img_height = pil_image.size

        image_stream.seek(0)
        img = ImageReader(image_stream)

        pdf_width = img_width * 0.75
        pdf_height = img_height * 0.75

        c = canvas.Canvas(file_path, pagesize=(pdf_width, pdf_height))
        c.drawImage(img, 0, 0, width=pdf_width, height=pdf_height)
        c.save()

        # -------------------------
        # PRINT (WIN32 ONLY)
        # -------------------------
        if printer_name:

            available_printers = [p[2] for p in win32print.EnumPrinters(2)]

            if printer_name not in available_printers:
                return {
                    "success": False,
                    "message": f"Invalid printer: {printer_name}"
                }

            image_stream.seek(0)
            image = Image.open(image_stream)

            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)

            printable_area = (
                hDC.GetDeviceCaps(8),
                hDC.GetDeviceCaps(10)
            )

            safe_name = str(file_name).replace("/", "_").replace("\\", "_")

            try:
                hDC.StartDoc(safe_name)
                hDC.StartPage()

                dib = ImageWin.Dib(image)

    # Original image size
                img_width, img_height = image.size

    # Printer width
                printer_width = printable_area[0]

    # Maintain aspect ratio
                ratio = printer_width / img_width

                new_width = printer_width
                new_height = int(img_height * ratio)

    # Draw image without stretching
                dib.draw(
                    hDC.GetHandleOutput(),
                    (0, 0, new_width, new_height)
                )

                hDC.EndPage()
                hDC.EndDoc()

            except Exception as e:
                print("PRINT ERROR:", str(e))
                return {
                    "success": False,
                    "message": str(e)
                }

            finally:
                hDC.DeleteDC()

        return {
            "success": True,
            "path": file_path
        }

    except Exception as e:
        print("GENERAL ERROR:", str(e))
        return {
            "success": False,
            "message": str(e)
        }