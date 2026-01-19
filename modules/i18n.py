import streamlit as st

# UI Translations Dictionary
STRINGS = {
    "en": {
        "app_title": "AI Security Maturity Assessment",
        "app_subtitle": "NIST AI RMF mapped to CSA AICM Controls",
        "sidebar_settings": "Application Settings",
        "lang_selector": "Interface Language",
        "dashboard_tab": "Executive Dashboard",
        "assessment_tab": "Assessment",
        "evidence_tab": "Evidence Locker",
        "evidence_subtitle": "Upload documents to enable AI Auto-Assessment",
        "roi_tab": "ROI Calculator",
        "save_btn": "💾 Save & Download Report",
        "auto_assess": "✨ Auto-Assess",
        "analyze": "🚀 Analyze",
        "clone_btn": "📋 Clone as New Scenario",
        "draft_mode": "Draft Mode",
        "draft_desc": "You are drafting a new scenario based on historical data from {project}.",
        "cancel_draft": "✖️ Cancel Draft & Clear Data",
        "nist_govern": "Cultivate a culture of risk management.",
        "nist_map": "Context recognized and risks identified.",
        "nist_measure": "Assessed, analyzed, and tracked.",
        "nist_manage": "Prioritize and act upon risks.",
        "nist_csa": "Additional CSA AICM requirements.",
        "maturity_foundation": "1. Foundation & Governance",
        "maturity_security": "2. Security & Verification",
        "maturity_ops": "3. Operations & Optimization",
        "tab_enterprise": "🏛️ Enterprise",
        "tab_cloud": "☁️ Solutions Cloud",
        "tab_saas": "📦 Solutions SaaS",
        "journey_header": "Maturity Journey Phase",
        "all_waves": "All Waves",
        "phase_label": "Current Phase",
        "progress_label": "Progress",
        "project_name_label": "Project / Product Name",
        "project_name_placeholder": "e.g. Finance Chatbot v2"
    },
    "pt": {
        "app_title": "Avaliação de Maturidade em Segurança de IA",
        "app_subtitle": "NIST AI RMF mapeado para Controles CSA AICM",
        "sidebar_settings": "Configurações do Aplicativo",
        "lang_selector": "Idioma da Interface",
        "dashboard_tab": "Dashboard Executivo",
        "assessment_tab": "Avaliação",
        "evidence_tab": "Repositório de Evidências",
        "evidence_subtitle": "Carregue documentos para habilitar a Auto-Avaliação por IA",
        "roi_tab": "Calculadora de ROI",
        "save_btn": "💾 Salvar e Baixar Relatório",
        "auto_assess": "✨ Auto-Avaliação",
        "analyze": "🚀 Analisar",
        "clone_btn": "📋 Clonar como Novo Cenário",
        "draft_mode": "Modo Rascunho",
        "draft_desc": "Você está criando um novo cenário baseado em dados históricos de {project}.",
        "cancel_draft": "✖️ Cancelar Rascunho e Limpar Dados",
        "nist_govern": "Cultivar uma cultura de gestão de riscos.",
        "nist_map": "Contexto reconhecido e riscos identificados.",
        "nist_measure": "Avaliado, analisado e monitorado.",
        "nist_manage": "Priorizar e agir sobre os riscos.",
        "nist_csa": "Requisitos adicionais do CSA AICM.",
        "maturity_foundation": "1. Fundação e Governança",
        "maturity_security": "2. Segurança e Verificação",
        "maturity_ops": "3. Operações e Otimização",
        "tab_enterprise": "🏛️ Corporativo",
        "tab_cloud": "☁️ Cloud (Cloud Solutions)",
        "tab_saas": "📦 SaaS (SaaS Solutions)",
        "journey_header": "Fase da Jornada de Maturidade",
        "all_waves": "Todas as Fases",
        "phase_label": "Fase Atual",
        "progress_label": "Progresso",
        "project_name_label": "Nome do Projeto / Produto",
        "project_name_placeholder": "ex: Chatbot Financeiro v2"
    }
}

def get_lang():
    return st.session_state.get('lang', 'en')

def t(key, **kwargs):
    lang = get_lang()
    text = STRINGS.get(lang, STRINGS['en']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
