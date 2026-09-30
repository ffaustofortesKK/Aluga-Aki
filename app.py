import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página e tema visual
st.set_page_config(
    page_title="Plataforma de Aluguer e Serviços — FFK",
    page_icon="🎤",
    layout="wide"
)

# Aplicar estilo CSS personalizado (Tema Escuro com Dourado semelhante à imagem de referência)
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    h1, h2, h3 {
        color: #FFC107 !important;
        font-family: monospace;
    }
    .stButton>button {
        background-color: #FFC107;
        color: #121212;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #FFA000;
        color: #000000;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1E1E1E;
        color: #FFFFFF;
        border: 1px solid #333333;
    }
    </style>
""", unsafe_allow_html=True)

# Categorias solicitadas
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

# Simulação de Base de Dados na Sessão
if "prestadores" not in st.session_state:
    st.session_state["prestadores"] = []

def main():
    st.title("🌟 Plataforma de Aluguer e Serviços FFK")
    st.write("Bem-vindo à central de gestão de produtos, equipamentos e serviços.")

    # Menu Único em Tabs (Abas Horizontais) no topo
    tab_home, tab_registo, tab_login, tab_admin = st.tabs([
        "🏠 Página Inicial", 
        "📝 Registar Empresa", 
        "🔐 Login Prestador", 
        "⚙️ Administração"
    ])

    with tab_home:
        mostrar_home()

    with tab_registo:
        mostrar_registo()

    with tab_login:
        mostrar_login_prestador()

    with tab_admin:
        mostrar_painel_admin()

def mostrar_home():
    st.header("Empresas e Serviços Disponíveis")
    st.write("Explore as opções aprovadas na nossa plataforma.")
    
    aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]
    
    if not aprovados:
        st.info("Ainda não existem empresas aprovadas na plataforma.")
    else:
        for p in aprovados:
            with st.expander(f"🏢 {p['nome_empresa']} — [{p['categoria']}]"):
                st.write(f"📞 **Telefone:** {p['telefone']}")
                st.write(f"📍 **Localização:** Rua {p['localizacao']['rua']}, Bairro {p['localizacao']['bairro']}, {p['localizacao']['municipio']}")
                st.markdown("**Portefólio / Fotos:**")
                if p['fotos']:
                    cols = st.columns(min(len(p['fotos']), 3))
                    for idx, foto_info in enumerate(p['fotos']):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            st.image(foto_info['imagem'], use_container_width=True)
                            st.caption(f"📝 {foto_info['descricao']}")

def mostrar_registo():
    st.header("📝 Registo de Novo Prestador / Empresa")
    st.write("Preencha os dados abaixo. O registo ficará pendente de aprovação pela administração.")

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
        st.markdown("### 📍 Localização")
        col_loc1, col_loc2, col_loc3 = st.columns(3)
        with col_loc1:
            bairro = st.text_input("Bairro*")
        with col_loc2:
            municipio = st.text_input("Município*")
        with col_loc3:
            rua = st.text_input("Rua*")

        st.markdown("---")
        st.markdown("### 📸 Upload de Fotos (Até 6 fotos com descrição)")
        
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

        submitted = st.form_submit_button("Submeter Registo")

        if submitted:
            if not nome_empresa or not telefone or not bairro or not municipio or not rua or not password:
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            elif password != confirmar_password:
                st.error("As palavras-passe não coincidem.")
            else:
                novo_prestador = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "nome_empresa": nome_empresa,
                    "telefone": telefone,
                    "categoria": categoria,
                    "password": password,
                    "localizacao": {"bairro": bairro, "municipio": municipio, "rua": rua},
                    "fotos": fotos_dados,
                    "status": "Pendente"
                }
                st.session_state["prestadores"].append(novo_prestador)
                st.success("Registo submetido com sucesso! O administrador irá validar a sua empresa em breve.")

def mostrar_login_prestador():
    st.header("🔐 Área Restrita do Prestador")
    st.write("Insira os seus dados para aceder e atualizar o seu cadastro.")

    with st.form("form_login"):
        nome_pesquisa = st.text_input("Nome da Empresa")
        pass_input = st.text_input("Palavra-passe", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            prestador = next((p for p in st.session_state["prestadores"] if p["nome_empresa"].lower() == nome_pesquisa.lower() and p["password"] == pass_input), None)
            if prestador:
                st.session_state["prestador_logado"] = prestador['id']
                st.success(f"Autenticação bem-sucedida para: {prestador['nome_empresa']}")
            else:
                st.error("Empresa não encontrada ou palavra-passe incorreta.")

    if "prestador_logado" in st.session_state:
        p_id = st.session_state["prestador_logado"]
        p_atual = next((p for p in st.session_state["prestadores"] if p["id"] == p_id), None)
        
        if p_atual:
            st.markdown("---")
            st.subheader(f"Gerir Perfil: {p_atual['nome_empresa']}")
            with st.form("form_update"):
                novo_tel = st.text_input("Atualizar Telefone", value=p_atual['telefone'])
                nova_rua = st.text_input("Atualizar Rua", value=p_atual['localizacao']['rua'])
                
                if st.form_submit_button("Guardar Alterações"):
                    p_atual['telefone'] = novo_tel
                    p_atual['localizacao']['rua'] = nova_rua
                    st.success("Dados alterados com sucesso!")

def mostrar_painel_admin():
    st.header("⚙️ Painel de Administração")
    
    admin_pass = st.text_input("Palavra-passe de Administrador", type="password", key="adm_pass")
    
    # Palavra-passe de teste para o admin
    if admin_pass != "admin123":
        st.info("Insira a palavra-passe de administração para ver e gerir as empresas (Utilize `admin123` para teste).")
        return

    st.success("Administrador autenticado com sucesso.")
    st.markdown("### 📋 Lista de Empresas Registadas")

    prestadores = st.session_state["prestadores"]
    
    if not prestadores:
        st.warning("Ainda não existem registos pendentes ou aprovados.")
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
                        st.rerun()
                else:
                    if st.button(f"Suspender", key=f"susp_{i}"):
                        p['status'] = "Pendente"
                        st.rerun()
            with col3:
                if st.button(f"🗑️ Excluir", key=f"del_{i}"):
                    st.session_state["prestadores"].pop(i)
                    st.rerun()
            st.markdown("---")

if __name__ == "__main__":
    main()
