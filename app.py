if st.button("Testar conexão com banco"):
    try:
        conn = get_conn()
        conn.close()
        st.success("Conexão OK com SQLiteCloud.")
    except Exception as e:
        st.error(f"Falha de conexão: {e}")
