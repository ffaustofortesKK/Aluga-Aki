import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuração da página e tema visual
st.set_page_config(
    page_title="AKITEM — Procure o que precisa, em pouco tempo",
    page_icon="🤝",
    layout="wide"
)

# Estilo CSS personalizado
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

# Dicionário rigoroso de Categorias e Especialidades exigidas
ESPECIALIDADES_POR_CATEGORIA = {
    "Moda": ["Sapato", "Bijuteria", "Roupa", "Peruca"],
    "Música": ["Aparelhagem de Som", "Dj", "Luzes", "Karaoke"],
    "Empregada Doméstica": ["Engomadeira", "Lavadeira", "Arrumadeira", "Baba interna"],
    "Carro": ["Aluguer de carro", "motorista ou Taxista Privado"],
    "Aluguer de Casa": ["T1", "T2", "T3"]
}

SUBCATEGORIAS_ALUGUER = ["Tudo"] + list(ESPECIALIDADES_POR_CATEGORIA.keys())

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
            if isinstance(f, dict):
                fotos_serializaveis.append(f)
            else:
                fotos_serializaveis.append({
                    "nome_ficheiro": getattr(f, "name", "foto_carregada.jpg")
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

if "termo_pesquisa" not in st.session_state:
    st.session_state["termo_pesquisa"] = ""

def main():
    # --- CABEÇALHO SUPERIOR ---
    col_logo, col_search, col_user = st.columns([2.5, 6, 2])
    
    with col_logo:
        st.image("https://cdn.phototourl.com/member/2026-09-30-c5a53c21-f2c4-49d9-b4f4-9c0bb984b1fd.jpg", width=180)
        
    with col_search:
        st.session_state["termo_pesquisa"] = st.text_input("Pesquisa Geral", placeholder="Pesquisar artigos ou prestadores...", value=st.session_state["termo_pesquisa"], label_visibility="collapsed")
        
    with col_user:
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

    st.markdown("<hr style='margin: 15px 0px 20px 0px; border: 0.5px solid #EAEAEA;'>", unsafe_allow_html=True)

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
    st.markdown('<div class="hero-title">Procure o que precisa, <span class="hero-highlight">em pouco tempo.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Carros, som, tendas, trajes, equipamentos e muito mais, de particulares e empresas verificadas.</div>', unsafe_allow_html=True)

    # --- BARRA DE SUBCATEGORIAS ---
    sub_cols = st.columns(len(SUBCATEGORIAS_ALUGUER))
    for idx, sub in enumerate(SUBCATEGORIAS_ALUGUER):
        with sub_cols[idx]:
            if st.button(sub, key=f"subcat_btn_{idx}", use_container_width=True):
                st.session_state["filtro_subcat"] = sub
                st.rerun()

    st.markdown(f"<small>A filtrar por categoria: <b>{st.session_state['filtro_subcat']}</b></small>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 15px 0px 20px 0px; border: 0.5px solid #EAEAEA;'>", unsafe_allow_html=True)

    st.markdown("### Disponíveis para alugar / prestação")
    
    prestadores_aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]

    filtro = st.session_state["filtro_subcat"]
    if filtro != "Tudo":
        prestadores_aprovados = [p for p in prestadores_aprovados if p["categoria"].lower() == filtro.lower() or p.get("especialidade", "").lower() == filtro.lower()]

    termo = st.session_state["termo_pesquisa"].strip().lower()
    if termo:
        prestadores_aprovados = [p for p in prestadores_aprovados if termo in p["nome_empresa"].lower() or termo in p["categoria"].lower() or termo in p.get("especialidade", "").lower()]

    if not prestadores_aprovados:
        st.info("Nenhum prestador ou artigo encontrado com os critérios selecionados.")

    cols = st.columns(4)
    for idx, p in enumerate(prestadores_aprovados):
        col_atual = cols[idx % 4]
        with col_atual:
            st.markdown(f"""
                <div class="product-card">
                    <div style="position: relative; background-color: #f8f9fa; height: 160px; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 35px;">📦</span>
                        <span class="badge-caucao">Verificado</span>
                        <span class="badge-empresa">{p.get('especialidade', p['categoria'])}</span>
                    </div>
                    <div class="product-title">{p['nome_empresa']}</div>
                    <div class="product-loc">Contacto: {p['telefone']}</div>
                    <div style="font-size: 11px; color: #555; margin: 0 12px 6px 12px;">📍 {p['localizacao']}</div>
                    <div class="product-price">Sob Consulta</div>
                </div>
            """, unsafe_allow_html=True)

def mostrar_registo():
    st.header("📝 Registo de Novo Prestador / Empresa")
    st.write("Preencha os campos abaixo. As especialidades atualizam-se de forma estrita conforme a categoria escolhida.")

    # Usamos st.selectbox fora do form para atualizar dinamicamente a especialidade sem conflito de cache
    categoria = st.selectbox("Categoria Principal*", list(ESPECIALIDADES_POR_CATEGORIA.keys()))
    
    # Lista estrita correspondente à categoria selecionada
    opcoes_especialidade = ESPECIALIDADES_POR_CATEGORIA.get(categoria, ["Geral"])

    with st.form("form_registo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome e Sobrenome/Empresa*")
            telefone = st.text_input("Número de Telefone*")
            
        with col2:
            password = st.text_input("Palavra-passe (Password)*", type="password")
            confirmar_password = st.text_input("Confirmar Palavra-passe*", type="password")
            
        # Especialidade restrita estritamente à categoria escolhida acima
        especialidade = st.selectbox("Especialidade da Categoria*", opcoes_especialidade)

        st.markdown("---")
        st.markdown("### 📍 Localização")
        localizacao = st.text_input("Localização (Bairro, Município, Rua)*")

        st.markdown("---")
        st.markdown("### 📞 Contacto Alternativo")
        col_alt1, col_alt2 = st.columns(2)
        with col_alt1:
            contacto_alternativo = st.text_input("Contacto alternativo (Número)*")
        with col_alt2:
            nome_contacto_alt = st.text_input("Nome e Sobrenome/Empresa do Contacto alternativo*")

        st.markdown("---")
        sobre_empresa = st.text_area("Descrição dos seus produtos ou serviços*", height=100)

        submitted = st.form_submit_button("Submeter Registo para Aprovação")

        if submitted:
            if not nome_empresa or not telefone or not localizacao or not contacto_alternativo or not nome_contacto_alt or not password:
                st.error("Preencha todos os campos obrigatórios (*).")
            elif password != confirmar_password:
                st.error("As palavras-passe não coincidem.")
            else:
                novo_prestador = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "nome_empresa": nome_empresa,
                    "telefone": telefone,
                    "categoria": categoria,
                    "especialidade": especialidade,
                    "password": password,
                    "localizacao": localizacao,
                    "contacto_alternativo": contacto_alternativo,
                    "nome_contacto_alt": nome_contacto_alt,
                    "sobre_empresa": sobre_empresa,
                    "fotos": [],
                    "status": "Pendente"
                }
                st.session_state["prestadores"].append(novo_prestador)
                guardar_dados(st.session_state["prestadores"])
                st.success("Registo submetido com sucesso! Aguarda validação do Administrador.")

def mostrar_login_prestador():
    st.header("🔐 Área Restrita do Prestador")
    st.write("Aceda para gerir os seus dados, serviços e carregar/apagar livremente as suas fotos (limite de 20).")

    with st.form("form_login"):
        nome_pesquisa = st.text_input("Nome e Sobrenome/Empresa")
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
            st.subheader(f"Gestão de Perfil e Fotos: {p_atual['nome_empresa']}")
            
            with st.form("form_update_prestador"):
                novo_tel = st.text_input("Atualizar Telefone", value=p_atual['telefone'])
                nova_loc = st.text_input("Atualizar Localização", value=p_atual['localizacao'])
                novo_sobre = st.text_area("Atualizar Descrição", value=p_atual.get('sobre_empresa', ''))
                
                if st.form_submit_button("Guardar Alterações Básicas"):
                    p_atual['telefone'] = novo_tel
                    p_atual['localizacao'] = nova_loc
                    p_atual['sobre_empresa'] = novo_sobre
                    guardar_dados(st.session_state["prestadores"])
                    st.success("Alterações guardadas com sucesso!")

            st.markdown("---")
            st.markdown("### 🖼️ Gestão de Fotografias (Até 20 fotos)")
            st.write(f"Fotos atuais carregadas: **{len(p_atual.get('fotos', []))} / 20**")

            novas_fotos = st.file_uploader("Carregar novas fotografias", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="uploader_fotos")
            
            if st.button("Adicionar Fotos Selecionadas"):
                fotos_atuais = p_atual.get("fotos", [])
                if len(fotos_atuais) + len(novas_fotos) > 20:
                    st.error("Limite excedido! O máximo permitido é de 20 fotografias.")
                else:
                    for f in novas_fotos:
                        fotos_atuais.append({"nome_ficheiro": f.name})
                    p_atual["fotos"] = fotos_atuais
                    guardar_dados(st.session_state["prestadores"])
                    st.success("Fotos carregadas com sucesso!")
                    st.rerun()

            if p_atual.get("fotos"):
                st.markdown("#### Fotografias Guardadas (Pode remover indesejadas):")
                for idx_f, foto in enumerate(p_atual["fotos"]):
                    col_f1, col_f2 = st.columns([4, 1])
                    with col_f1:
                        st.write(f"📸 {foto.get('nome_ficheiro', f'Foto {idx_f+1}')}")
                    with col_f2:
                        if st.button("Apagar", key=f"del_foto_{idx_f}"):
                            p_atual["fotos"].pop(idx_f)
                            guardar_dados(st.session_state["prestadores"])
                            st.success("Foto removida!")
                            st.rerun()

def mostrar_painel_admin():
    st.header("⚙️ Painel de Administração")
    st.write("Insira as credenciais de Administrador para gerir a plataforma.")

    with st.form("form_admin_login"):
        user_input = st.text_input("Utilizador Admin")
        pass_input = st.text_input("Palavra-passe Admin", type="password")
        login_admin = st.form_submit_button("Entrar como Administrador")

        if login_admin:
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
                    st.write(f"**Nome/Empresa:** {p['nome_empresa']}")
                    st.write(f"**Categoria:** {p['categoria']} ({p.get('especialidade', 'Geral')}) | **Estado:** `{p['status']}`")
                    st.write(f"**Local:** {p['localizacao']} | **Tel:** {p['telefone']}")
                    st.write(f"**Contacto Alternativo:** {p.get('nome_contacto_alt', 'N/A')} ({p.get('contacto_alternativo', 'N/A')})")
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
                        st.success("Prestador removido!")
                        st.rerun()
                st.markdown("---")

if __name__ == "__main__":
    main()
