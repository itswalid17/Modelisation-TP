import streamlit as st
import pandas as pd
import numpy as np

# 1. إعدادات الصفحة (توسيع الشاشة لراحة أكبر)
st.set_page_config(page_title="Réseaux de Petri", layout="wide", page_icon="🕸️")

# --- العنوان الرئيسي ---
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🕸️ TP Modélisation et Simulation : Réseaux de Petri</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- القسم الأول: الأبعاد ---
st.markdown("### ⚙️ 1. Configuration des Dimensions")
col1, col2, col3 = st.columns([1, 1, 2]) 
with col1:
    P = st.number_input("🟢 Nombre de Places (P)", min_value=1, value=3, step=1)
with col2:
    T = st.number_input("⬛ Nombre de Transitions (T)", min_value=1, value=2, step=1)

# توليد أسماء الأماكن والانتقالات
places_labels = [f"P{i+1}" for i in range(P)]
trans_labels = [f"T{i+1}" for i in range(T)]

# --- القسم الثاني: إدخال المصفوفات ---
st.markdown("---")
st.markdown("### 📊 2. Saisie des Matrices")
st.info("💡 **Astuce :** Cliquez sur les cellules pour modifier les valeurs. Vous pouvez utiliser les flèches du clavier pour naviguer rapidement !")

# إعدادات الأعمدة لضمان إدخال أرقام صحيحة فقط
num_config = st.column_config.NumberColumn(min_value=0, step=1, format="%d")
config_dict = {col: num_config for col in trans_labels}
config_dict_is = {"Valeur": num_config}

col_m1, col_m2 = st.columns(2)

# إصلاح المشكلة: إضافة (P و T) إلى الـ Key لمنع تداخل أبعاد المصفوفات عند تغييرها
with col_m1:
    st.write("**🔽 Matrice M1 (Pre)**")
    df_m1_init = pd.DataFrame(0, index=places_labels, columns=trans_labels, dtype=int)
    df_m1 = st.data_editor(df_m1_init, key=f"m1_{P}_{T}", use_container_width=True, column_config=config_dict)

with col_m2:
    st.write("**🔼 Matrice M2 (Post)**")
    df_m2_init = pd.DataFrame(0, index=places_labels, columns=trans_labels, dtype=int)
    df_m2 = st.data_editor(df_m2_init, key=f"m2_{P}_{T}", use_container_width=True, column_config=config_dict)

m1_np = df_m1.values
m2_np = df_m2.values

# --- القسم الثالث: مصفوفة M3 ---
st.markdown("---")
st.markdown("### 🧮 3. Matrice d'Incidence M3 (M2 - M1)")

m3_np = m2_np - m1_np
df_m3 = pd.DataFrame(m3_np, index=places_labels, columns=trans_labels, dtype=int)

# دالة تلوين محسنة لراحة العين
def color_cells(val):
    bg_color = '#ffe6e6' if val < 0 else ('#e6ffe6' if val > 0 else '#f8f9fa')
    text_color = '#cc0000' if val < 0 else ('#008000' if val > 0 else '#6c757d')
    return f'background-color: {bg_color}; color: {text_color}; font-weight: bold; text-align: center;'

st.dataframe(df_m3.style.map(color_cells), use_container_width=True)

# --- القسم الرابع: العلامة الابتدائية وشعاع S ---
st.markdown("---")
st.markdown("### 🎯 4. Marquage Initial et Séquence Algébrique")
col_i, col_s = st.columns(2)

with col_i:
    st.write("**🟢 Marquage Initial (i)**")
    df_i_init = pd.DataFrame(0, index=places_labels, columns=["Valeur"], dtype=int)
    df_i = st.data_editor(df_i_init, key=f"i_{P}_{T}", use_container_width=True, column_config=config_dict_is)

with col_s:
    st.write("**⬛ Vecteur S (Algébrique)**")
    df_s_init = pd.DataFrame(0, index=trans_labels, columns=["Valeur"], dtype=int)
    df_s = st.data_editor(df_s_init, key=f"s_{P}_{T}", use_container_width=True, column_config=config_dict_is)

i_np = df_i.values.flatten()
s_np = df_s.values.flatten()

# --- القسم الخامس: العمليات والمحاكاة ---
st.markdown("---")
st.markdown("### 🚀 5. Actions et Simulation")

tab1, tab2, tab3 = st.tabs(["🧮 Calcul Algébrique", "🔍 Franchissabilité", "🎬 Simulation de Séquence"])

with tab1:
    st.markdown("#### Équation d'état : K = i + M3 · S")
    if st.button("🔢 Lancer le Calcul Algébrique (K)", use_container_width=True):
        k_np = i_np + np.dot(m3_np, s_np)
        df_k = pd.DataFrame(k_np, index=places_labels, columns=["Résultat K"], dtype=int)
        st.dataframe(df_k.style.map(lambda _: 'background-color: #e3f2fd; font-weight: bold; text-align: center;'), use_container_width=True)

with tab2:
    st.markdown("#### Vérification au marquage initial (i)")
    if st.button("✅ Afficher les transitions franchissables", use_container_width=True):
        franchissables = []
        for t_idx in range(T):
            if np.all(i_np >= m1_np[:, t_idx]):
                franchissables.append(f"T{t_idx+1}")
                
        if franchissables:
            st.success(f"🎉 Transitions franchissables : **{', '.join(franchissables)}**")
        else:
            st.error("🛑 Aucune transition n'est franchissable (Blocage / Deadlock).")

with tab3:
    st.markdown("#### Simuler une exécution pas-à-pas")
    seq_str = st.text_input("Saisissez la séquence (ex: 1, 2, 1) :", placeholder="1, 2, 1")
    
    if st.button("▶️ Démarrer la Simulation", type="primary", use_container_width=True):
        if not seq_str.strip():
            st.warning("⚠️ Veuillez entrer une séquence valide pour commencer.")
        else:
            try:
                # إصلاح: تنظيف الإدخال لمنع الأخطاء في حال إدخال فواصل زائدة
                raw_seq = [x.strip() for x in seq_str.replace("T", "").replace("t", "").split(",") if x.strip()]
                sequence = [int(x) - 1 for x in raw_seq]
                
                if not sequence:
                    st.warning("⚠️ La séquence saisie n'est pas valide.")
                else:
                    marking = i_np.copy()
                    st.info(f"**Marquage de départ M0** = {marking.tolist()}")
                    
                    success = True
                    with st.container():
                        for step, t in enumerate(sequence):
                            if t < 0 or t >= T:
                                st.error(f"❌ La transition **T{t+1}** n'existe pas dans le réseau.")
                                success = False
                                break
                                
                            if np.all(marking >= m1_np[:, t]):
                                marking = marking + m3_np[:, t]
                                st.success(f"✅ **T{t+1} franchie** ➔ Nouveau marquage **M{step+1}** = {marking.tolist()}")
                            else:
                                st.error(f"🛑 **ÉCHEC** : La transition **T{t+1}** NON franchissable au marquage {marking.tolist()}!")
                                success = False
                                break
                        
                    if success:
                        st.balloons()
                        
            except ValueError:
                st.error("⚠️ Format de séquence invalide. Utilisez des nombres séparés par des virgules (ex: 1,2)")
                
