import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def _save_dataframe(customer_name, data, ext):
    df = pd.DataFrame(data)
    folder = "generated_files"
    os.makedirs(folder, exist_ok=True)
    filename = f"{customer_name}_orders.{ext}"
    path = os.path.join(folder, filename)
    return df, path

def generate_excel(customer_name, data):
    df, path = _save_dataframe(customer_name, data, "xlsx")
    df.to_excel(path, index=False, engine='xlsxwriter')
    return path

def generate_csv(customer_name, data):
    df, path = _save_dataframe(customer_name, data, "csv")
    df.to_csv(path, index=False)
    return path

def generate_pdf(customer_name, data):
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("pdf_template.html")
    grand_total = sum(item['price'] * item['quantity'] for item in data)
    html_content = template.render(customer_name=customer_name, orders=data, grand_total=grand_total)

    folder = "generated_files"
    os.makedirs(folder, exist_ok=True)
    filename = f"{customer_name}_orders.pdf"
    path = os.path.join(folder, filename)
    with open(path, "w+b") as result_file:
        pisa.CreatePDF(src=html_content, dest=result_file)
    return path
