from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import tempfile

def generar_pdf(template_path, context, nombre_archivo):
    # Renderizamos el HTML con los datos
    html_string = render_to_string(template_path, context)
    
    # Creamos un archivo temporal para el PDF
    response = tempfile.NamedTemporaryFile(delete=False)
    
    # Configuramos el diseño del PDF (Estilos CSS para WeasyPrint)
    css = CSS(string='''
        @page { size: A4; margin: 15mm; }
        body { font-family: sans-serif; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        h1 { color: #333; }
    ''')
    
    # Generamos el PDF
    HTML(string=html_string).write_pdf(response.name, stylesheets=[css])
    
    return response.name