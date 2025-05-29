import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def _save_dataframe(city, data, ext):
    df = pd.DataFrame(data)
    folder = "generated_files"
    os.makedirs(folder, exist_ok=True)
    filename = f"{city}_weather.{ext}"
    path = os.path.join(folder, filename)
    return df, path

def generate_excel(city, data):
    df, path = _save_dataframe(city, data, "xlsx")
    df.to_excel(path, index=False, engine='xlsxwriter')
    return path

def generate_csv(city, data):
    df, path = _save_dataframe(city, data, "csv")
    df.to_csv(path, index=False)
    return path

def generate_pdf(city, data):
    env = Environment(loader=FileSystemLoader("views"))
    template = env.get_template("pdf_template.html")
    html_content = template.render(city=city, forecast=data)

    folder = "generated_files"
    os.makedirs(folder, exist_ok=True)
    filename = f"{city}_weather.pdf"
    path = os.path.join(folder, filename)
    with open(path, "w+b") as result_file:
        pisa.CreatePDF(src=html_content, dest=result_file)
    return path
