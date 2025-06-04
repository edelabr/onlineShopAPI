from io import BytesIO
from fastapi import Response
from fastapi.responses import StreamingResponse
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def generate_excel(customer_name, data):
    try:
        if not data:
            return {"error": "No hay datos para generar el Excel"}
        
        buffer = BytesIO()
        df = pd.DataFrame(data)
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Orders")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={customer_name}_orders.xlsx"}
        )
    except Exception as e:
        return {"error": str(e)}


def generate_csv(customer_name, data):
    try:
        if not data:
            return {"error": "No hay datos para generar el CSV"}
        
        # Generar el archivo CSV en memoria
        buffer = BytesIO()
        df = pd.DataFrame(data)
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        # Enviar el archivo CSV al cliente
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={customer_name}_orders.csv"}
        )
    except Exception as e:
        return {"error": str(e)}

def generate_pdf(customer_name, data):
    try:
        if not data:
            return {"error": "No hay datos para generar el PDF"}
        
        env = Environment(loader=FileSystemLoader("app/templates"))
        template = env.get_template("pdf_template_orders.html")
        grand_total = sum(item['price'] * item['quantity'] for item in data)
        html_content = template.render(customer_name=customer_name, orders=data, grand_total=grand_total)

        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=buffer)
        if pisa_status.err:
            return {"error": "Error al generar el PDF"}
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={customer_name}_orders.pdf"}
        )
    except Exception as e:
        return {"error": str(e)}