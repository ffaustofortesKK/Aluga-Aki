import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configuração da página e tema visual
st.set_page_config(
    page_title="Plataforma de Aluguer e Serviços",
    page_icon="🤝",
    layout="wide"
)

# Estilo CSS personalizado (Tema Escuro com Dourado)
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
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
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

# Ficheiro JSON para garantir persistência (os dados não se perdem)
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
    # Nota: Arquivos carregados via st.file_uploader guardam objetos binários/temporários. 
    # Para guardar em JSON puro de forma persistente, guardamos os metadados e descrições das imagens.
    dados_para_salvar = []
    for p in prestadores:
        p_copia = p.copy()
        # Converter objetos de ficheiro carregados para nomes/strings se necessário
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

def main():
    # Cabeçalho com Logótipo / Símbolo de Aluguer
    col_logo, col_menu = st.columns([3, 2])
    with col_logo:
        st.markdown("# 🤝 FFK — Plataforma de Aluguer & Serviços")
        st.write("Encontre e alugue produtos, equipamentos ou serviços com segurança.")
    
    with col_menu:
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        # Menu no canto superior direito simulado com selectbox interativo
        opcao_menu = st.selectbox(
            "📌 Menu de Navegação",
            ["🏠 Página Inicial", "📝 Registar Empresa", "🔐 Login Prestador", "⚙️ Administração"],
            key="menu_superior"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Direcionamento com base na escolha do menu superior direito
    if opcao_menu == "🏠 Página Inicial":
        mostrar_home()
    elif opcao_menu == "📝 Registar Empresa":
        mostrar_registo()
    elif opcao_menu == "🔐 Login Prestador":
        mostrar_login_prestador()
    elif opcao_menu == "⚙️ Administração":
        mostrar_painel_admin()

def mostrar_home():
    st.header("🌟 Empresas e Prestadores Aprovados")
    
    aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]
    
    if not aprovados:
        st.info("Ainda não existem empresas aprovadas na plataforma.")
    else:
        for p in aprovados:
            with st.expander(f"🏢 {p['nome_empresa']} — [{p['categoria']}]"):
                st.write(f"📞 **Telefone:** {p['telefone']}")
                st.write(f"📍 **Localização:** Rua {p['localizacao']['rua']}, Bairro {p['localizacao']['bairro']}, {p['localizacao']['municipio']}")
                st.markdown(f"**📖 Sobre a Empresa / Serviços:** \n> {p.get('sobre_empresa', 'Sem descrição fornecida.')}")
                
                st.markdown("**📸 Portefólio:**")
                fotos = p.get('fotos', [])
                if fotos:
                    cols = st.columns(min(len(fotos), 3))
                    for idx, foto_info in enumerate(fotos):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            st.caption(f"📝 {foto_info.get('descricao', 'Sem descrição')}")

def mostrar_registo():
    st.header("📝 Registo de Novo Prestador / Empresa")
    st.write("Preencha os campos abaixo. Após submeter, o administrador validará o seu registo.")

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
        sobre_empresa = st.text_area("Fale um pouco sobre a empresa, o que faz, quais os serviços e produtos que aluga:*", height=100)

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
        st.markdown("### 📸 Upload de 6 Fotos com Descrição")
        
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
                st.error("Por favor, preencha todos os campos obrigatórios (*), incluindo a descrição da empresa.")
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
                st.success("Registo submetido com sucesso! Os dados foram guardados e aguardam validação do Administrador.")

def mostrar_login_prestador():
    st.header("🔐 Área Restrita do Prestador")
    st.write("Insira os seus dados para aceder e atualizar o seu cadastro e serviços.")

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
                novo_sobre = st.text_area("Atualizar Descrição da Empresa", value=p_atual.get('sobre_empresa', ''))
                
                if st.form_submit_button("Guardar Alterações"):
                    p_atual['telefone'] = novo_tel
                    p_atual['localizacao']['rua'] = nova_rua
                    p_atual['sobre_empresa'] = novo_sobre
                    guardar_dados(st.session_state["prestadores"])
                    st.success("Dados alterados e guardados com sucesso!")

def mostrar_painel_admin():
    st.header("⚙️ Painel de Administração")
    
    admin_pass = st.text_input("Palavra-passe de Administrador", type="password", key="adm_pass")
    
    if admin_pass != "admin123":
        st.info("Insira a palavra-passe de administração para gerir as empresas (Utilize `admin123` para teste).")
        return

    st.success("Administrador autenticado com sucesso.")
    st.markdown("### 📋 Gestão de Empresas Registadas")

    prestadores = st.session_state["prestadores"]
    
    if not prestadores:
        st.warning("Ainda não existem registos na plataforma.")
        return

    for i, p in enumerate(prestadores):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**Empresa:** {p['nome_empresa']}")
                st.write(f"**Categoria:** {p['categoria']} | **Estado:** `{p['status']}`")
                st.write(f"**Local:** {p['localizacao']['municipio']} - {p['localizacao']['bairro']}")
                st.write(f"*{p.get('sobre_empresa', '')[:60]}...*")
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
                if st.button(f"🗑️ Excluir Empresa", key=f"del_{i}"):
                    st.session_state["prestadores"].pop(i)
                    guardar_dados(st.session_state["prestadores"])
                    st.success("Empresa excluída com sucesso!")
                    st.rerun()
            st.markdown("---")

if __name__ == "__main__":
    main()
