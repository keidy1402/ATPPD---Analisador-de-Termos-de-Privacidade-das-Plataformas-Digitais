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
    import os
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.error("Chave da API do Gemini não configurada! Adicione GEMINI_API_KEY nos Secrets do Streamlit.")

# Estilização CSS para os cards de notícias
st.markdown("""
    <style>
    .parchment-card {
        background-color: #f9f9fb;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #162E5C;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Nível de risco estimado (Seção 5)
dados_risco = {
    "Whatsapp": 65, "Snapchat": 70, "Youtube": 75, 
    "Facebook": 90, "Instagram": 85, "Twitter": 80, "Tiktok": 95
}

st.title("🛡️ Analisador de Termos de Privacidade")
st.markdown("Promovendo transparência e segurança digital para os seus dados.")
st.write("---")

# --- SEÇÃO 1: SELEÇÃO DA PLATAFORMA ---
st.markdown("### 🔍 Seção 1: Selecione a Plataforma para Análise")
plataformas = ["Whatsapp", "Snapchat", "Youtube", "Facebook", "Instagram", "Twitter", "Tiktok"]
opcao = st.selectbox("Escolha uma rede social/plataforma:", plataformas)

if st.button("👁️ Analisar Termos de Privacidade"):
    # Nome esperado para o arquivo (ex: termos/whatsapp.txt)
    caminho_arquivo = f"termos{opcao.lower()}.txt"
    
    # Verifica se o arquivo .txt realmente existe na pasta
    if not os.path.exists(caminho_arquivo):
        st.error(f"Arquivo de termos não encontrado! Certifique-se de que o arquivo '{caminho_arquivo}' existe no seu repositório.")
    else:
        # Lendo o conteúdo real do arquivo .txt
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo_txt = f.read()

        with st.spinner(f"Lendo arquivo .txt e analisando políticas do {opcao}..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # --- PROCESSANDO SEÇÃO 2 (RESUMO) ---
                prompt_resumo = (
                    f"Com base exclusivamente no seguinte texto de termos de uso da plataforma {opcao}, "
                    f"faça um resumo crítico de NO MÁXIMO 7 LINHAS destacando os pontos mais invasivos ou perigosos para o usuário.\n\n"
                    f"TEXTO DOS TERMOS:\n{conteudo_txt[:15000]}" # Limitando caracteres para segurança do limite de tokens
                )
                response_resumo = model.generate_content(prompt_resumo)
                resumo_texto = response_resumo.text

                # --- PROCESSANDO SEÇÃO 3 (PALAVRAS CHAVE) ---
                prompt_palavras = (
                    f"Com base no seguinte texto de termos de uso da plataforma {opcao}, "
                    f"extraia de 15 a 20 PALAVRAS-CHAVE isoladas (separadas estritamente por vírgula) que representem os maiores riscos à privacidade contidos no texto.\n\n"
                    f"TEXTO:\n{conteudo_txt[:15000]}"
                )
                response_palavras = model.generate_content(prompt_palavras)
                palavras_risco = response_palavras.text

                # --- PROCESSANDO SEÇÃO 4 (DICAS) ---
                prompt_dicas = (
                    f"Considerando os riscos encontrados no texto de termos de uso do {opcao}, "
                    f"forneça 3 dicas práticas em formato de tópicos markdown de como o usuário pode configurar sua conta ou agir "
                    f"dentro da plataforma para se proteger após ter aceitado esses termos.\n\n"
                    f"TEXTO:\n{conteudo_txt[:15000]}"
                )
                response_dicas = model.generate_content(prompt_dicas)
                dicas_texto = response_dicas.text

                # --- SEÇÃO 2: EXIBIÇÃO DO RESUMO ---
                st.markdown("### 📝 Seção 2: Resumo Crítico dos Termos (Máx. 7 linhas)")
                st.info(resumo_texto)
                st.write("---")

                # --- SEÇÃO 3: NUVEM DE PALAVRAS ---
                st.markdown("### ☁️ Seção 3: Palavras de Maior Risco Identificadas no Arquivo")
                try:
                    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=30, colormap='Reds').generate(palavras_risco)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                except Exception as e:
                    st.warning("Exibindo termos chave extraídos:")
                    st.write(palavras_risco)
                st.write("---")

                # --- SEÇÃO 4: DICAS PRÁTICAS ---
                st.markdown("### 💡 Seção 4: Como se proteger na Plataforma")
                st.success(dicas_texto)
                st.write("---")

                # --- SEÇÃO 5: GRÁFICO COMPARATIVO E INTERPRETAÇÃO ---
                st.markdown("### 📊 Seção 5: Índice de Risco Comparativo de Privacidade")
                fig_comp, ax_comp = plt.subplots(figsize=(10, 4))
                cores = ['#d9534f' if p == opcao else '#8c8c8c' for p in dados_risco.keys()]
                ax_comp.bar(dados_risco.keys(), dados_risco.values(), color=cores)
                ax_comp.set_ylabel('Índice de Risco (0-100)')
                st.pyplot(fig_comp)
                
                prompt_comp = (
                    f"Gere uma breve interpretação comparando o risco do {opcao} (Pontuação atual: {dados_risco[opcao]}/100) "
                    f"frente ao mercado atual com base no que foi analisado no documento."
                )
                response_comp = model.generate_content(prompt_comp)
                st.markdown(f"**Análise Comparativa:** {response_comp.text}")
                st.write("---")

            except Exception as e:
                st.error(f"Erro ao processar dados com a API do Gemini: {e}")

    # --- SEÇÃO 6: NOTÍCIAS RELACIONADAS ---
    st.markdown(f"### 📰 Seção 6: O Que Estão Falando Sobre a Privacidade do {opcao}?")
    st.markdown("Fique por dentro das últimas manchetes e investigações de tratamento de dados:")
    
    termo_busca = f"{opcao} privacidade"
    termo_codificado = urllib.parse.quote(termo_busca)
    url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    try:
        resposta = requests.get(url_feed, timeout=5)
        root = ET.fromstring(resposta.content)
        noticias = root.findall('.//item')[:2]
        
        if noticias:
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                titulo1 = noticias[0].find('title').text
                link1 = noticias[0].find('link').text
                fonte1 = noticias[0].find('source').text if noticias[0].find('source') is not None else "Portal de Notícias"
                data1 = noticias[0].find('pubDate').text[:16]
                st.markdown(f"""
                    <div class="parchment-card" style="min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link1}" target="_blank" style="text-decoration: none; color: #162E5C;">{titulo1}</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte1} | Publicado em: {data1}</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Clique no título acima para conferir a reportagem diretamente da fonte original.</p>
                    </div>
                """, unsafe_allow_html=True)
            with col_n2:
                if len(noticias) > 1:
                    titulo2 = noticias[1].find('title').text
                    link2 = noticias[1].find('link').text
                    fonte2 = noticias[1].find('source').text if noticias[1].find('source') is not None else "Portal de Notícias"
                    data2 = noticias[1].find('pubDate').text[:16]
                    st.markdown(f"""
                        <div class="parchment-card" style="min-height: 200px;">
                            <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link2}" target="_blank" style="text-decoration: none; color: #162E5C;">{titulo2}</a></h4>
                            <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte2} | Publicado em: {data2}</p>
                            <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe a segunda cobertura do cenário regulatório internacional desta plataforma.</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Não encontramos notícias recentes específicas para esta plataforma no momento.")
    except Exception as e:
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            st.markdown(f"""
                <div class="parchment-card" style="min-height: 200px;">
                    <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://g1.globo.com/tecnologia/" target="_blank" style="text-decoration: none; color: #162E5C;">{opcao} e Investigações de Tratamento de Dados</a></h4>
                    <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: Portal G1 Tecnologia</p>
                    <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe as notícias sobre as auditorias mais recentes da ANPD envolvendo tratamento de informações sensíveis no Brasil.</p>
                </div>
            """, unsafe_allow_html=True)
        with col_n2:
            st.markdown(f"""
                <div class="parchment-card" style="min-height: 200px;">
                    <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://www.bbc.com/portuguese/topics/c40g969r280t" target="_blank" style="text-decoration: none; color: #162E5C;">Mudanças nas Políticas e Regulamentações da Controladora do {opcao}</a></h4>
                    <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: BBC Brasil</p>
                    <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Análise crítica sobre as novas regras globais de inteligência artificial e privacidade de dados de grandes corporações.</p>
                </div>
            """, unsafe_allow_html=True)
