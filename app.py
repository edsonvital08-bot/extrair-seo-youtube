import streamlit as st
import yt_dlp
import requests
import re
from st_copy_to_clipboard import st_copy_to_clipboard

# Configuração da página para o tema escuro e layout idêntico ao da imagem
st.set_page_config(page_title="Extrair SEO do YouTube", layout="centered")

# Estilização CSS para forçar o visual escuro e o alinhamento dos componentes
st.markdown("""
    <style>
    .stApp {
        background-color: #121824;
        color: #ffffff;
    }
    h1 {
        text-align: center;
        text-transform: uppercase;
        font-size: 26px !important;
        letter-spacing: 1px;
        color: #e2e8f0 !important;
        margin-bottom: 30px !important;
    }
    label {
        color: #a3e635 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    /* Botão Verde Principal (Buscar) */
    div.element-container:has(button[key="btn_buscar"]) button {
        width: 100%;
        background-color: #84cc16 !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        padding: 10px !important;
        border-radius: 6px !important;
    }
    div.element-container:has(button[key="btn_buscar"]) button:hover {
        background-color: #a3e635 !important;
    }
    
    /* Botão Laranja (Copiar Tudo) */
    div.element-container:has(button[key="btn_copiar_tudo"]) button {
        width: 100%;
        background-color: #f97316 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        padding: 12px !important;
        border-radius: 6px !important;
        margin-top: 20px;
    }
    div.element-container:has(button[key="btn_copiar_tudo"]) button:hover {
        background-color: #fb923c !important;
    }

    /* Botão Vermelho (Limpar Dados) */
    div.element-container:has(button[key="btn_limpar"]) button {
        width: 100%;
        background-color: #ef4444 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        padding: 10px !important;
        border-radius: 6px !important;
        margin-top: 10px;
    }
    div.element-container:has(button[key="btn_limpar"]) button:hover {
        background-color: #f87171 !important;
    }
    
    /* Botões Azuis de Download e customização dos botões de cópia */
    div.stDownloadButton > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #60a5fa !important;
    }
    
    /* Ajuste para alinhar o botão de cópia ao lado da caixa de texto */
    div[data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("EXTRAIR SEO DO YOUTUBE")

# Inicializa a memória estável do app (Session State)
if 'seo_dados' not in st.session_state:
    st.session_state.seo_dados = None

# Função para limpar os dados da tela
def limpar_dados():
    st.session_state.seo_dados = None

# Entrada da URL do usuário
url_video = st.text_input("Digite a URL do vídeo do YouTube:", placeholder="https://www.youtube.com/watch?v=...")

# Executa a busca ao clicar
if st.button("Buscar Dados SEO", key="btn_buscar"):
    if url_video:
        with st.spinner("Acessando o YouTube e extraindo metadados reais..."):
            try:
                ydl_opts = {'skip_download': True, 'quiet': True, 'extract_flat': False}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url_video, download=False)
                    
                    # Extração precisa dos dados reais
                    titulo = info.get('title', 'Não encontrado')
                    descricao = info.get('description', 'Não encontrada')
                    
                    tags_lista = info.get('tags', [])
                    tags = ", ".join(tags_lista) if tags_lista else "Nenhuma tag encontrada neste vídeo."
                    
                    hashtags_encontradas = re.findall(r"#\w+", descricao)
                    hashtags = " ".join(hashtags_encontradas) if hashtags_encontradas else "Nenhuma hashtag encontrada."
                    
                    views = info.get('view_count', 0)
                    likes = info.get('like_count', 'N/A')
                    autor = info.get('uploader', 'Desconhecido')
                    id_video = info.get('id', '')
                    info_geral = f"Canal: {autor}\nVisualizações: {views:,}\nCurtidas: {likes}\nID do Vídeo: {id_video}"
                    
                    thumb_url = info.get('thumbnail', f"https://img.youtube.com/vi/{id_video}/maxresdefault.jpg")
                    
                    # Baixa a imagem em segundo plano para o botão de download salvar na hora
                    try:
                        img_data = requests.get(thumb_url).content
                    except:
                        img_data = b""

                    # Memoriza os dados para os botões de copiar não resetarem a tela
                    st.session_state.seo_dados = {
                        "titulo": titulo,
                        "descricao": descricao,
                        "tags": tags,
                        "hashtags": hashtags,
                        "info_geral": info_geral,
                        "thumb_url": thumb_url,
                        "img_data": img_data,
                        "id_video": id_video
                    }
                    
            except Exception as e:
                st.error("Erro ao tentar acessar o vídeo. Certifique-se de que a URL está correta.")
                st.caption(f"Detalhes técnicos: {e}")
    else:
        st.warning("Por favor, insira uma URL válida.")

# Renderiza os resultados fixos se estiverem carregados na memória
if st.session_state.seo_dados is not None:
    dados = st.session_state.seo_dados

    st.write("### Miniatura do Vídeo:")
    st.image(dados["thumb_url"], use_container_width=True)
    
    # Botão de download direto e imediato da imagem
    if dados["img_data"]:
        st.download_button(
            label="📥 Fazer Download da Miniatura",
            data=dados["img_data"],
            file_name=f"thumbnail_{dados['id_video']}.jpg",
            mime="image/jpeg",
            key="download_thumb_btn"
        )
    
    st.markdown("---")

    # Função que cria o campo de texto estruturado com o botão de cópia real ao lado
    def criar_campo_com_copiar(label, texto, chave):
        col1, col2 = st.columns([6, 1.2])
        with col1:
            st.text_area(label, value=texto, height=110, key=f"txt_{chave}")
        with col2:
            st.write("Copiar:")
            # Esta ferramenta lida perfeitamente com a transferência sem reexecutar ou quebrar o app
            st_copy_to_clipboard(texto, before_copy_label="📋", after_copy_label="✔ OK", key=f"clip_{chave}")

    # Exibição dos blocos de dados individuais
    criar_campo_com_copiar("Título:", dados["titulo"], "tit")
    criar_campo_com_copiar("Meta Descrição:", dados["descricao"], "desc")
    criar_campo_com_copiar("Tags:", dados["tags"], "tg")
    criar_campo_com_copiar("Hashtags:", dados["hashtags"], "hash")
    criar_campo_com_copiar("Informações do Vídeo:", dados["info_geral"], "inf")
    
    st.markdown("---")
    
    # Estruturação da área "Copiar tudo de uma vez"
    texto_completo_seo = (
        f"--- TÍTULO ---\n{dados['titulo']}\n\n"
        f"--- META DESCRIÇÃO ---\n{dados['descricao']}\n\n"
        f"--- TAGS ---\n{dados['tags']}\n\n"
        f"--- HASHTAGS ---\n{dados['hashtags']}\n\n"
        f"--- INFORMAÇÕES DO VÍDEO ---\n{dados['info_geral']}"
    )
    
    st.write("### 📋 Copiar Todo o SEO de uma Vez (Título para baixo):")
    st_copy_to_clipboard(texto_completo_seo, before_copy_label="💥 Clique Aqui para Copiar Tudo Junto", after_copy_label="🔥 TUDO COPIADO!", key="clip_tudo")
    
    # Botão de Limpar no rodapé da página
    st.button("❌ Limpar Dados e Buscar Outro Vídeo", key="btn_limpar", on_click=limpar_dados)