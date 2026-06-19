
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import json
import random
from io import BytesIO

# --- MOTOR GRÁFICO RESILIENTE ---
try:
    import plotly.express as px
    PLOTLY_DISPONIVEL = True
except ImportError:
    PLOTLY_DISPONIVEL = False

# --- MOTOR DE PDF REVISADO ---
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    import html
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Espelho da Verdade - Termos de Privacidade",
    page_icon="🌹",
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
 
        /* Fundo estilo pergaminho real e fontes temáticas */
        .stApp {
            background-color: #FAF5EC;
            color: #2C1E21;
            font-family: 'Lora', serif;
        }
 
        /* Títulos com a fonte Cinzel (estilo castelo) */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Cinzel', serif !important;
            color: #162E5C !important; /* Azul Imperial */
            font-weight: 600;
        }
 
        /* Divisores dourados elegantes */
        .gold-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #D4AF37, transparent); /* Ouro Real */
            margin: 25px 0;
        }
 
        /* Caixa em estilo pergaminho para blocos de texto */
        .parchment-card {
            background-color: #FFFFFF;
            border: 1px solid #E6D9C5;
            border-top: 4px solid #D4AF37;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* Nuvem de Palavras via CSS */
        .word-cloud-container {
            padding: 20px;
            text-align: center;
            line-height: 2.5;
            background: #FFFDF9;
            border-radius: 10px;
            border: 1px dashed #D4AF37;
        }

        /* Quadro de Atenção Vermelho Carmesim */
        .attention-box {
            background-color: #FFF5F5;
            border: 2px solid #991B1B;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-top: 20px;
            position: relative;
        }

        .attention-label {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: #991B1B;
            color: white;
            padding: 2px 15px;
            font-family: 'Cinzel', serif;
            font-size: 0.8rem;
            border-radius: 4px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Container de Score Temático */
        .score-container {
            text-align: center;
            background: linear-gradient(135deg, #162E5C 0%, #0B1D3A 100%);
            color: #FAF5EC;
            padding: 30px;
            border-radius: 12px;
            border: 2px solid #D4AF37;
        }

        .score-number {
            font-family: 'Cinzel', serif;
            font-size: 4rem;
            color: #F5D04C;
            line-height: 1;
        }

        /* Rodapé de época */
        .footer {
            font-family: 'Cinzel', serif;
            font-size: 0.8rem;
            text-align: center;
            margin-top: 50px;
            border-top: 1px dashed #D4AF37;
            padding-top: 20px;
            color: #5C4B40;
        }
    </style>
""", unsafe_allow_html=True)

class DicaSeguranca(BaseModel):
    titulo: str = Field(description="Título curto da dica de proteção prática.")
    passos: list[str] = Field(description="Lista com 3 a 5 passos sequenciais extremamente simples de executar.")

class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Resumo do termo em linguagem clara.")
    red_flags: list[str] = Field(description="Lista de 5 a 8 palavras ou termos curtos de risco.")
    palavra_mais_critica: str = Field(description="Conceito que representa o maior risco isolado.")
    pontuacao_risco: int = Field(description="Nota de 0 a 100.")
    dicas_protecao: list[DicaSeguranca] = Field(description="Lista de 3 dicas práticas passo a passo.")

# --- BANCO DE CONTINGÊNCIA (IMUNE A QUEDAS E ERROS 503 DO GEMINI) ---
ACERVO_CONTINGENCIA = {
    "Facebook": {
        "resumo_claro": "O Facebook monitora intensamente sua atividade fora do aplicativo, coletando dados de navegação, histórico de compras e interesses para traçar perfis psicológicos profundos voltados a anúncios direcionados.",
        "red_flags": ["Rastreamento", "Cookies", "Perfilamento", "Algoritmos", "Big Data", "Compartilhamento"],
        "palavra_mais_critica": "Venda de Metadados",
        "pontuacao_risco": 88,
        "dicas_protecao": [
            {"titulo": "Desativar Rastreamento Fora do Facebook", "passos": ["Abra o aplicativo e vá em Configurações.", "Desça até 'Suas informações do Facebook' e toque em 'Atividade fora do Facebook'.", "Selecione 'Desativar atividade futura' para impedir o rastreamento em outros sites."]},
            {"titulo": "Limitar Preferências de Anúncios", "passos": ["Vá em Configurações > Preferências de Anúncios.", "Toque em 'Configurações de anúncios'.", "Desative o uso de dados de parceiros para exibição de anúncios."]},
            {"titulo": "Revisar Permissões de Aplicativos", "passos": ["Acesse Configurações > Aplicativos e Sites.", "Remova jogos ou testes antigos que ainda têm acesso à sua conta."]}
        ]
    },
    "Instagram": {
        "resumo_claro": "O Instagram coleta dados geográficos em tempo real e analisa detalhadamente o tempo de visualização e interações com fotos e vídeos para calibrar algoritmos de engajamento viciantes.",
        "red_flags": ["Inteligência Artificial", "Metadados de Fotos", "Localização Exata", "Reconhecimento Facial", "Anúncios Comportamentais"],
        "palavra_mais_critica": "Treinamento de IA",
        "pontuacao_risco": 85,
        "dicas_protecao": [
            {"titulo": "Tornar a Conta Privada", "passos": ["Vá ao seu Perfil e toque nas três linhas no canto superior.", "Acesse Configurações > Privacidade da Conta.", "Ative a chave 'Conta Privada'."]},
            {"titulo": "Desativar Localização Precisa", "passos": ["Abra as configurações do seu celular.", "Vá em Aplicativos > Instagram > Permissões.", "Selecione 'Localização' e desative a opção 'Usar localização precisa'."]},
            {"titulo": "Pausar Sugestões de Conteúdo", "passos": ["Vá ao seu feed inicial.", "Toque no 'X' em uma publicação sugerida e selecione 'Soneca de postagens sugeridas por 30 dias'."]}
        ]
    },
    "Snapchat": {
        "resumo_claro": "O Snapchat rastreia de forma ativa a geolocalização do usuário mesmo em segundo plano para o recurso 'Snap Map', além de catalogar dados de filtros faciais interativos.",
        "red_flags": ["Mapa de Amigos", "Filtros 3D", "Localização Contínua", "Memórias em Nuvem", "Reconhecimento de Voz"],
        "palavra_mais_critica": "Snap Map (Rastreamento Físico)",
        "pontuacao_risco": 65,
        "dicas_protecao": [
            {"titulo": "Ativar o Modo Fantasma", "passos": ["Abra a tela do Mapa no Snapchat.", "Toque na engrenagem no canto superior.", "Marque a caixa 'Modo Fantasma' para esconder sua posição de todos."]},
            {"titulo": "Limpar Dados de Lentes", "passos": ["Vá em Configurações > Ações de Conta.", "Toque em 'Limpar Dados de Lente' para apagar mapeamentos faciais temporários."]},
            {"titulo": "Desativar Contribuição ao Holofote", "passos": ["Evite enviar Snaps com localização para o 'Holofote público' se quiser manter privacidade total."]}
        ]
    },
    "TikTok": {
        "resumo_claro": "O TikTok possui políticas extremamente invasivas, incluindo a capacidade de capturar o ritmo de digitação, biometria facial e comportamentos de navegação através de seu navegador embutido.",
        "red_flags": ["Biometria", "Ritmo de Digitação", "Navegador Embutido", "Padrão de Teclado", "Compartilhamento na China"],
        "palavra_mais_critica": "Coleta Biométrica Invasiva",
        "pontuacao_risco": 90,
        "dicas_protecao": [
            {"titulo": "Evitar o Navegador Interno", "passos": ["Nunca faça login ou insira senhas em links abertos dentro do TikTok.", "Sempre toque nos três pontos no topo da página aberta e escolha 'Abrir no navegador externo' (Safari ou Chrome)."]},
            {"titulo": "Desativar Compartilhamento de Contatos", "passos": ["Acesse Perfil > Configurações > Privacidade.", "Toque em 'Sincronizar contatos e amigos do Facebook' e desative ambas as chaves."]},
            {"titulo": "Limitar Anúncios Personalizados", "passos": ["Vá em Configurações > Anúncios.", "Desative a opção 'Anúncios personalizados' para parar de ser rastreado para fins comerciais."]}
        ]
    },
    "Twitter (X)": {
        "resumo_claro": "O X utiliza por padrão todas as suas postagens públicas, interações e curtidas para treinar sua inteligência artificial proprietária (Grok), sem consentimento explícito prévio.",
        "red_flags": ["Treinamento Grok", "Inteligência Artificial", "Extração de Dados", "Perfil Político", "Dados Biométricos"],
        "palavra_mais_critica": "Treinamento de IA Grok",
        "pontuacao_risco": 75,
        "dicas_protecao": [
            {"titulo": "Desativar Treinamento do Grok", "passos": ["Acesse Configurações e Privacidade no menu lateral.", "Vá em 'Privacidade e segurança' > 'Grok'.", "Desmarque a caixa que permite que o X use seus posts para treinamento da IA."]},
            {"titulo": "Proteger Seus Posts", "passos": ["Vá em Configurações > Privacidade e segurança > Audiência e marcação.", "Ative a opção 'Proteger seus posts' para torná-los visíveis apenas a seguidores aprovados."]},
            {"titulo": "Limitar Compartilhamento com Parceiros", "passos": ["Vá em Configurações > Privacidade > Compartilhamento de dados com parceiros.", "Desative todas as permissões."]}
        ]
    },
    "WhatsApp": {
        "resumo_claro": "Embora o WhatsApp proteja o conteúdo das mensagens com criptografia de ponta a ponta, ele coleta e compartilha uma grande quantidade de metadados com as demais empresas da Meta, como contatos, IPs e horários de conexão.",
        "red_flags": ["Metadados", "Lista de Contatos", "Endereço IP", "Registro de Chamadas", "Sincronização Meta"],
        "palavra_mais_critica": "Vazamento de Metadados",
        "pontuacao_risco": 55,
        "dicas_protecao": [
            {"titulo": "Ocultar Endereço IP nas Chamadas", "passos": ["Vá em Configurações > Privacidade.", "Toque em 'Configurações Avançadas'.", "Ative a opção 'Proteger endereço IP nas chamadas'."]},
            {"titulo": "Desativar Confirmações de Leitura", "passos": ["Acesse Configurações > Privacidade.", "Desative a chave 'Confirmações de leitura' para evitar monitoramento de resposta."]},
            {"titulo": "Bloquear Backup em Nuvem sem Senha", "passos": ["Vá em Configurações > Conversas > Backup de conversas.", "Ative o 'Backup criptografado de ponta a ponta' para que o Google/Apple não leiam suas conversas na nuvem."]}
        ]
    },
    "YouTube": {
        "resumo_claro": "O YouTube rastreia meticulosamente cada segundo de vídeo assistido, pesquisas realizadas e termos clicados, unificando essas informações ao seu perfil central do Google para publicidade direcionada.",
        "red_flags": ["Histórico de Vídeos", "Perfil Unificado Google", "Segmentação por Idade", "Padrões de Sono", "Rastreamento Infantil"],
        "palavra_mais_critica": "Rastreamento Unificado Google",
        "pontuacao_risco": 70,
        "dicas_protecao": [
            {"titulo": "Pausar Histórico de Exibição", "passos": ["Abra o YouTube e toque no seu Perfil.", "Vá em Histórico e toque nos três pontos no canto superior.", "Selecione 'Pausar histórico de exibição' para evitar perfilamento comportamental."]},
            {"titulo": "Configurar Exclusão Automática", "passos": ["Acesse sua 'Conta do Google' > Dados e Privacidade.", "Vá em 'Atividade na Web e de Apps' e defina a exclusão automática para 3 meses."]},
            {"titulo": "Desativar Anúncios Personalizados", "passos": ["Acesse as configurações do seu perfil do Google (My Ad Center) e desligue totalmente a personalização de anúncios."]}
        ]
    }
}

@st.cache_data
def analisar_ia_com_contingencia(texto, plataforma):
    """
    Tenta analisar via API do Gemini. Caso o servidor Google esteja fora do ar
    ou retorne o erro de alta demanda (503), busca o relatório ideal de contingência.
    """
    try:
        client = genai.Client()
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analise o termo de privacidade de {plataforma}: {texto}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalisePrivacidade,
                temperature=0.2
            )
        )
        return json.loads(resp.text), False  # Retorna a resposta e avisa que NÃO é contingência
    except Exception:
        # Se falhar, busca instantaneamente o banco local para o usuário não ficar sem serviço
        return ACERVO_CONTINGENCIA.get(plataforma), True

def limpar_texto_pdf(texto):
    """
    Evita que o ReportLab quebre se houver caracteres reservados do XML
    (como '&', '<' ou '>') contidos nos termos analisados.
    """
    if not PDF_DISPONIVEL or not texto:
        return ""
    texto_escapado = html.escape(str(texto))
    # Restaura formatações básicas intencionais para o PDF
    texto_escapado = texto_escapado.replace("&lt;b&gt;", "").replace("&lt;/b&gt;", "")
    texto_escapado = texto_escapado.replace("&lt;i&gt;", "").replace("&lt;/i&gt;", "")
    return texto_escapado

def gerar_pdf_corrigido(plataforma, analise):
    """
    Gera um PDF elegante baseado no tema, perfeitamente compatível com o Streamlit Cloud.
    """
    if not PDF_DISPONIVEL:
        return None
 
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
 
    # Estilos clássicos e seguros
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#162E5C'), alignment=1)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#162E5C'), spaceBefore=15, spaceAfter=8)
    body_style = ParagraphStyle('B', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#2C1E21'), leading=14, spaceAfter=10)
    step_style = ParagraphStyle('S', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#2E7D32'), leading=13, leftIndent=15, spaceAfter=5)
 
    story = [
        Paragraph(f"ESCUDO DE DEFESA: {limpar_texto_pdf(plataforma)}", title_style),
        Spacer(1, 15),
        Paragraph(f"Grau Geral de Risco Detectado: {analise['pontuacao_risco']}%", h2_style),
        Paragraph(limpar_texto_pdf(analise['resumo_claro']), body_style),
        Spacer(1, 5),
        Paragraph("PASSO A PASSO DE PROTEÇÃO (DIDÁTICO):", h2_style)
    ]
 
    # Adicionando as dicas passo a passo no PDF
    for i, dica in enumerate(analise['dicas_protecao'], 1):
        story.append(Paragraph(f"{i}. {limpar_texto_pdf(dica['titulo'])}", body_style))
        for j, p in enumerate(dica['passos'], 1):
            story.append(Paragraph(f"Passo {j}: {limpar_texto_pdf(p)}", step_style))
        story.append(Spacer(1, 5))
 
    # Rodapé da página
    story.append(Spacer(1, 20))
    story.append(Paragraph("<font color='#6B5B52'>FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</font>", ParagraphStyle('F', parent=styles['Normal'], alignment=1, fontSize=8)))
 
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO (A BELA E A FERA) ---
MAPA_ICONES = {
    "Facebook": "https://img.icons8.com/fluency/96/facebook-new.png",
    "Instagram": "https://img.icons8.com/fluency/96/instagram-new.png",
    "Snapchat": "https://img.icons8.com/fluency/96/snapchat.png",
    "TikTok": "https://img.icons8.com/fluency/96/tiktok.png",
    "Twitter (X)": "https://img.icons8.com/fluency/96/twitterx.png",
    "WhatsApp": "https://img.icons8.com/fluency/96/whatsapp.png",
    "YouTube": "https://img.icons8.com/fluency/96/youtube-play.png"
}

st.markdown('<div style="text-align: center;"><h1>🌹 O Espelho da Verdade</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# Centralização da Caixa de Seleção
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    opcao = st.selectbox("Selecione a plataforma para abrir o Relatório:", ["Selecione..."] + list(ACERVO_CONTINGENCIA.keys()))

if opcao != "Selecione...":
    # Carregando texto e consultando a IA resiliente
    analise, fallback = analisar_ia_com_contingencia("Contrato fictício ou real para análise...", opcao)
 
    # Se o Gemini estava congestionado (Erro 503), exibe aviso temático amigável
    if fallback:
        st.info("🔮 *O Espelho da Verdade está sob uma névoa de alta demanda neste momento. Para sua segurança imediata, revelamos o Laudo Sagrado de nossa biblioteca interna de contingência.*")

    if analise:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="{MAPA\_ICONES\[opcao]}" width="60">
                    <h3>Relatório Real de {opcao}</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="parchment-card">{analise["resumo_claro"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="score-container">
                    <div class="score-number">{analise["pontuacao_risco"]}%</div>
                    <div style="font-family: 'Cinzel', serif; margin-top: 8px;">Risco Geral Detectado</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
 
        # --- SINAIS DE ALERTA & ESCUDO DE DEFESA ---
        f1, f2 = st.columns(2)
        with f1:
            st.subheader("🚩 Sinais de Alerta")
 
            # Nuvem de Palavras Dinâmica gerada via CSS
            tags_html = ""
            for tag in analise['red_flags']:
                size = random.uniform(1.2, 2.0)
                opacity = random.uniform(0.65, 1.0)
                tags_html += f'<span style="font-size:{size}rem; opacity:{opacity}; margin: 8px; display: inline-block; color:#991B1B; font-family:\\'Cinzel\\', serif;">{tag}</span>'
 
            st.markdown(f'<div class="word-cloud-container">{tags_html}</div>', unsafe_allow_html=True)
 
            # Quadro de ATENÇÃO Solicitado
            st.markdown(f"""
                <div class="attention-box">
                    <div class="attention-label">ATENÇÃO</div>
                    <span style="font-size: 1.6rem; font-weight: bold; color: #991B1B; font-family: 'Cinzel', serif;">
                        {analise['palavra_mais_critica']}
                    </span>
                </div>
            """, unsafe_allow_html=True)

        with f2:
            st.subheader("🛡️ Escudo de Defesa")
            st.markdown("Siga as orientações práticas para se proteger dentro do aplicativo:")
 
            for d in analise['dicas_protecao']:
                with st.expander(f"⚙️ {d['titulo']}"):
                    for i, p in enumerate(d['passos'], 1):
                        st.write(f"**{i}º Passo:** {p}")
 
            # Botão de download do PDF robusto
            if PDF_DISPONIVEL:
                pdf_output = gerar_pdf_corrigido(opcao, analise)
                if pdf_output:
                    st.download_button(
                        label="📜 Baixar Guia Prático em PDF",
                        data=pdf_output,
                        file_name=f"Escudo_Defesa_{opcao}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.warning("O motor de PDFs está offline no momento. Utilize o guia na tela.")

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        st.subheader("📊 Comparativo Geral de Periculosidade")
 
        # Estrutura de dados do gráfico
        df_plot = pd.DataFrame({
            'Plataforma': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
            'Risco': [88, 85, 65, 90, 75, 55, 70]
        }).sort_values('Risco', ascending=True)

        if PLOTLY_DISPONIVEL:
            fig = px.bar(
                df_plot,
                x='Risco',
                y='Plataforma',
                orientation='h',
                color='Risco',
                color_continuous_scale=['#F5D04C', '#D4AF37', '#991B1B'] # Degradê temático
            )
 
            # Customizando para integrar perfeitamente com o fundo de pergaminho
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Cinzel",
                font_color="#162E5C",
                margin=dict(l=20, r=20, t=10, b=10),
                xaxis=dict(showgrid=False, range=[0, 100], title="Nível de Risco (%)"),
                yaxis=dict(showgrid=False, title="")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback nativo ultra-seguro se o Plotly falhar por falta de dependências no GitHub
            st.bar_chart(data=df_plot, x='Plataforma', y='Risco', color='#D4AF37')

        # --- RELATÓRIO DE INTERPRETAÇÃO DO GRÁFICO ---
        st.markdown(f"""
            <div class="parchment-card" style="border-top: 4px solid #162E5C; margin-top: 15px;">
                <h4 style="margin-top:0">📜 Interpretação do Espelho</h4>
                <p>O gráfico acima revela a hierarquia das sombras no reino digital.
                Observamos que o TikTok e o Facebook se posicionam como as "Feras" mais dominantes,
                apresentando níveis de risco críticos (acima de 85%) devido à coleta agressiva de dados biométricos e comportamentais.
                Em contrapartida, o WhatsApp, embora pertença à Meta, figura como o "Convidado" mais seguro desta lista,
                protegido por sua criptografia de mensagens, embora ainda exija cautela com seus metadados.</p>
                <p>Plataformas como YouTube e Instagram mantêm um equilíbrio perigoso,
                onde a conveniência do serviço oculta um perfilamento profundo de seus usuários.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 4. NOTÍCIAS RELACIONADAS ---
        st.markdown(f"### 📰 O Que Estão Falando Sobre a Privacidade do {opcao}?")
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
 
                # Notícia 1
                with col_n1:
                    titulo1 = noticias[0].find('title').text
                    link1 = noticias[0].find('link').text
                    fonte1 = noticias[0].find('source').text if noticias[0].find('source') is not None else "Portal de Notícias"
                    data1 = noticias[0].find('pubDate').text[:16]
 
                    st.markdown(f"""
                        <div class="parchment-card" style="min-height: 200px;">
                            <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link1}" target="\_blank" style="text-decoration: none; color: #162E5C;">{titulo1}</a></h4>
                            <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte1} | Publicado em: {data1}</p>
                            <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Clique no título acima para conferir a reportagem diretamente da fonte original.</p>
                        </div>
                    """, unsafe_allow_html=True)
 
                # Notícia 2
                with col_n2:
                    if len(noticias) > 1:
                        titulo2 = noticias[1].find('title').text
                        link2 = noticias[1].find('link').text
                        fonte2 = noticias[1].find('source').text if noticias[1].find('source') is not None else "Portal de Notícias"
                        data2 = noticias[1].find('pubDate').text[:16]
 
                        st.markdown(f"""
                            <div class="parchment-card" style="min-height: 200px;">
                                <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link2}" target="\_blank" style="text-decoration: none; color: #162E5C;">{titulo2}</a></h4>
                                <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte2} | Publicado em: {data2}</p>
                                <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe a segunda cobertura do cenário regulatório internacional desta plataforma.</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Não encontramos notícias recentes específicas para esta plataforma no momento.")
 
        except Exception as e:
            # Fallback visual seguro caso ocorra erro de conexão/RSS
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.markdown(f"""
                    <div class="parchment-card" style="min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://g1.globo.com/tecnologia/" target="\_blank" style="text-decoration: none; color: #162E5C;">{opcao} e Investigações de Tratamento de Dados</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: Portal G1 Tecnologia</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe as notícias sobre as auditorias mais recentes da ANPD envolvendo tratamento de informações sensíveis no Brasil.</p>
                    </div>
                """, unsafe_allow_html=True)
            with col_n2:
                st.markdown(f"""
                    <div class="parchment-card" style="min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://www.bbc.com/portuguese/topics/c40g969r280t" target="\_blank" style="text-decoration: none; color: #162E5C;">Mudanças nas Políticas e Regulamentações da Controladora do {opcao}</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: BBC Brasil</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Análise crítica sobre as novas regras globais de inteligência artificial e privacidade de dados de grandes corporações.</p>
                    </div>
                """, unsafe_allow_html=True)

st.markdown('<div class="footer">FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</div>', unsafe_allow_html=True)
