import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="Réseaux de Petri", layout="wide", page_icon="🕸️")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🕸️ TP Modélisation : Réseaux de Petri</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- القسم الأول: الأبعاد ---
st.markdown("### ⚙️ 1. Configuration des Dimensions")
col1, col2 = st.columns(2) 
with col1:
    P = st.number_input("🟢 Nombre de Places (P)", min_value=1, value=3, step=1)
with col2:
    T = st.number_input("⬛ Nombre de Transitions (T)", min_value=1, value=2, step=1)

places_labels = [f"P{i+1}" for i in range(P)]
trans_labels = [f"T{i+1}" for i in range(T)]

# --- القسم الثاني: إدخال المصفوفات ---
st.markdown("---")
st.markdown("### 📊 2. Saisie des Matrices")
st.info("📱 **Sur mobile :** Touchez une case pour ouvrir le pavé numérique. Laissez vide pour '0'.")

# إعدادات مخصصة لإجبار الهاتف على فتح لوحة الأرقام
num_config = st.column_config.NumberColumn(
    "Valeur", min_value=0, step=1, format="%d"
)
config_dict = {col: num_config for col in trans_labels}
config_dict_is = {"Valeur": num_config}

col_m1, col_m2 = st.columns(2)

with col_m1:
    st.write("**🔽 Matrice $M_1$ (Pre)**")
    df_m1_init = pd.DataFrame(0, index=places_labels, columns=trans_labels, dtype=int)
    # استخدام data_editor
    df_m1_raw = st.data_editor(df_m1_init, key=f"m1_{P}_{T}", use_container_width=True, column_config=config_dict)
    # ✨ الحل الجذري لمشكلة الـ NaN (تحويل الفراغات إلى 0 فوراً)
    df_m1 = df_m1_raw.fillna(0).astype(int)

with col_m2:
    st.write("**🔼 Matrice $M_2$ (Post)**")
    df_m2_init = pd.DataFrame(0, index=places_labels, columns=trans_labels, dtype=int)
    df_m2_raw = st.data_editor(df_m2_init, key=f"m2_{P}_{T}", use_container_width=True, column_config=config_dict)
    # ✨ الحل الجذري لمشكلة الـ NaN
    df_m2 = df_m2_raw.fillna(0).astype(int)

m1_np = df_m1.values
m2_np = df_m2.values

# --- القسم الثالث: مصفوفة M3 ---
st.markdown("---")
st.markdown("### 🧮 3. Matrice d'Incidence $M_3$ ($M_2 - M_1$)")

m3_np = m2_np - m1_np
df_m3 = pd.DataFrame(m3_np, index=places_labels, columns=trans_labels, dtype=int)

def color_cells(val):
    bg_color = '#ffe6e6' if val < 0 else ('#e6ffe6' if val > 0 else '#f8f9fa')
    text_color = '#cc0000' if val < 0 else ('#008000' if val > 0 else '#6c757d')
    return f'background-color: {bg_color}; color: {text_color}; font-weight: bold; text-align: center;'

st.dataframe(df_m3.style.map(color_cells), use_container_width=True)

# --- القسم الرابع: العلامة الابتدائية وشعاع S ---
st.markdown("---")
st.markdown("### 🎯 4. Marquage Initial et Séquence")
col_i, col_s = st.columns(2)

with col_i:
    st.write("**🟢 Marquage Initial ($i$)**")
    df_i_init = pd.DataFrame(0, index=places_labels, columns=["Valeur"], dtype=int)
    df_i_raw = st.data_editor(df_i_init, key=f"i_{P}_{T}", use_container_width=True, column_config=config_dict_is)
    df_i = df_i_raw.fillna(0).astype(int)

with col_s:
    st.write("**⬛ Vecteur $S$ (Algébrique)**")
    df_s_init = pd.DataFrame(0, index=trans_labels, columns=["Valeur"], dtype=int)
    df_s_raw = st.data_editor(df_s_init, key=f"s_{P}_{T}", use_container_width=True, column_config=config_dict_is)
    df_s = df_s_raw.fillna(0).astype(int)

i_np = df_i.values.flatten()
s_np = df_s.values.flatten()

# --- القسم الخامس: العمليات والمحاكاة ---
st.markdown("---")
st.markdown("### 🚀 5. Actions et Simulation")

tab1, tab2, tab3 = st.tabs(["🧮 Calcul Algébrique", "🔍 Franchissabilité", "🎬 Simulation"])

with tab1:
    st.markdown("#### Équation d'état : $K = i + M_3 \cdot S$")
    if st.button("🔢 Lancer le Calcul ($K$)", use_container_width=True):
        k_np = i_np + np.dot(m3_np, s_np)
        df_k = pd.DataFrame(k_np, index=places_labels, columns=["Résultat $K$"], dtype=int)
        st.dataframe(df_k.style.map(lambda _: 'background-color: #e3f2fd; font-weight: bold; text-align: center;'), use_container_width=True)

with tab2:
    if st.button("✅ Vérifier les transitions franchissables (au marquage $i$)", use_container_width=True):
        franchissables = []
        for t_idx in range(T):
            if np.all(i_np >= m1_np[:, t_idx]):
                franchissables.append(f"T{t_idx+1}")
                
        if franchissables:
            st.success(f"🎉 Transitions franchissables : **{', '.join(franchissables)}**")
        else:
            st.error("🛑 Aucune transition n'est franchissable (Blocage).")

with tab3:
    st.info("📱 Tapez les numéros séparés par des virgules (ex: 1, 2, 1)")
    seq_str = st.text_input("Séquence :", placeholder="1, 2")
    
    if st.button("▶️ Démarrer la Simulation", type="primary", use_container_width=True):
        if not seq_str.strip():
            st.warning("⚠️ Veuillez entrer une séquence.")
        else:
            try:
                # تنظيف مرن للبيانات يقبل الفواصل والمسافات العشوائية
                raw_seq = [x.strip() for x in seq_str.replace("T", "").replace("t", "").split(",") if x.strip()]
                sequence = [int(x) - 1 for x in raw_seq]
                
                if not sequence:
                    st.warning("⚠️ Séquence invalide.")
                else:
                    marking = i_np.copy()
                    st.write(f"**$M_0$** = `{marking.tolist()}`")
                    
                    success = True
                    for step, t in enumerate(sequence):
                        if t < 0 or t >= T:
                            st.error(f"❌ La transition **$T_{t+1}$** n'existe pas.")
                            success = False
                            break
                            
                        if np.all(marking >= m1_np[:, t]):
                            marking = marking + m3_np[:, t]
                            st.success(f"✅ **$T_{t+1}$** ➔ **$M_{step+1}$** = `{marking.tolist()}`")
                        else:
                            st.error(f"🛑 **ÉCHEC** : **$T_{t+1}$** NON franchissable au marquage `{marking.tolist()}`")
                            success = False
                            break
                            
                    if success:
                        st.balloons()
                        
            except ValueError:
                st.error("⚠️ Format invalide. Utilisez uniquement des chiffres et des virgules.")

