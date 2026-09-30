import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Plataforma de Aluguer e Serviços",
    page_icon="🏢",
    layout="wide"
)

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

# Simulação de Base de Dados na Sessão (Para testes locais antes de ligar ao Firebase/Supabase)
if "prestadores" not in st.session_state:
    st.session_state["prestadores"] = []

def main():
    st.sidebar.title("Menu de Navegação")
    menu = st.sidebar.selectbox(
        "Escolha uma opção", 
        ["🏠 Página Inicial", "📝 Registar Empresa / Prestador", "🔐 Login Prestador", "⚙️ Painel do Administrador"]
    )

    if menu == "🏠 Página Inicial":
        mostrar_home()
    elif menu == "📝 Registar Empresa / Prestador":
        mostrar_registo()
    elif menu == "🔐 Login Prestador":
        mostrar_login_prestador()
    elif menu == "⚙️ Painel do Administrador":
        mostrar_painel_admin()

def mostrar_home():
    st.title("🌟 Plataforma de Aluguer de Produtos e Serviços")
    st.write("Encontre os melhores prestadores nas categorias de música, construção, eventos, automóveis e serviços domésticos.")
    
    st.markdown("### Empresas Aprovadas em Destaque")
    aprovados = [p for p in st.session_state["prestadores"] if p.get("status") == "Aprovado"]
    
    if not aprovados:
        st.info("Ainda não existem empresas aprovadas na plataforma.")
    else:
        for p in aprovados:
            with st.expander(f"🏢 {p['nome_empresa']} — *{p['categoria']}*"):
                st.write(f"📞 **Telefone:** {p['telefone']}")
                st.write(f"📍 **Localização:** Bairro {p['localizacao']['bairro']}, Município {p['localizacao']['municipio']}, Rua {p['localizacao']['rua']}")
                st.markdown("**Galeria / Portefólio:**")
                cols = st.columns(min(len(p['fotos']), 3))
                for idx, foto_info in enumerate(p['fotos']):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.image(foto_info['imagem'], use_container_width=True)
                        st.caption(f"📝 {foto_info['descricao']}")

def mostrar_registo():
    st.title("📝 Registo de Nova Empresa / Prestador")
    st.write("Preencha os campos abaixo para submeter o seu registo. O administrador irá analisar e aprovar a sua inserção.")

    with st.form("form_registo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_empresa = st.text_input("Nome da Empresa / Prestador*")
            telefone = st.text_input("Número de Telefone*")
            categoria = st.selectbox("Categoria Principal*", CATEGORIAS)
        with col2:
            password = st.text_input("Palavra-passe (Password)*", type="password")
            confirmar_password = st.text_input("Confirmar Palavra-passe*", type="password")

        st.markdown("---")
        st.markdown("### Localização")
        col_loc1, col_loc2, col_loc3 = st.columns(3)
        with col_loc1:
            bairro = st.text_input("Bairro*")
        with col_loc2:
            municipio = st.text_input("Município*")
        with col_loc3:
            rua = st.text_input("Rua*")

        st.markdown("---")
        st.markdown("### Fotos e Descrições (Faça o upload de até 6 fotos com respetiva legenda)")
        
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
            elif len(fotos_dados) == 0:
                st.warning("Recomendamos o envio de pelo menos uma foto para validação.")
            else:
                novo_prestador = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "nome_empresa": nome_empresa,
                    "telefone": telefone,
                    "categoria": categoria,
                    "password": password,
                    "localizacao": {"bairro": bairro, "municipio": municipio, "rua": rua},
                    "fotos": fotos_dados,
                    "status": "Pendente"  # Pendente de aprovação pelo Administrador
                }
                st.session_state["prestadores"].append(novo_prestador)
                st.success("Registo efetuado com sucesso! Aguarde a validação do Administrador para aparecer na plataforma.")

def mostrar_login_prestador():
    st.title("🔐 Área do Prestador")
    st.write("Faça login com os seus dados para atualizar o seu perfil ou catálogo.")

    nome_pesquisa = st.text_input("Nome da Empresa")
    pass_input = st.text_input("Palavra-passe", type="password")

    if st.button("Entrar"):
        prestador = next((p for p in st.session_state["prestadores"] if p["nome_empresa"].lower() == nome_pesquisa.lower() and p["password"] == pass_input), None)
        
        if prestador:
            st.session_state["prestador_logado"] = prestador['id']
            st.success(f"Bem-vindo, {prestador['nome_empresa']}!")
        else:
            st.error("Empresa não encontrada ou palavra-passe incorreta.")

    if "prestador_logado" in st.session_state:
        p_id = st.session_state["prestador_logado"]
        p_atual = next((p for p in st.session_state["prestadores"] if p["id"] == p_id), None)
        
        if p_atual:
            st.markdown("---")
            st.subheader(f"Atualizar Dados: {p_atual['nome_empresa']}")
            with st.form("form_update"):
                novo_tel = st.text_input("Novo Telefone", value=p_atual['telefone'])
                nova_rua = st.text_input("Nova Rua", value=p_atual['localizacao']['rua'])
                
                if st.form_submit_button("Guardar Alterações"):
                    p_atual['telefone'] = novo_tel
                    p_atual['localizacao']['rua'] = nova_rua
                    st.success("Dados atualizados com sucesso!")

def mostrar_painel_admin():
    st.title("⚙️ Painel do Administrador")
    
    # Simples autenticação de admin para testes
    admin_pass = st.text_input("Palavra-passe de Administrador", type="password")
    if admin_pass != "admin123":
        st.warning("Insira a palavra-passe de administrador (utilize `admin123` para teste).")
        return

    st.success("Administrador autenticado com sucesso.")
    st.markdown("### Gestão de Prestadores e Aprovações")

    prestadores = st.session_state["prestadores"]
    
    if not prestadores:
        st.info("Nenhum prestador registado até ao momento.")
        return

    for i, p in enumerate(prestadores):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**Empresa:** {p['nome_empresa']}")
                st.write(f"**Categoria:** {p['categoria']} | **Status:** {p['status']}")
                st.write(f"**Local:** {p['localizacao']['municipio']} - {p['localizacao']['bairro']}")
            with col2:
                if p['status'] == "Pendente":
                    if st.button(f"Aprovar {p['nome_empresa']}", key=f"apr_{i}"):
                        p['status'] = "Aprovado"
                        st.rerun()
                else:
                    if st.button(f"Suspender {p['nome_empresa']}", key=f"susp_{i}"):
                        p['status'] = "Pendente"
                        st.rerun()
            with col3:
                if st.button(f"🗑️ Excluir {p['nome_empresa']}", key=f"del_{i}"):
                    st.session_state["prestadores"].pop(i)
                    st.rerun()
            st.markdown("---")

if __name__ == "__main__":
    main()
