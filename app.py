import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuração da página e tema visual (Layout limpo estilo marketplace)
st.set_page_config(
    page_title="AKITEM — Alugue o que precisa, quando precisa",
    page_icon="🤝",
    layout="wide"
)

# Estilo CSS personalizado para imitar fielmente o design profissional
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #1A1A1A;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #111111;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .hero-highlight {
        color: #FF5722;
    }
    .hero-subtitle {
        font-size: 15px;
        color: #666666;
        text-align: center;
        margin-bottom: 30px;
    }
    .product-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 0px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        border: 1px solid #EAEAEA;
        overflow: hidden;
        position: relative;
    }
    .product-title {
        font-size: 14px;
        font-weight: 600;
        color: #2C3E50;
        margin: 10px 12px 2px 12px;
    }
    .product-loc {
        font-size: 12px;
        color: #777777;
        margin: 0 12px 10px 12px;
    }
    .product-price {
        font-size: 15px;
        font-weight: bold;
        color: #111111;
        margin: 0 12px 14px 12px;
    }
    .badge-caucao {
        position: absolute;
        top: 10px;
        left: 10px;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        color: #333333;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .badge-empresa {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: rgba(0, 0, 0, 0.75);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

CATEGORIAS_PRINCIPAIS = [
    "Início", 
    "Compras & E-Commerce", 
    "Alugar", 
    "Eventos", 
    "Comida & Restaurantes", 
    "Supermercados", 
    "Farmácia & Saúde", 
    "Alojamento & Reservas", 
    "Prestação de Serviços"
]

SUBCATEGORIAS_ALUGUER = [
    "Tudo",
    "Música", 
    "Roupa", 
    "Materiais de construção", 
    "Luzes Para Eventos", 
    "Materiais de Decoração", 
    "Carro", 
    "Empregada Doméstica", 
    "Limpeza de Obra"
]

DB_FILE = "dados_prestadores.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_dados(prestadores):
    dados_para_salvar = []
    for p in prestadores:
        p_copia = p.copy()
        fotos_serializaveis = []
        for f in p_copia.get("fotos", []):
            fotos_serializaveis.append({
                "descricao": f.get("descricao", ""),
                "nome_ficheiro": getattr(f.get("imagem"), "name", "foto_carregada.jpg") if f.get("imagem") else ""
            })
        p_copia["fotos"] = fotos_serializaveis
        dados_para_salvar.append(p_copia)
        
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

if "prestadores" not in st.session_state:
    st.session_state["prestadores"] = carregar_dados()

if "filtro_subcat" not in st.session_state:
    st.session_state["filtro_subcat"] = "Tudo"

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "🏠 Página Inicial"

def main():
    # --- CABEÇALHO SUPERIOR (Logótipo, Pesquisa e Botão de Utilizador) ---
    col_logo, col_search, col_user = st.columns([2.5, 6, 2])
    
    with col_logo:
        st.image("https://cdn.phototourl.com/member/2026-09-30-c5a53c21-f2c4-49d9-b4f4-9c0bb984b1fd.jpg", width=180)
        
    with col_search:
        termo_geral = st.text_input("Pesquisa Geral", placeholder="Pesquisar produtos, lojas ou serviços...", label_visibility="collapsed")
        
    with col_user:
        # Menu de Ação através do "Boneco" (Selectbox limpo no canto superior direito)
        acao_utilizador = st.selectbox(
            "Utilizador", 
            ["👤 Entrar / Conta", "📝 Registar Nova Empresa", "🔐 Login Prestador", "⚙️ Administração (Adminff24)"],
            label_visibility="collapsed"
        )
        
        if "Registar" in acao_utilizador:
            st.session_state["pagina_atual"] = "📝 Registar Empresa"
        elif "Prestador" in acao_utilizador:
            st.session_state["pagina_atual"] = "🔐 Login Prestador"
        elif "Administração" in acao_utilizador:
            st.session_state["pagina_atual"] = "⚙️ Administração"
        elif "Entrar" in acao_utilizador and st.session_state["pagina_atual"] not in ["🏠 Página Inicial"]:
            st.session_state["pagina_atual"] = "🏠 Página Inicial"

    # --- BARRA DE NAVEGAÇÃO DE CATEGORIAS TOPO ---
    cols_nav = st.columns(9)
    for idx, cat in enumerate(CATEGORIAS_PRINCIPAIS):
        with cols_nav[idx]:
            if st.button(cat, key=f"nav_top_{idx}", use_container_width=True):
                if cat in ["Início", "Alugar"]:
                    st.session_state["pagina_atual"] = "🏠 Página Inicial"
                    st.session_state["filtro_subcat"] = "Tudo"
                    st.rerun()

    st.markdown("<hr style='margin: 10px 0px 20px 0px; border: 0.5px solid #EAEAEA;'>", unsafe_allow_html=True)

    # --- ROTEAMENTO DAS PÁGINAS ---
    if st.session_state["pagina_atual"] == "🏠 Página Inicial":
        mostrar_pagina_inicial()
    elif st.session_state["pagina_atual"] == "📝 Registar Empresa":
        mostrar_registo()
    elif st.session_state["pagina_atual"] == "🔐 Login Prestador":
        mostrar_login_prestador()
    elif st.session_state["pagina_atual"] == "⚙️ Administração":
        mostrar_painel_admin()

def mostrar_pagina_inicial():
    st.markdown('<div class="hero-title">Alugue o que precisa, <span class="hero-highlight">quando precisa.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Carros, som, tendas, trajes, equipamentos e muito mais, de particulares e empresas verificadas.</div>', unsafe_allow_html=True)

    # --- BARRA DE PESQUISA AVANÇADA ---
    with st.container():
        sc1, sc2, sc3, sc4, sc5 = st.columns([2.5, 2, 1.8, 1.8, 0.6])
        with sc1:
            st.text_input("O quê", placeholder="Pesquisar artigos...", label_visibility="collapsed")
        with sc2:
            st.text_input("Onde", placeholder="Luanda, Talatona...", label_visibility="collapsed")
        with sc3:
            st.text_input("Levantamento", placeholder="dd/mm/aaaa", label_visibility="collapsed")
        with sc4:
            st.text_input("Devolução", placeholder="dd/mm/aaaa", label_visibility="collapsed")
        with sc5:
            st.button("🔍", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BARRA DE SUBCATEGORIAS ---
    sub_cols = st.columns(len(SUBCATEGORIAS_ALUGUER))
    for idx, sub in enumerate(SUBCATEGORIAS_ALUGUER):
        with sub_cols[idx]:
            if st.button(sub, key=f"subcat_btn_{idx}", use_container_width=True):
                st.session_state["filtro_subcat"] = sub
                st.rerun()

    st.markdown(f"<small>A filtrar por categoria: <b>{st.session_state['filtro_subcat']}</b></small>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 15px 0px 20px 0px; border: 0.5px solid #EAEAEA;'>", unsafe_allow_html=True)

    st.markdown("### Disponíveis para alugar")
    
    produtos_exemplo = [
        {
            "nome": "Cadeira de silicone",
            "locador": "Aluguer de Decoração",
            "preco": "750 Kz dia",
            "imagem": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=500",
            "categoria": "Materiais de Decoração"
        },
        {
            "nome": "Cadeiras de plástico",
            "locador": "Aluguer de Decoração",
            "preco": "500 Kz dia",
            "imagem": "https://images.unsplash.com/photo-1544457070-4cd773b4d71e?w=500",
            "categoria": "Materiais de Decoração"
        },
        {
            "nome": "Cadeiras de alugar",
            "locador": "Aluguer de Decoração",
            "preco": "750 Kz dia",
            "imagem": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500",
            "categoria": "Materiais de Decoração"
        }
    ]

    prestadores_aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]

    filtro = st.session_state["filtro_subcat"]
    if filtro != "Tudo":
        produtos_exemplo = [p for p in produtos_exemplo if p["categoria"].lower() == filtro.lower()]

    cols = st.columns(4)
    
    for idx, item in enumerate(produtos_exemplo):
        col_atual = cols[idx % 4]
        with col_atual:
            st.markdown(f"""
                <div class="product-card">
                    <div style="position: relative;">
                        <img src="{item['imagem']}" style="width: 100%; height: 160px; object-fit: cover;">
                        <span class="badge-caucao">Sem caução</span>
                        <span class="badge-empresa">Empresa</span>
                    </div>
                    <div class="product-title">{item['nome']}</div>
                    <div class="product-loc">Locador: {item['locador']}</div>
                    <div style="font-size: 11px; color: #555; margin: 0 12px 6px 12px;">Reserva sem caução</div>
                    <div class="product-price">{item['preco']}</div>
                </div>
            """, unsafe_allow_html=True)

    for idx, p in enumerate(prestadores_aprovados):
        col_atual = cols[(len(produtos_exemplo) + idx) % 4]
        with col_atual:
            st.markdown(f"""
                <div class="product-card">
                    <div style="position: relative; background-color: #f0f0f0; height: 160px; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 35px;">📦</span>
                        <span class="badge-caucao">Verificado</span>
                        <span class="badge-empresa">Empresa</span>
                    </div>
                    <div class="product-title">{p['nome_empresa']}</div>
                    <div class="product-loc">Categoria: {p['categoria']}</div>
                    <div style="font-size: 11px; color: #555; margin: 0 12px 6px 12px;">📍 {p['localizacao']['municipio']}</div>
                    <div class="product-price">Sob Consulta</div>
                </div>
            """, unsafe_allow_html=True)

def mostrar_registo():
    st.header("📝 Registo de Novo Prestador / Empresa")
    st.write("Preencha os dados abaixo para submeter o seu negócio à plataforma AKITEM.")

    with st.form("form_registo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome da Empresa*")
            telefone = st.text_input("Número de Telefone*")
            categoria = st.selectbox("Categoria Principal*", SUBCATEGORIAS_ALUGUER[1:])
        with col2:
            password = st.text_input("Palavra-passe (Password)*", type="password")
            confirmar_password = st.text_input("Confirmar Palavra-passe*", type="password")

        st.markdown("---")
        st.markdown("### 📖 Descrição da Empresa")
        sobre_empresa = st.text_area("Fale sobre os seus produtos e serviços de aluguer:*", height=100)

        st.markdown("---")
        st.markdown("### 📍 Localização Detalhada")
        col_loc1, col_loc2, col_loc3 = st.columns(3)
        with col_loc1:
            bairro = st.text_input("Bairro*")
        with col_loc2:
            municipio = st.text_input("Município*")
        with col_loc3:
            rua = st.text_input("Rua*")

        submitted = st.form_submit_button("Submeter Registo para Aprovação")

        if submitted:
            if not nome_empresa or not telefone or not bairro or not municipio or not rua or not password or not sobre_empresa:
                st.error("Preencha todos os campos obrigatórios (*).")
            elif password != confirmar_password:
                st.error("As palavras-passe não coincidem.")
            else:
                novo_prestador = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "nome_empresa": nome_empresa,
                    "telefone": telefone,
                    "categoria": categoria,
                    "password": password,
                    "sobre_empresa": sobre_empresa,
                    "localizacao": {"bairro": bairro, "municipio": municipio, "rua": rua},
                    "fotos": [],
                    "status": "Pendente"
                }
                st.session_state["prestadores"].append(novo_prestador)
                guardar_dados(st.session_state["prestadores"])
                st.success("Registo submetido com sucesso! Aguarda validação do Administrador.")

def mostrar_login_prestador():
    st.header("🔐 Área Restrita do Prestador")
    st.write("Aceda para gerir os seus dados e serviços na plataforma.")

    with st.form("form_login"):
        nome_pesquisa = st.text_input("Nome da Empresa")
        pass_input = st.text_input("Palavra-passe", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            prestador = next((p for p in st.session_state["prestadores"] if p["nome_empresa"].lower() == nome_pesquisa.lower() and p["password"] == pass_input), None)
            if prestador:
                st.session_state["prestador_logado"] = prestador['id']
                st.success(f"Sessão iniciada para: {prestador['nome_empresa']}")
            else:
                st.error("Dados incorretos ou empresa não encontrada.")

    if "prestador_logado" in st.session_state:
        p_id = st.session_state["prestador_logado"]
        p_atual = next((p for p in st.session_state["prestadores"] if p["id"] == p_id), None)
        
        if p_atual:
            st.markdown("---")
            st.subheader(f"Editar Perfil: {p_atual['nome_empresa']}")
            with st.form("form_update"):
                novo_tel = st.text_input("Atualizar Telefone", value=p_atual['telefone'])
                nova_rua = st.text_input("Atualizar Rua", value=p_atual['localizacao']['rua'])
                novo_sobre = st.text_area("Atualizar Descrição", value=p_atual.get('sobre_empresa', ''))
                
                if st.form_submit_button("Guardar Alterações"):
                    p_atual['telefone'] = novo_tel
                    p_atual['localizacao']['rua'] = nova_rua
                    p_atual['sobre_empresa'] = novo_sobre
                    guardar_dados(st.session_state["prestadores"])
                    st.success("Alterações guardadas com sucesso!")

def mostrar_painel_admin():
    st.header("⚙️ Painel de Administração")
    st.write("Insira as credenciais de Administrador para gerir a plataforma.")

    with st.form("form_admin_login"):
        user_input = st.text_input("Utilizador Admin")
        pass_input = st.text_input("Palavra-passe Admin", type="password")
        login_admin = st.form_submit_button("Entrar como Administrador")

        if login_admin:
            # Validação estricta com as tuas credenciais indicadas
            if user_input == "adminff24" and pass_input == "ffkaraoke2026":
                st.session_state["admin_autenticado"] = True
                st.success("Sessão de Administrador iniciada com sucesso!")
            else:
                st.error("Utilizador ou palavra-passe de Administrador incorretos.")

    if st.session_state.get("admin_autenticado", False):
        st.markdown("---")
        st.success("✅ Acesso administrativo autorizado (Adminff24).")
        st.markdown("### 📋 Gestão de Prestadores Registados")

        prestadores = st.session_state["prestadores"]
        if not prestadores:
            st.warning("Sem registos de prestadores na plataforma.")
            return

        for i, p in enumerate(prestadores):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**Empresa:** {p['nome_empresa']}")
                    st.write(f"**Categoria:** {p['categoria']} | **Estado:** `{p['status']}`")
                    st.write(f"**Local:** {p['localizacao']['municipio']} - {p['localizacao']['bairro']}")
                with col2:
                    if p['status'] == "Pendente":
                        if st.button(f"Aprovar", key=f"apr_{i}"):
                            p['status'] = "Aprovado"
                            guardar_dados(prestadores)
                            st.rerun()
                    else:
                        if st.button(f"Suspender", key=f"susp_{i}"):
                            p['status'] = "Pendente"
                            guardar_dados(prestadores)
                            st.rerun()
                with col3:
                    if st.button(f"🗑️ Excluir", key=f"del_{i}"):
                        st.session_state["prestadores"].pop(i)
                        guardar_dados(prestadores)
                        st.success("Empresa removida!")
                        st.rerun()
                st.markdown("---")

if __name__ == "__main__":
    main()
