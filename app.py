import streamlit as st
import google.generativeai as genai
import xml.etree.ElementTree as ET
import urllib.parse
import requests
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Analisador de Privacidade Digital",
    page_icon="🛡️",
    layout="wide"
)

# --- CONFIGURAÇÃO DA API DO GEMINI ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.error("Chave da API do Gemini não configurada! Adicione GEMINI_API_KEY nos Secrets do Streamlit.")

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
    <style>
    /* Estilização dos cards de notícias */
    .news-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        border-top: 4px solid #1E3A8A;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    }
    
    .card-title a {
        text-decoration: none !important; 
        color: #1E3A8A !important;
        font-weight: 600;
    }
    .card-title a:hover {
        color: #3B82F6 !important;
    }
    
    .source-badge {
        background-color: #F3F4F6;
        color: #4B5563;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Dados de Risco
dados_risco = {
    "Whatsapp": 65, "Snapchat": 70, "Youtube": 75, 
    "Facebook": 90, "Instagram": 85, "Twitter": 80, "Tiktok": 95
}

# --- HEADER PRINCIPAL ---
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.markdown("<h1 style='text-align: center; margin: 0;'>🛡️</h1>", unsafe_allow_html=True)
with col_title:
    st.title("Analisador de Termos de Privacidade")
    st.caption("Promovendo transparência, clareza e segurança digital sobre os seus dados pessoais.")

st.markdown("---")

# --- SEÇÃO 1: SELEÇÃO DA PLATAFORMA ---
st.markdown("### 🔍 Escolha uma Plataforma para Análise")
plataformas = ["Whatsapp", "Snapchat", "Youtube", "Facebook", "Instagram", "Twitter", "Tiktok"]

col_select, col_btn = st.columns([3, 1])
with col_select:
    opcao = st.selectbox("Selecione a rede social ou serviço:", plataformas, label_visibility="collapsed")
with col_btn:
    disparar_analise = st.button("👁️ Analisar Políticas", use_container_width=True, type="primary")

if disparar_analise:
    caminho_arquivo = f"{opcao.upper()}.txt"
    
    if not os.path.exists(caminho_arquivo):
        st.error(f"Arquivo de termos não encontrado! Certifique-se de que o arquivo '{caminho_arquivo}' existe no seu repositório.")
    else:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo_txt = f.read()

        with st.spinner(f"Extraindo insights acionáveis das políticas do {opcao}..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Prompts Focados em CONTEÚDO TÉCNICO E ACIONÁVEL, mantendo a escaneabilidade
                prompt_resumo = (
                    f"Leia os termos de uso do {opcao}. Extraia os 3 pontos mais invasivos à privacidade do usuário. "
                    f"Apresente em formato de bullet points curtos. Para cada ponto, explique especificamente O QUE eles coletam "
                    f"e QUAL O RISCO REAL para o usuário (ex: 'coletam histórico de navegação para venda de perfil'). "
                    f"Seja técnico, direto e altamente informativo. Ocupe no máximo 8 a 10 linhas.\n\n"
                    f"TEXTO DOS TERMOS:\n{conteudo_txt[:15000]}"
                )
                
                prompt_palavras = (
                    f"Extraia de 10 a 15 termos ou jargões técnicos isolados (separados apenas por vírgula) que representem "
                    f"as práticas mais agressivas de coleta de dados neste texto do {opcao}.\n\n"
                    f"TEXTO:\n{conteudo_txt[:15000]}"
                )
                
                prompt_dicas = (
                    f"Baseado na política do {opcao}, escreva 3 instruções passo a passo de como o usuário pode proteger sua conta. "
                    f"Siga estritamente esta estrutura para cada dica:\n"
                    f"**[Nome da Ação]**: [Explicação breve do porquê fazer isso] -> **Como fazer:** [Caminho aproximado no menu do app, ex: Configurações > Privacidade > Desativar X].\n"
                    f"Não invente menus, use a lógica padrão do app. Seja extremamente útil e diretivo. Máximo de 10 linhas totais.\n\n"
                    f"TEXTO:\n{conteudo_txt[:15000]}"
                )

                response_resumo = model.generate_content(prompt_resumo)
                resumo_texto = response_resumo.text

                response_palavras = model.generate_content(prompt_palavras)
                palavras_risco = response_palavras.text

                response_dicas = model.generate_content(prompt_dicas)
                dicas_texto = response_dicas.text

                # --- EXIBIÇÃO DE RESULTADOS ---
                st.markdown("---")
                
                col_metric, col_resumo = st.columns([1, 3])
                
                with col_metric:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.metric(
                        label=f"Índice de Risco: {opcao}", 
                        value=f"{dados_risco[opcao]}/100", 
                        delta="Risco Alto" if dados_risco[opcao] >= 75 else "Risco Moderado",
                        delta_color="inverse"
                    )
                
                with col_resumo:
                    st.markdown("### 📝 Riscos Identificados na Política")
                    st.warning(resumo_texto)

                st.markdown("---")

                col_nuvem, col_grafico = st.columns(2)
                
                with col_nuvem:
                    st.markdown("### ☁️ Termos Sensíveis Encontrados")
                    try:
                        wordcloud = WordCloud(
                            width=600, height=350, 
                            background_color='white', 
                            max_words=20, 
                            colormap='Reds',
                            prefer_horizontal=0.7
                        ).generate(palavras_risco)
                        
                        fig, ax = plt.subplots(figsize=(6, 3.5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    except Exception:
                        st.warning("Termos extraídos:")
                        st.write(palavras_risco)

                with col_grafico:
                    st.markdown("### 📊 Índice de Risco Comparativo")
                    fig_comp, ax_comp = plt.subplots(figsize=(6, 3.5))
                    cores = ['#EF4444' if p == opcao else '#9CA3AF' for p in dados_risco.keys()]
                    
                    bars = ax_comp.bar(dados_risco.keys(), dados_risco.values(), color=cores, width=0.6)
                    ax_comp.set_ylabel('Pontuação (0-100)', fontsize=9, color='#4B5563')
                    ax_comp.tick_params(axis='both', labelsize=8, colors='#4B5563')
                    
                    for spine in ['top', 'right', 'left', 'bottom']:
                        ax_comp.spines[spine].set_visible(False)
                    ax_comp.grid(axis='y', linestyle='--', alpha=0.3)
                    
                    st.pyplot(fig_comp)

                prompt_comp = (
                    f"Explique de forma analítica por que o {opcao} tem nota de risco {dados_risco[opcao]}/100 em comparação ao mercado. "
                    f"Mencione 1 ou 2 práticas de coleta de dados exclusivas ou agressivas dessa plataforma para justificar a nota. "
                    f"Seja denso em informação, mas ocupe no máximo 4 linhas."
                )
                response_comp = model.generate_content(prompt_comp)
                st.markdown(f"💡 **Por que essa nota?** *{response_comp.text}*")

                st.markdown("---")

                st.markdown("### 🛡️ Manual Prático de Proteção")
                st.success(dicas_texto)
                st.markdown("---")

            except Exception as e:
                st.error(f"Erro ao processar dados com a API do Gemini: {e}")

# --- SEÇÃO 6: NOTÍCIAS RELACIONADAS ---
st.markdown(f"### 📰 Monitoramento de Vazamentos e Privacidade: {opcao if 'opcao' in locals() else ''}")
st.caption("Fique por dentro das últimas manchetes, vazamentos ou investigações envolvendo os seus dados:")

termo_busca = f"{opcao if 'opcao' in locals() else 'Redes Sociais'} vazamento de dados privacidade"
termo_codificado = urllib.parse.quote(termo_busca)
url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

col_n1, col_n2 = st.columns(2)

try:
    resposta = requests.get(url_feed, timeout=5)
    root = ET.fromstring(resposta.content)
    noticias = root.findall('.//item')[:2]
    
    if noticias:
        titulo1 = noticias[0].find('title').text
        link1 = noticias[0].find('link').text
        fonte1 = noticias[0].find('source').text if noticias[0].find('source') is not None else "Portal de Notícias"
        data1 = noticias[0].find('pubDate').text[:16]
        
        with col_n1:
            st.markdown(f"""
                <div class="news-card">
                    <span class="source-badge">{fonte1}</span>
                    <h4 class="card-title"><a href="{link1}" target="_blank">{titulo1}</a></h4>
                    <p style="color: #6B7280; font-size: 0.8rem; margin: 8px 0 0 0;">📅 Publicado em: {data1}</p>
                </div>
            """, unsafe_allow_html=True)
            
        if len(noticias) > 1:
            titulo2 = noticias[1].find('title').text
            link2 = noticias[1].find('link').text
            fonte2 = noticias[1].find('source').text if noticias[1].find('source') is not None else "Portal de Notícias"
            data2 = noticias[1].find('pubDate').text[:16]
            
            with col_n2:
                st.markdown(f"""
                    <div class="news-card">
                        <span class="source-badge">{fonte2}</span>
                        <h4 class="card-title"><a href="{link2}" target="_blank">{titulo2}</a></h4>
                        <p style="color: #6B7280; font-size: 0.8rem; margin: 8px 0 0 0;">📅 Publicado em: {data2}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Não encontramos notícias recentes sobre vazamentos ou privacidade para esta plataforma nas últimas horas.")

except Exception:
    with col_n1:
        st.markdown(f"""
            <div class="news-card">
                <span class="source-badge">Portal G1</span>
                <h4 class="card-title"><a href="https://g1.globo.com/tecnologia/" target="_blank">Novas Investigações de Tratamento de Dados no Brasil</a></h4>
                <p style="color: #6B7280; font-size: 0.85rem; margin-top: 10px;">Acompanhe atualizações sobre as auditorias mais recentes da ANPD envolvendo tratamento de informações sensíveis.</p>
            </div>
        """, unsafe_allow_html=True)
    with col_n2:
        st.markdown(f"""
            <div class="news-card">
                <span class="source-badge">TecMundo</span>
                <h4 class="card-title"><a href="https://www.tecmundo.com.br/seguranca" target="_blank">Aprenda a Blindar Suas Redes Sociais</a></h4>
                <p style="color: #6B7280; font-size: 0.85rem; margin-top: 10px;">Artigos práticos sobre segurança da informação, autenticação em duas etapas e gestão de permissões.</p>
            </div>
        """, unsafe_allow_html=True)
