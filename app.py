import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="TP Réseaux de Petri", layout="centered")

st.title("TP Modélisation et Simulation")
st.subheader("Réseaux de Petri")

# --- الجزء العلوي: الإعدادات ---
st.markdown("### Dimensions du Réseau")
col1, col2 = st.columns(2)
P = col1.number_input("Places (P):", min_value=1, value=3, step=1)
T = col2.number_input("Transitions (T):", min_value=1, value=2, step=1)

places_labels = [f"P{i+1}" for i in range(P)]
trans_labels = [f"T{i+1}" for i in range(T)]

# --- الجزء الأول: Matrices M1 و M2 ---
st.markdown("---")
st.markdown("### 1. Matrices $M_1$ (Pre) et $M_2$ (Post)")

# إضافة خيار لاختيار واجهة الإدخال المناسبة للجهاز
saisie_mode = st.radio(
    "🖥️📱 Mode de saisie (اختر طريقة الإدخال):", 
    ["Tableau (PC)", "Liste Verticale (Mobile)"], 
    horizontal=True
)

# تهيئة المصفوفات مسبقاً
m1_np = np.zeros((P, T), dtype=int)
m2_np = np.zeros((P, T), dtype=int)

if saisie_mode == "Tableau (PC)":
    st.info("Modifiez les valeurs directement dans les tableaux ci-dessous.")
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.write("**Matrice $M_1$ (Pre)**")
        df_m1_init = pd.DataFrame(0, index=places_labels, columns=trans_labels)
        df_m1 = st.data_editor(df_m1_init, key="m1", use_container_width=True)

    with col_m2:
        st.write("**Matrice $M_2$ (Post)**")
        df_m2_init = pd.DataFrame(0, index=places_labels, columns=trans_labels)
        df_m2 = st.data_editor(df_m2_init, key="m2", use_container_width=True)
    
    m1_np = df_m1.values
    m2_np = df_m2.values

else: # Mode Mobile
    st.info("Saisissez les poids via les menus déroulants (idéal pour les écrans tactiles).")
    tab_m1, tab_m2 = st.tabs(["M1 (Pre-conditions)", "M2 (Post-conditions)"])
    
    with tab_m1:
        for j, t in enumerate(trans_labels):
            with st.expander(f"Poids de {t} (Matrice M1)"):
                for i, p in enumerate(places_labels):
                    # الإدخال العمودي المخصص للهواتف
                    m1_np[i, j] = st.number_input(f"{p} $\\rightarrow$ {t}", min_value=0, value=0, step=1, key=f"m1_mob_{i}_{j}")
                    
    with tab_m2:
        for j, t in enumerate(trans_labels):
            with st.expander(f"Poids de {t} (Matrice M2)"):
                for i, p in enumerate(places_labels):
                    m2_np[i, j] = st.number_input(f"{t} $\\rightarrow$ {p}", min_value=0, value=0, step=1, key=f"m2_mob_{i}_{j}")

# --- الجزء الثاني: حساب M3 ---
st.markdown("---")
st.markdown("### 2. Matrice d'Incidence $M_3$ ($M_2 - M_1$)")

m3_np = m2_np - m1_np
df_m3 = pd.DataFrame(m3_np, index=places_labels, columns=trans_labels)

def color_cells(val):
    color = '#e74c3c' if val < 0 else ('#2ecc71' if val > 0 else 'transparent')
    return f'background-color: {color}; color: white' if color != 'transparent' else ''

st.dataframe(df_m3.style.map(color_cells), use_container_width=True)

# --- الجزء الثالث: العلامة الابتدائية وشعاع S ---
st.markdown("---")
st.markdown("### Vecteurs de Marquage et Algébrique")

i_np = np.zeros(P, dtype=int)
s_np = np.zeros(T, dtype=int)

if saisie_mode == "Tableau (PC)":
    col_i, col_s = st.columns(2)
    with col_i:
        st.write("**Marquage Initial ($i$)**")
        df_i_init = pd.DataFrame(0, index=places_labels, columns=["Valeur"])
        df_i = st.data_editor(df_i_init, key="i", use_container_width=True)
        i_np = df_i.values.flatten()

    with col_s:
        st.write("**Vecteur $S$ (Algébrique)**")
        df_s_init = pd.DataFrame(0, index=trans_labels, columns=["Valeur"])
        df_s = st.data_editor(df_s_init, key="s", use_container_width=True)
        s_np = df_s.values.flatten()
else:
    tab_i, tab_s = st.tabs(["Marquage Initial ($i$)", "Vecteur $S$"])
    with tab_i:
        for i, p in enumerate(places_labels):
            i_np[i] = st.number_input(f"Jetons dans {p}", min_value=0, value=0, step=1, key=f"i_mob_{i}")
    with tab_s:
        for j, t in enumerate(trans_labels):
            s_np[j] = st.number_input(f"Activation de {t}", min_value=0, value=0, step=1, key=f"s_mob_{j}")

# --- الجزء الرابع: العمليات والمحاكاة ---
st.markdown("---")
st.markdown("### 3. Actions et Simulation")

tab1, tab2, tab3 = st.tabs(["Calcul Algébrique ($K$)", "Transitions Franchissables", "Simulation de Séquence"])

with tab1:
    st.write("Équation d'état : $K = i + M_3 \cdot S$")
    if st.button("Calculer $K$", type="primary"):
        k_np = i_np + np.dot(m3_np, s_np)
        df_k = pd.DataFrame(k_np, index=places_labels, columns=["Résultat $K$"])
        st.dataframe(df_k.style.map(color_cells), use_container_width=True)

with tab2:
    if st.button("Afficher les transitions franchissables au marquage $i$"):
        franchissables = []
        for t_idx in range(T):
            if np.all(i_np >= m1_np[:, t_idx]):
                franchissables.append(f"T{t_idx+1}")
                
        if franchissables:
            st.success(f"Transitions franchissables : **{', '.join(franchissables)}**")
        else:
            st.error("Aucune transition franchissable à ce stade.")

with tab3:
    seq_str = st.text_input("Séquence (ex: 1,2,1 pour $T_1 \\rightarrow T_2 \\rightarrow T_1$):")
    if st.button("Simuler la séquence"):
        if not seq_str.strip():
            st.warning("Veuillez entrer une séquence valide.")
        else:
            try:
                raw_seq = seq_str.replace("T", "").replace("t", "").split(",")
                sequence = [int(x.strip()) - 1 for x in raw_seq]
                
                marking = i_np.copy()
                st.write(f"**$M_0$** = {marking.tolist()}")
                
                success = True
                for step, t in enumerate(sequence):
                    if t < 0 or t >= T:
                        st.error(f"❌ La transition $T_{t+1}$ n'existe pas.")
                        success = False
                        break
                        
                    if np.all(marking >= m1_np[:, t]):
                        marking = marking + m3_np[:, t]
                        st.success(f"✅ $T_{t+1}$ franchie.  **$M_{step+1}$** = {marking.tolist()}")
                    else:
                        st.error(f"❌ ÉCHEC : $T_{t+1}$ NON franchissable à ce stade!")
                        success = False
                        break
                
                if success:
                    st.balloons()
                    
            except ValueError:
                st.error("Format de séquence invalide. Utilisez des nombres séparés par des virgules (ex: 1,2)")
                
