import streamlit as st
import numpy as np
import pandas as pd

# إعدادات الصفحة
st.set_page_config(
    page_title="TP Modélisation et Simulation - Réseaux de Petri",
    page_icon="🌐",
    layout="wide"
)

# عنوان التطبيق
st.title("🌐 TP Modélisation et Simulation - Réseaux de Petri")
st.markdown("---")

# --- القائمة الجانبية لإدخال الأبعاد ---
st.sidebar.header("⚙️ Configuration du Réseau")
P = st.sidebar.number_input("Nombre de Places (P):", min_value=1, value=3, step=1)
T = st.sidebar.number_input("Nombre de Transitions (T):", min_value=1, value=2, step=1)

# تسميات تلقائية لصفوف المصفوفات وأعمدتها
place_labels = [f"P{i+1}" for i in range(P)]
transition_labels = [f"T{j+1}" for j in range(T)]

# --- القسم الأول: إدخال المصفوفات وحساب M3 ---
st.header("1. Matrices d'Incidence")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Matrice M1 (Pre)")
    # جدول تفاعلي لإدخال قيم M1
    m1_df = st.data_editor(
        pd.DataFrame(0, index=place_labels, columns=transition_labels), 
        key="m1_input"
    )

with col2:
    st.subheader("Matrice M2 (Post)")
    # جدول تفاعلي لإدخال قيم M2
    m2_df = st.data_editor(
        pd.DataFrame(0, index=place_labels, columns=transition_labels), 
        key="m2_input"
    )

# تحويل البيانات المدخلة إلى مصفوفات Numpy للحساب الاستدلالي
M1 = m1_df.to_numpy()
M2 = m2_df.to_numpy()
M3 = M2 - M1

# عرض مصفوفة Incidence M3 مع تلوين الخلايا تلقائياً بناءً على قيمها
st.subheader("Matrice d'Incidence M3 (M2 - M1)")
m3_df = pd.DataFrame(M3, index=place_labels, columns=transition_labels)

def color_cells(val):
    if val < 0:
        return 'background-color: #e74c3c; color: white; font-weight: bold;'
    elif val > 0:
        return 'background-color: #2ecc71; color: white; font-weight: bold;'
    return 'background-color: #95a5a6; color: white;'

st.dataframe(m3_df.style.applymap(color_cells), use_container_width=True)

st.markdown("---")

# --- القسم الثاني: العلامات المتجهة والحسابات ---
st.header("2. Marquage et Vecteurs")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Marquage Initial ($i$ / $M_0$)")
    i_df = st.data_editor(
        pd.DataFrame(0, index=place_labels, columns=["Marquage"]), 
        key="i_input"
    )
    i_vec = i_df["Marquage"].to_numpy()

with col4:
    st.subheader("Vecteur S (Algébrique)")
    s_df = st.data_editor(
        pd.DataFrame(0, index=transition_labels, columns=["Tours"]), 
        key="s_input"
    )
    s_vec = s_df["Tours"].to_numpy()

# أزرار التحكم والعمليات الحسابية
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📊 Calcul Algébrique (K)", type="primary", use_container_width=True):
        # المعادلة الرياضية: K = i + M3 * S
        dot_product = np.dot(M3, s_vec)
        K = i_vec + dot_product
        
        st.success("Résultat de l'Équation d'état K :")
        k_df = pd.DataFrame(K, index=place_labels, columns=["Nouveau Marquage K"])
        st.table(k_df)

with col_btn2:
    if st.button("🔍 Afficher Franchissables", use_container_width=True):
        franchissables = []
        for t_idx in range(T):
            # شرط العبور: أن تكون علامات الأماكن أكبر أو تساوي مصفوفة Pre
            if all(i_vec[p] >= M1[p, t_idx] for p in range(P)):
                franchissables.append(f"T{t_idx+1}")
                
        if franchissables:
            st.success(f"Transitions franchissables au marquage actuel : **{', '.join(franchissables)}**")
        else:
            st.error("Aucune transition franchissable !")

st.markdown("---")

# --- القسم الثالث: محاكاة السلاسل ---
st.header("3. Simulation de Séquence S")
seq_str = st.text_input("Séquence d'entrée (ex: 1,2,1 pour T1 -> T2 -> T1):", value="1,2")

if st.button("🚀 Simuler Séquence", use_container_width=True):
    if not seq_str.strip():
        st.warning("Veuillez entrer une séquence.")
    else:
        try:
            # تنظيف السلسلة وتحويلها لفهارس برمجية
            raw_seq = seq_str.replace("T", "").replace("t", "").split(",")
            sequence = [int(x.strip()) - 1 for x in raw_seq]
            
            # التحقق من صحة أرقام الانتقالات
            valid = True
            for t in sequence:
                if t < 0 or t >= T:
                    st.error(f"La transition T{t+1} n'existe pas.")
                    valid = False
                    break
            
            if valid:
                current_marking = i_vec.copy()
                st.write(f"**Marquage Initial $M_0$ :** `{list(current_marking)}`")
                
                # تنفيذ المحاكاة خطوة بخطوة
                for step, t in enumerate(sequence):
                    if all(current_marking[p] >= M1[p, t] for p in range(P)):
                        current_marking += M3[:, t]
                        st.info(f"✅ **Étape {step+1}:** T{t+1} franchie. ➡️ `M{step+1} = {list(current_marking)}`")
                    else:
                        st.error(f"❌ **Étape {step+1}:** ÉCHEC : T{t+1} NON franchissable à ce stade !")
                        break
        except ValueError:
            st.error("Format de séquence invalide. Utilisez des nombres séparés par des virgules (ex: 1,2)")
