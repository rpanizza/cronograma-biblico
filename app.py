st.title("📜 Cronograma Profético Bíblico")

    # --- NOVO: Layout dos Botões no Canto Superior Direito ---
    # Cria colunas: uma larga para preencher o espaço e duas estreitas para os botões.
    col_spacer, col_login, col_share = st.columns([12, 1.5, 1]) 
    
    with col_login:
        # Usamos st.button() com um label conciso. 
        # A chave 'login_button' evita problemas de chave duplicada no Streamlit.
        if st.button("🔑 Login", key='login_button'):
            st.session_state.page = 'login' 
            st.experimental_rerun()
            
    with col_share:
        # Botão de Compartilhar usando apenas ícone para ser minimalista:
        # 🔗 = Ícone de Link ou 📤 = Ícone de Compartilhamento. Usaremos o de link para clareza.
        if st.button("🔗", key='share_button'):
            st.toast("Link de compartilhamento copiado para a área de transferência! (Simulado)")
            
    # Linha Horizontal para separar o cabeçalho do conteúdo
    st.markdown("---")
    
    # ... (O restante da função show_dashboard, começando por st.subheader("A Linha do Tempo..."))
