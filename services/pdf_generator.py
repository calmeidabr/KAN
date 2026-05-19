from fpdf import FPDF
import tempfile

def clean_text(s):
    if not s: return ""
    s = str(s).replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-').replace('—', '-')
    s = s.replace("<b>", "").replace("</b>", "").replace("<br>", "\n")
    return s.encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf(nome, data_nasc_str, dados, titulo="Mapa Numerologico Cabalistico"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, clean_text(titulo), ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 7, f"Nome: {clean_text(nome)}", ln=True)
    pdf.cell(190, 7, f"Data de Nascimento: {data_nasc_str}", ln=True)
    pdf.ln(5)
    
    col1 = 60
    col2 = 130
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col1, 8, clean_text("Campo"), 1, 0, 'L', True)
    pdf.cell(col2, 8, clean_text("Resultado"), 1, 1, 'L', True)
    
    pdf.set_font("Arial", '', 9)
    for row in dados:
        campo = clean_text(row.get('Campo', ''))
        resultado = clean_text(row.get('Resultado', ''))
        
        linhas_estimadas = max(1, (len(resultado) // 80) + 1)
        altura_linha = linhas_estimadas * 6
        
        if pdf.get_y() + altura_linha > 275:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(col1, 8, clean_text("Campo"), 1, 0, 'L', True)
            pdf.cell(col2, 8, clean_text("Resultado"), 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)

        start_y = pdf.get_y()
        pdf.set_x(col1 + 10)
        pdf.multi_cell(col2, 6, resultado, 1)
        end_y = pdf.get_y()
        altura_final = end_y - start_y
        
        pdf.set_y(start_y)
        pdf.multi_cell(col1, altura_final, campo, 1)
        pdf.set_y(end_y)
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, 'rb') as f:
            return f.read()
