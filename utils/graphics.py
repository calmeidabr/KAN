import os
import base64
import streamlit as st

@st.cache_data
def load_background_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def gerar_svg_triangulos_harmonicos(membros_triangulos, lider_nome=None, width=1280, height=720):
    """
    Gera uma string SVG contendo a visualização interativa dos triângulos harmônicos.
    
    membros_triangulos: dict no formato {nome_membro: [{"campo": "...", "valor": int_ou_str}, ...]}
    lider_nome: str correspondente ao nome do líder (para receber coroa e destaque)
    """
    path_fundo = os.path.join("images", "plano_kan_fundo.jpg")
    fundo_b64 = load_background_base64(path_fundo)
    
    coords_map = {
        1: (794, 176), 2: (1037, 243), 3: (960, 380),
        4: (794, 585), 5: (486, 585), 6: (320, 380),
        7: (243, 243), 8: (486, 176), 9: (640, 120),
        11: (1037, 243), 22: (794, 585)
    }
    
    cores = [
        "rgba(255, 200, 100, 0.5)", "rgba(100, 200, 255, 0.5)",
        "rgba(200, 255, 100, 0.5)", "rgba(255, 100, 200, 0.5)",
        "rgba(100, 255, 200, 0.5)", "rgba(255, 160, 100, 0.5)",
        "rgba(160, 100, 255, 0.5)", "rgba(100, 160, 255, 0.5)"
    ]
    
    cores_borda = [
        "rgba(255, 200, 100, 0.95)", "rgba(100, 200, 255, 0.95)",
        "rgba(200, 255, 100, 0.95)", "rgba(255, 100, 200, 0.95)",
        "rgba(100, 255, 200, 0.95)", "rgba(255, 160, 100, 0.95)",
        "rgba(160, 100, 255, 0.95)", "rgba(100, 160, 255, 0.95)"
    ]
    
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" class="kan-triangles-svg" style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); background-color: #1e1d24;">')
    
    # Adicionar CSS e Filtros no <defs>
    svg_parts.append("""
      <defs>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="6" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <style>
          svg.kan-triangles-svg .talento-group {
              transition: transform 0.25s ease, filter 0.25s ease;
              cursor: pointer;
          }
          svg.kan-triangles-svg .talento-group polygon {
              transition: fill-opacity 0.25s ease, stroke-width 0.25s ease, stroke 0.25s ease;
          }
          svg.kan-triangles-svg .talento-group text {
              transition: font-size 0.25s ease, fill 0.25s ease;
          }
          /* Efeito de hover no grupo do talento */
          svg.kan-triangles-svg .talento-group:hover {
              filter: url(#glow) brightness(1.25);
          }
          svg.kan-triangles-svg .talento-group:hover polygon {
              fill-opacity: 0.75;
              stroke-width: 4px;
              stroke: #FFFFFF !important;
          }
          svg.kan-triangles-svg .talento-group:hover text {
              font-size: 42px;
              fill: #FFFFFF !important;
          }
        </style>
      </defs>
    """)
    
    # Imagem de fundo
    if fundo_b64:
        svg_parts.append(f'  <image href="data:image/jpeg;base64,{fundo_b64}" x="0" y="0" width="{width}" height="{height}" />')
    else:
        svg_parts.append(f'  <rect x="0" y="0" width="{width}" height="{height}" fill="#1B1D24" />')
        
    # Ordenar membros de forma que o líder seja desenhado por último (por cima)
    itens_tri = list(membros_triangulos.items())
    itens_tri_ordenados = sorted(
        itens_tri,
        key=lambda item: 1 if item[0] == lider_nome else 0
    )
    
    for i, (m_nome, verts) in enumerate(itens_tri_ordenados):
        poly_points = []
        for v in verts:
            val_num = v.get("valor") if isinstance(v, dict) else v
            if val_num is None:
                continue
            val_num = int(val_num)
            if val_num in coords_map:
                poly_points.append(coords_map[val_num])
            else:
                val_reduz = sum(int(d) for d in str(val_num))
                if val_reduz in coords_map:
                    poly_points.append(coords_map[val_reduz])
                    
        if len(poly_points) == 3:
            color_idx = i % len(cores)
            fill_color = cores[color_idx]
            border_color = cores_borda[color_idx]
            border_width = "2"
            
            # Se for o líder, destaca a borda original
            is_lider = (m_nome == lider_nome)
            if is_lider:
                border_color = "#FFFFFF"
                border_width = "4.5"
                
            pts_str = " ".join(f"{p[0]},{p[1]}" for p in poly_points)
            
            # Baricentro do triângulo
            cx = sum(p[0] for p in poly_points) // 3
            cy = sum(p[1] for p in poly_points) // 3
            
            primeiro_nome = str(m_nome).split()[0]
            nome_display = f"👑 {primeiro_nome}" if is_lider else primeiro_nome
            
            # Grupo SVG para o membro
            svg_parts.append(f'  <g class="talento-group" data-nome="{m_nome}">')
            svg_parts.append(f'    <polygon points="{pts_str}" fill="{fill_color}" stroke="{border_color}" stroke-width="{border_width}" fill-opacity="1" />')
            
            # Esfera preta no vértice do KAN (poly_points[0])
            k_vertex = poly_points[0]
            svg_parts.append(f'    <circle cx="{k_vertex[0]}" cy="{k_vertex[1]}" r="6" fill="#000000" />')
            
            # Texto com contorno (stroke) para máxima legibilidade
            svg_parts.append(f'    <text x="{cx}" y="{cy}" font-family="Arial" font-size="34" fill="#EFEFEF" font-weight="bold" text-anchor="middle" dominant-baseline="central" stroke="#101010" stroke-width="2" paint-order="stroke fill">{nome_display}</text>')
            svg_parts.append('  </g>')
            
    svg_parts.append('</svg>')
    svg_str = "\n".join(svg_parts)
    # Minifica a string SVG removendo indentações e quebras de linha
    # para evitar que o markdown parser do Streamlit interprete como bloco de código.
    return "".join(line.strip() for line in svg_str.split("\n") if line.strip())

