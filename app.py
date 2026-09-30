import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuração da página e tema visual
st.set_page_config(
    page_title="AKITEM — Plataforma de Aluguer e Serviços",
    page_icon="🤝",
    layout="wide"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .stApp {
        background-color: #E3F2FD;
        color: #1A1A1A;
    }
    .product-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #EFEFEF;
    }
    .product-title {
        font-size: 15px;
        font-weight: 600;
        color: #2C3E50;
        margin-top: 10px;
    }
    .product-price {
        font-size: 16px;
        font-weight: bold;
        color: #111111;
        margin-top: 5px;
    }
    .store-tag {
        font-size: 11px;
        font-weight: bold;
        color: #FF5722;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

CATEGORIAS = [
    "Música", 
    "Roupa", 
    "Materiais de Construção", 
    "Luzes Para Eventos", 
    "Materiais de Decoração", 
    "Carro", 
    "Empregada Doméstica", 
    "Limpeza de Obra"
]

# Subcategorias detalhadas por secção (como na imagem de referência)
SUBCATEGORIAS = {
    "Alugar": ["Carros", "Motas & Scooters", "Carrinhas & Vans", "Camiões & Pesados", "Geradores & Energia", "Som Profissional", "Iluminação & Luz", "Tendas & Equipamentos"],
    "Eventos": ["Casamentos", "Aniversários", "Festas Corporativas", "Concertos", "Espaços & quintas"],
    "Comida & Restaurantes": ["Prato Feito", "Catering", "Churrasco", "Sobremesas & Bolos", "Bebidas"],
    "Supermercados": ["Mercearia", "Frutas & Legumes", "Talho", "Bebidas & Snacks", "Higiene & Limpeza"],
    "Farmácia & Saúde": ["Medicamentos", "Primeiros Socorros", "Vitaminas & Suplementos", "Cuidados Pessoais"],
    "Alojamento & Reservas": ["Hotéis", "Apartamentos Mobilados", "Resorts", "Casas de Campo"],
    "Prestação de Serviços": ["Limpeza de Obra", "Empregada Doméstica", "Electricista", "Canalizador", "Segurança"]
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

if "filtro_categoria" not in st.session_state:
    st.session_state["filtro_categoria"] = None

def main():
    # --- CABEÇALHO SUPERIOR ---
    col_logo, col_search, col_actions = st.columns([2, 5, 2])
    
    with col_logo:
        # Inserção do logótipo oficial AKITEM
        st.image("https://cdn.phototourl.com/member/2026-09-30-c5a53c21-f2c4-49d9-b4f4-9c0bb984b1fd.jpg", width=220)
        
    with col_search:
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        termo_pesquisa = st.text_input("Pesquisa", placeholder="Pesquisar produtos, lojas ou serviços...", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_actions:
        st.markdown("""
            <div style='display: flex; justify-content: flex-end; align-items: center; gap: 15px; margin-top: 15px; font-size: 14px; font-weight: 500;'>
                <span>❤️ <sup>0</sup></span>
                <span>🛒 <sup>0</sup></span>
                <span><b>Entrar 👤</b></span>
            </div>
        """, unsafe_allow_html=True)

    # --- BARRA DE NAVEGAÇÃO SUPERIOR COM CLIQUE FUNCIONAL ---
    nav_cols = st.columns(8)
    
    # Botão Início limpa os filtros e recarrega a página principal
    with nav_cols[0]:
        if st.button("🏠 Início"):
            st.session_state["filtro_categoria"] = None
            st.rerun()
            
    menus_principais = list(SUBCATEGORIAS.keys())
    for idx, menu in enumerate(menus_principais[:7]):
        with nav_cols[idx + 1]:
            if st.button(menu):
                st.session_state["filtro_categoria"] = menu
                st.rerun()

    st.markdown("---")

    # Menu de Gestão Principal
    col_bc, col_menu_sel = st.columns([3, 2])
    with col_bc:
        if st.session_state["filtro_categoria"]:
            st.markdown(f"<small><b>Início</b> › Categoria: <b>{st.session_state['filtro_categoria']}</b></small>", unsafe_allow_html=True)
        else:
            st.markdown("<small><b>Início</b> › Painel Principal</small>", unsafe_allow_html=True)
            
    with col_menu_sel:
        opcao_menu = st.selectbox(
            "Navegação Principal",
            ["🏠 Página Inicial", "📝 Registar Empresa", "🔐 Login Prestador", "⚙️ Administração"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    if opcao_menu == "🏠 Página Inicial":
        mostrar_home(termo_pesquisa)
    elif opcao_menu == "📝 Registar Empresa":
        mostrar_registo()
    elif opcao_menu == "🔐 Login Prestador":
        mostrar_login_prestador()
    elif opcao_menu == "⚙️ Administração":
        mostrar_painel_admin()

def mostrar_home(termo_busca=""):
    cat_selecionada = st.session_state.get("filtro_categoria")
    
    if cat_selecionada and cat_selecionada in SUBCATEGORIAS:
        st.markdown(f"## 📌 Opções em: {cat_selecionada}")
        st.write("Selecione abaixo um dos itens para filtrar os prestadores correspondentes:")
        
        subs = SUBCATEGORIAS[cat_selecionada]
        sub_cols = st.columns(min(len(subs), 4))
        for idx, sub in enumerate(subs):
            with sub_cols[idx % 4]:
                if st.button(f"🔍 {sub}", key=f"sub_{cat_selecionada}_{idx}"):
                    st.info(f"A filtrar por: **{sub}**")
        
        st.markdown("---")

    aba_selecionada = st.radio("", ["Produtos", "Serviços", "Parceiros"], horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]
    
    if termo_busca:
        aprovados = [p for p in aprovados if termo_busca.lower() in p['nome_empresa'].lower() or termo_busca.lower() in p['categoria'].lower()]

    if not aprovados:
        st.info("Nenhum prestador ou produto encontrado de momento.")
        return

    cols = st.columns(4)
    for idx, p in enumerate(aprovados):
        col_atual = cols[idx % 4]
        with col_atual:
            st.markdown(f"""
                <div class="product-card">
                    <div class="store-tag">{p['categoria']}</div>
                    <div class="product-title">{p['nome_empresa']}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 4px;">📍 {p['localizacao']['municipio']}</div>
                    <div class="product-price">Disponível para Aluguer</div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Ver Detalhes"):
                st.write(f"📞 **Telefone:** {p['telefone']}")
                st.write(f"📍 **Endereço:** Rua {p['localizacao']['rua']}, {p['localizacao']['bairro']}")
                st.markdown(f"**Sobre:** {p.get('sobre_empresa', 'Sem descrição.')}")

def mostrar_registo():
    st.header("📝 Registo de Novo Prestador / Empresa")
    st.write("Preencha os dados abaixo para submeter o seu negócio à plataforma.")

    with st.form("form_registo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome da Empresa*")
            telefone = st.text_input("Número de Telefone*")
            categoria = st.selectbox("Categoria Principal*", CATEGORIAS)
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

        st.markdown("---")
        st.markdown("### 📸 Portefólio (Carregar até 6 fotos)")
        
        fotos_dados = []
        for i in range(1, 7):
            st.markdown(f"**Foto {i}**")
            f_col1, f_col2 = st.columns([1, 2])
            with f_col1:
                img_file = st.file_uploader(f"Carregar imagem {i}", type=["jpg", "png", "jpeg"], key=f"img_{i}")
            with f_col2:
                desc = st.text_input(f"Descrição da foto {i}", key=f"desc_{i}")
            
            if img_file:
                fotos_dados.append({"imagem": img_file, "descricao": desc})

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
                    "fotos": fotos_dados,
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
    admin_pass = st.text_input("Palavra-passe de Administrador", type="password", key="adm_pass")
    
    if admin_pass != "admin123":
        st.info("Insira a palavra-passe de administração (Utilize `admin123` para teste).")
        return

    st.success("Acesso administrativo autorizado.")
    st.markdown("### 📋 Gestão de Prestadores Registados")

    prestadores = st.session_state["prestadores"]
    if not prestadores:
        st.warning("Sem registos na plataforma.")
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
