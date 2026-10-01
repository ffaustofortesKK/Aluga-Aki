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

# Estilo CSS personalizado para o marketplace
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

# Subcategorias atualizadas conforme pedido
SUBCATEGORIAS_ALUGUER = [
    "Tudo",
    "Moda",             # Sapato, Bijuteria, Roupa, Peruca
    "Música",           # Aparelhagem de Som, DJ, Luzes, Karaoke
    "Empregada Doméstica", # Engomadeira, Lavadeira, Arrumadeira, Baba interna
    "Carro",            # Aluguer de carro, motorista ou Taxista Privado
    "Materiais de construção", 
    "Materiais de Decoração", 
    "Limpeza de Obra"
]

# Mapeamento detalhado para os filtros/seleções secundárias se necessário
OPCOES_DETALHADAS = {
    "Moda": ["Sapato", "Bijuteria", "Roupa", "Peruca"],
    "Música": ["Aparelhagem de Som", "DJ", "Luzes", "Karaoke"],
    "Empregada Doméstica": ["Engomadeira", "Lavadeira", "Arrumadeira", "Baba interna"],
    "Carro": ["Aluguer de carro", "Motorista ou Taxista Privado"]
}

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
        # Garantir que as fotos são guardadas de forma segura (nomes/legendas)
        fotos_serializaveis = []
        for f in p_copia.get("fotos", []):
            if isinstance(f, dict):
                fotos_serializaveis.append(f)
            else:
                fotos_serializaveis.append({"url": str(f), "descricao": "Foto de produto"})
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
        st.text_input("Pesquisa Geral", placeholder="Pesquisar produtos, lojas ou serviços...", label_visibility="collapsed")
        
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

    # --- BARRA DE NAVEGAÇÃO TOPO ---
    cols_nav = st.columns(9)
    for idx, cat in enumerate(CATEGORIAS_PRINCIPAIS):
        with cols_nav[idx]:
            if st.button(cat, key=f"nav_top_{idx}", use_container_width=True):
                if cat in ["Início", "Alugar"]:
                    st.session_state["pagina_atual"] = "🏠 Página Inicial"
                    st.session_state["filtro_subcat"] = "Tudo"
                    st.rerun()

    st.markdown("<hr style='margin: 10px 0px 20px 0px; border: 0.5px solid #EAEAEA;'>", unsafe_allow_html=True)

    # --- ROTEAMENTO ---
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
    st.markdown('<div class="hero-subtitle">Moda, som, carros, serviços domésticos e muito mais, de particulares e empresas verificadas.</div>', unsafe_allow_html=True)

    # --- BARRA DE PESQUISA ---
    with st.container():
        sc1, sc2 = st.columns([9, 1])
        with sc1:
            st.session_state["termo_pesquisa"] = st.text_input("O quê", placeholder="Pesquisar artigos...", value=st.session_state["termo_pesquisa"], label_visibility="collapsed")
        with sc2:
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

    st.markdown("### Disponíveis para alugar / Serviços")
    
    prestadores_aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]

    filtro = st.session_state["filtro_subcat"]
    if filtro != "Tudo":
        prestadores_aprovados = [p for p in prestadores_aprovados if p.get("categoria") == filtro or p.get("especialidade") == filtro]

    termo = st.session_state["termo_pesquisa"].strip().lower()
    if termo:
        prestadores_aprovados = [p for p in prestadores_aprovados if termo in p["nome_empresa"].lower() or termo in p["categoria"].lower()]

    if not prestadores_aprovados:
        st.info("Nenhum prestador ou artigo encontrado com os critérios selecionados.")

    cols = st.columns(4)
    for idx, p in enumerate(prestadores_aprovados):
        col_atual = cols[idx % 4]
        foto_capra = "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=500"
        if p.get("fotos") and len(p["fotos"]) > 0:
            primeira = p["fotos"][0]
            if isinstance(primeira, dict) and "url" in primeira:
                foto_capra = primeira["url"]

        with col_atual:
            st.markdown(f"""
                <div class="product-card">
                    <div style="position: relative;">
                        <img src="{foto_capra}" style="width: 100%; height: 160px; object-fit: cover;">
                        <span class="badge-caucao">Verificado</span>
                        <span class="badge-empresa">Empresa</span>
                    </div>
                    <div class="product-title">{p['nome_empresa']}</div>
                    <div class="product-loc">Categoria: {p.get('categoria')} ({p.get('especialidade', '')})</div>
                    <div style="font-size: 11px; color: #555; margin: 0 12px 6px 12px;">📍 {p['localizacao']}</div>
                    <div class="product-price">Sob Consulta</div>
                </div>
            """, unsafe_allow_html=True)

def mostrar_registo():
    st.header("📝 Registo de Novo Prestador / Empresa")
    st.write("Preencha os dados abaixo com as informações exigidas para submeter o seu negócio.")

    with st.form("form_registo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome e Sobrenome / Empresa*")
            telefone = st.text_input("Número de Telefone*")
            categoria = st.selectbox("Categoria Principal*", [c for c in SUBCATEGORIAS_ALUGUER if c != "Tudo"])
            
            # Sub-opções dinâmicas com base na categoria escolhida
            especialidade = ""
            if categoria in OPCOES_DETALHADAS:
                especialidade = st.selectbox("Específica / Especialidade*", OPCOES_DETALHADAS[categoria])

        with col2:
            contacto_alternativo = st.text_input("Contacto alternativo*")
            nome_contacto_alt = st.text_input("Nome e Sobrenome / Empresa do Contacto alternativo*")
            password = st.text_input("Palavra-passe (Password)*", type="password")
            confirmar_password = st.text_input("Confirmar Palavra-passe*", type="password")

        st.markdown("---")
        localizacao = st.text_input("Localização (Ex: Luanda, Talatona, Rua X)*")
        sobre_empresa = st.text_area("Fale sobre os seus produtos e serviços:*", height=100)

        submitted = st.form_submit_button("Submeter Registo para Aprovação")

        if submitted:
            if not nome_empresa or not telefone or not localizacao or not password or not contacto_alternativo or not nome_contacto_alt:
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
                    "contacto_alternativo": contacto_alternativo,
                    "nome_contacto_alt": nome_contacto_alt,
                    "password": password,
                    "sobre_empresa": sobre_empresa,
                    "localizacao": localizacao,
                    "fotos": [],
                    "status": "Pendente"
                }
                st.session_state["prestadores"].append(novo_prestador)
                guardar_dados(st.session_state["prestadores"])
                st.success("Registo submetido com sucesso! Aguarda validação do Administrador.")

def mostrar_login_prestador():
    st.header("🔐 Área Restrita do Prestador")
    st.write("Aceda para gerir os seus dados, serviços e carregar até 20 fotografias dos seus produtos.")

    with st.form("form_login"):
        nome_pesquisa = st.text_input("Nome e Sobrenome / Empresa")
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
            st.subheader(f"Painel de Controlo: {p_atual['nome_empresa']}")
            
            # Gestão de Fotos (Até 20 fotos com opção de apagar/carregar)
            st.markdown("### 🖼️ Gestão de Fotografias (Máximo 20)")
            fotos_atuais = p_atual.get("fotos", [])
            st.write(Temas de Fotos Atuais: `{len(fotos_atuais)}/20`)

            # Mostrar fotos atuais com botão para apagar
            if fotos_atuais:
                cols_f = st.columns(4)
                for idx, f_item in enumerate(fotos_atuais):
                    with cols_f[idx % 4]:
                        url_foto = f_item.get("url", "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=500")
                        st.image(url_foto, width=120)
                        if st.button(f"🗑️ Apagar Foto {idx+1}", key=f"del_foto_{p_id}_{idx}"):
                            p_atual["fotos"].pop(idx)
                            guardar_dados(st.session_state["prestadores"])
                            st.success("Fotografia removida com sucesso!")
                            st.rerun()

            # Adicionar novas fotos por URL ou link de imagem
            if len(fotos_atuais) < 20:
                st.markdown("#### Adicionar Nova Fotografia")
                with st.form(f"form_add_foto_{p_id}"):
                    nova_url = st.text_input("Link / URL Direto da Imagem (Ex: Unsplash, Imgur, etc.)")
                    desc_foto = st.text_input("Descrição ou Nome do Artigo/Serviço")
                    add_btn = st.form_submit_button("Carregar Fotografia")
                    
                    if add_btn:
                        if nova_url:
                            p_atual["fotos"].append({"url": nova_url, "descricao": desc_foto})
                            guardar_dados(st.session_state["prestadores"])
                            st.success("Fotografia adicionada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Insira um link de imagem válido.")
            else:
                st.warning("Atingiu o limite máximo de 20 fotografias.")

            st.markdown("---")
            st.subheader("Editar Dados de Contacto e Localização")
            with st.form("form_update_dados"):
                novo_tel = st.text_input("Telefone", value=p_atual['telefone'])
                novo_alt = st.text_input("Contacto Alternativo", value=p_atual.get('contacto_alternativo', ''))
                nova_loc = st.text_input("Localização", value=p_atual['localizacao'])
                novo_sobre = st.text_area("Descrição", value=p_atual.get('sobre_empresa', ''))
                
                if st.form_submit_button("Guardar Alterações"):
                    p_atual['telefone'] = novo_tel
                    p_atual['contacto_alternativo'] = novo_alt
                    p_atual['localizacao'] = nova_loc
                    p_atual['sobre_empresa'] = novo_sobre
                    guardar_dados(st.session_state["prestadores"])
                    st.success("Dados atualizados com sucesso!")

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
                    st.write(f"**Categoria:** {p['categoria']} ({p.get('especialidade','')}) | **Estado:** `{p['status']}`")
                    st.write(f"**Tel:** {p['telefone']} | **Local:** {p['localizacao']}")
                    st.write(f"**Contacto Alt:** {p.get('contacto_alternativo')} ({p.get('nome_contacto_alt')})")
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
