# ==========================================
# MODO 3: OPTIMIZER MA (MANUTENÇÃO ADITIVA)
# ==========================================
elif choice == menu[2]:
    st.header(menu[2])
    st.subheader("Otimização com Manutenção Aditiva (Mix de Peças)")
    st.write("Determine a combinação ótima entre peças tradicionais e impressas em 3D para minimizar custos, respeitando o risco alvo.")
    
    # Criar colunas para organizar os inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚙️ Peças Tradicionais")
        L_trad = st.number_input("Lambda Tradicional:", min_value=0.0000, value=0.05, step=0.01, format="%.6f", key="l_trad")
        T_trad = st.number_input("Tempo de reposição (t):", min_value=1, value=5, step=1, key="t_trad")
        C_trad = st.number_input("Custo Unitário (R$):", min_value=0.00, value=500.00, step=10.00, format="%.2f", key="c_trad")
        
    with col2:
        st.markdown("#### 🖨️ Peças Impressas em 3D")
        L_3d = st.number_input("Lambda 3D (maior fragilidade):", min_value=0.0000, value=0.08, step=0.01, format="%.6f", key="l_3d")
        T_3d = st.number_input("Tempo de impressão (t):", min_value=1, value=1, step=1, key="t_3d")
        C_3d = st.number_input("Custo de Impressão (R$):", min_value=0.00, value=100.00, step=10.00, format="%.2f", key="c_3d")
        
    st.divider()
    st.markdown("#### 📊 Parâmetros Globais do Sistema")
    col3, col4, col5 = st.columns(3)
    with col3:
        N_maq = st.number_input("Número de máquinas ativas (n):", min_value=1, value=10, step=1, key="n_maq_ma")
    with col4:
        R_PCT_MA = st.number_input("Risco Alvo (%):", min_value=0.01, max_value=99.99, value=5.00, step=1.0, format="%.2f", key="r_pct_ma")
    with col5:
        # Novo campo para evitar o travamento!
        limite_busca = st.number_input("Limite máx. de peças testadas:", min_value=10, value=150, step=10, help="Limita o processamento para não travar o sistema. Aumente se não achar solução.")

    st.subheader("Clique no botão abaixo para calcular o Mix Ótimo:")    
    botao_ma = st.button("Calcular Mix Ótimo MA")

    if botao_ma:
        risco_alvo = R_PCT_MA / 100.0
        
        melhor_custo = float('inf')
        melhor_mix = None
        melhor_risco = 1.0
        melhor_m = 0.0
        
        # Colocamos um "spinner" visual para você saber que ele está calculando e não travou
        with st.spinner('Processando milhares de combinações...'):
            custo_minimo_possivel = min(C_trad, C_3d)
            
            # Substituímos o while True pelo limite seguro definido no input
            for total_pecas in range(1, int(limite_busca) + 1):
                
                # Se já achamos uma combinação onde a peça mais barata possível 
                # multiplicada pelo total já é mais cara que o melhor achado, paramos.
                if total_pecas * custo_minimo_possivel >= melhor_custo:
                    break
                    
                for x_trad in range(total_pecas + 1):
                    x_3d = total_pecas - x_trad
                    custo_atual = (x_trad * C_trad) + (x_3d * C_3d)
                    
                    if custo_atual >= melhor_custo:
                        continue
                        
                    prop_trad = x_trad / total_pecas
                    prop_3d = x_3d / total_pecas
                    
                    m_trad_puro = L_trad * N_maq * T_trad
                    m_3d_puro = L_3d * N_maq * T_3d
                    m_equivalente = (prop_trad * m_trad_puro) + (prop_3d * m_3d_puro)
                    
                    prob_acumulada = poisson.cdf(total_pecas, m_equivalente)
                    risco_atual = max(1.0 - prob_acumulada, 0.0)
                    
                    if risco_atual <= risco_alvo:
                        melhor_custo = custo_atual
                        melhor_mix = (x_trad, x_3d)
                        melhor_risco = risco_atual
                        melhor_m = m_equivalente

        # Apresentação dos Resultados Visuais
        if melhor_mix is not None:
            st.success("✅ Combinação ótima encontrada com sucesso!")
            
            st.subheader("Resultados da Otimização")
            res_col1, res_col2, res_col3 = st.columns(3)
            
            res_col1.metric("Peças Tradicionais", f"{melhor_mix[0]} unid.")
            res_col2.metric("Peças 3D (Aditivas)", f"{melhor_mix[1]} unid.")
            res_col3.metric("Total de Peças", f"{melhor_mix[0] + melhor_mix[1]} unid.")
            
            st.divider()
            
            indicadores_col1, indicadores_col2, indicadores_col3 = st.columns(3)
            indicadores_col1.metric("Valor Esperado Falhas (m ponderado)", f"{melhor_m:.2f}")
            indicadores_col2.metric("Risco Obtido", f"{melhor_risco:.4%}")
            indicadores_col3.metric("Custo Total Mínimo", f"R$ {melhor_custo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            df_resultado = pd.DataFrame({
                "Tipo": ["Tradicional", "Impressão 3D"],
                "Quantidade": [melhor_mix[0], melhor_mix[1]],
                "Custo Unitário (R$)": [C_trad, C_3d],
                "Subtotal (R$)": [melhor_mix[0] * C_trad, melhor_mix[1] * C_3d]
            })
            st.dataframe(df_resultado, use_container_width=True, hide_index=True)
            
        else:
            st.error(f"❌ Não foi possível encontrar uma solução segura testando até {limite_busca} peças no total. Tente aumentar o limite de busca ou alterar os parâmetros.")
