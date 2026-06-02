import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TP Réseaux de Petri", layout="centered", page_icon="🕸️")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>TP Modélisation et Simulation : Réseaux de Petri</h2>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 1. إعدادات الأبعاد
# ==========================================
st.markdown("### ⚙️ 1. Paramètres (Dimensions)")
col_p, col_t = st.columns(2)
with col_p:
    P = st.number_input("Nombre de Places (P)", min_value=1, value=3, step=1, key="P")
with col_t:
    T = st.number_input("Nombre de Transitions (T)", min_value=1, value=2, step=1, key="T")

st.markdown("---")

# ==========================================
# دالة بناء المصفوفات بإحداثيات واضحة رياضياً
# ==========================================
def create_matrix_input(name, rows, cols, row_prefix, col_prefix):
    grid_data = []
    for r in range(rows):
        # إنشاء أعمدة لكل صف
        cols_ui = st.columns(cols)
        row_data = []
        for c in range(cols):
            with cols_ui[c]:
                # تحديد الإحداثيات بدقة (مثال: P1, T1) لكي لا يضيع المستخدم
                if col_prefix:
                    cell_label = f"[{row_prefix}{r+1}, {col_prefix}{c+1}]"
                else:
                    cell_label = f"{row_prefix}{r+1}"
                
                val = st.number_input(
                    label=cell_label, 
                    value=0, 
                    step=1, 
                    key=f"{name}_{r}_{c}"
                )
                row_data.append(int(val))
        grid_data.append(row_data)
        # فاصل بصري خفيف بين الصفوف لتسهيل القراءة
        st.write("") 
    return grid_data

# ==========================================
# 2. إدخال المصفوفات M1 و M2
# ==========================================
st.markdown("### 📊 2. Matrices M1 (Pre) et M2 (Post)")
st.info("📱 Les indices [P, T] indiquent la Ligne (Place) et la Colonne (Transition).")

col_m1, space, col_m2 = st.columns([1, 0.1, 1])

with col_m1:
    st.markdown("<h5 style='color: #2980b9;'>Matrice M1 (Pre)</h5>", unsafe_allow_html=True)
    m1_data = create_matrix_input("m1", P, T, "P", "T")

with col_m2:
    st.markdown("<h5 style='color: #8e44ad;'>Matrice M2 (Post)</h5>", unsafe_allow_html=True)
    m2_data = create_matrix_input("m2", P, T, "P", "T")

st.markdown("---")

# ==========================================
# 3. حساب وعرض M3 بشكل رياضي دقيق
# ==========================================
st.markdown("### 🧮 3. Matrice d'Incidence M3 (M2 - M1)")

# حساب M3 رياضياً
m3_data = []
for r in range(P):
    row = []
    for c in range(T):
        val = m2_data[r][c] - m1_data[r][c]
        row.append(val)
    m3_data.append(row)

# رسم المصفوفة M3 مع رؤوس الصفوف والأعمدة (Headers)
m3_html = """
<div style='overflow-x: auto; display: flex; justify-content: center; margin-bottom: 20px;'>
    <table style='border-collapse: collapse; text-align: center; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
"""

# صف عناوين الأعمدة (T1, T2...)
m3_html += "<tr><th style='padding: 10px; background-color: #f2f2f2; border: 1px solid #ddd;'></th>"
for c in range(T):
    m3_html += f"<th style='padding: 15px; background-color: #34495e; color: white; border: 1px solid #ddd;'>T{c+1}</th>"
m3_html += "</tr>"

# صفوف البيانات مع عناوين الصفوف (P1, P2...)
for r in range(P):
    m3_html += "<tr>"
    m3_html += f"<th style='padding: 15px; background-color: #34495e; color: white; border: 1px solid #ddd;'>P{r+1}</th>"
    for c in range(T):
        val = m3_data[r][c]
        bg_color = "#fce4e4" if val < 0 else ("#e4fce4" if val > 0 else "#f9f9f9")
        text_color = "#c0392b" if val < 0 else ("#27ae60" if val > 0 else "#7f8c8d")
        m3_html += f"<td style='background-color: {bg_color}; color: {text_color}; padding: 15px 25px; border: 1px solid #ddd; font-weight: bold; font-size: 16px;'>{val}</td>"
    m3_html += "</tr>"

m3_html += "</table></div>"
st.markdown(m3_html, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 4. العلامة الابتدائية i والشعاع S
# ==========================================
st.markdown("### 🎯 4. Vecteurs de Marquage (i) et Algébrique (S)")

col_i, space2, col_s = st.columns([1, 0.1, 1])

with col_i:
    st.markdown("<h5 style='color: #27ae60;'>Marquage Initial (i)</h5>", unsafe_allow_html=True)
    i_data = create_matrix_input("i", P, 1, "P", "")
    i_vec = [row[0] for row in i_data]

with col_s:
    st.markdown("<h5 style='color: #2c3e50;'>Vecteur Algébrique (S)</h5>", unsafe_allow_html=True)
    s_data = create_matrix_input("s", T, 1, "T", "")
    s_vec = [row[0] for row in s_data]

st.markdown("---")

# ==========================================
# 5. العمليات والمحاكاة
# ==========================================
st.markdown("### 🚀 5. Actions et Simulation")

res_alg = st.empty()
res_fran = st.empty()
res_sim = st.empty()

col_btn1, col_btn2 = st.columns(2)

# ----- زر الحساب الجبري K -----
with col_btn1:
    if st.button("🧮 1. Calcul Algébrique (K)", use_container_width=True):
        res_alg.empty()
        k_result = []
        for r in range(P):
            dot_product = sum(m3_data[r][c] * s_vec[c] for c in range(T))
            res_val = i_vec[r] + dot_product
            k_result.append(res_val)
            
        with res_alg.container():
            st.info("**Résultat K (Équation d'état : K = i + M3 · S) :**")
            k_html = "<div style='display: flex; gap: 10px; justify-content: center; margin-top: 10px;'>"
            for idx, val in enumerate(k_result):
                color = "#e74c3c" if val < 0 else "#2ecc71"
                k_html += f"<div style='text-align: center;'><span style='font-size: 12px; font-weight: bold; color: #555;'>P{idx+1}</span><br><div style='background-color: {color}; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px; min-width: 40px;'>{val}</div></div>"
            k_html += "</div>"
            st.markdown(k_html, unsafe_allow_html=True)

# ----- زر الانتقالات القابلة للعبور -----
with col_btn2:
    if st.button("✅ 2. Afficher Franchissables", use_container_width=True):
        res_fran.empty()
        franchissables = []
        for t in range(T):
            is_franchissable = True
            for p in range(P):
                if i_vec[p] < m1_data[p][t]:
                    is_franchissable = False
                    break
            if is_franchissable:
                franchissables.append(f"T{t+1}")
                
        with res_fran.container():
            if franchissables:
                st.success(f"**Transitions Franchissables au marquage i :** {', '.join(franchissables)}")
            else:
                st.error("**Aucune transition franchissable à ce stade.**")

st.markdown("<br>", unsafe_allow_html=True)

# ----- محاكاة التسلسل -----
st.markdown("**🎬 Simulation de Séquence S**")
seq_str = st.text_input("Séquence (ex: 1, 2, 1 pour T1 ➔ T2 ➔ T1) :", placeholder="1, 2, 1")

if st.button("▶️ Démarrer la Simulation", use_container_width=True, type="primary"):
    res_sim.empty()
    if not seq_str.strip():
        st.warning("⚠️ Veuillez entrer une séquence valide.")
    else:
        try:
            raw_seq = seq_str.replace("T", "").replace("t", "").split(",")
            sequence = [int(x.strip()) - 1 for x in raw_seq if x.strip()]
            
            marking = list(i_vec)
            
            with res_sim.container():
                st.write(f"**Trace de Simulation :**")
                st.markdown(f"**M0 = {marking}**")
                
                for step, t in enumerate(sequence):
                    if t < 0 or t >= T:
                        st.error(f"❌ La transition **T{t+1}** n'existe pas.")
                        break
                        
                    is_franchissable = True
                    for p in range(P):
                        if marking[p] < m1_data[p][t]:
                            is_franchissable = False
                            break
                            
                    if is_franchissable:
                        for p in range(P):
                            marking[p] = marking[p] + m3_data[p][t]
                        st.success(f"✅ **T{t+1}** franchie. **M{step+1} = {marking}**")
                    else:
                        st.error(f"❌ **ÉCHEC** : **T{t+1}** NON franchissable au marquage {marking} !")
                        break
                        
        except ValueError:
            st.error("⚠️ Format invalide. Utilisez des nombres séparés par des virgules.")
            
