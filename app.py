import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="TP Réseaux de Petri", layout="centered", page_icon="🕸️")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>TP Modélisation et Simulation : Réseaux de Petri</h2>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 1. إعدادات الأبعاد
# ==========================================
st.markdown("### ⚙️ 1. Paramètres (P et T)")
col_p, col_t = st.columns(2)
with col_p:
    P = st.number_input("Nombre de Places (P)", min_value=1, value=3, step=1, key="P")
with col_t:
    T = st.number_input("Nombre de Transitions (T)", min_value=1, value=2, step=1, key="T")

st.markdown("---")

# ==========================================
# دالة مساعدة لإنشاء شبكة إدخال متوافقة مع الهاتف
# ==========================================
def create_input_grid(name, rows, cols, prefix):
    grid_data = []
    for r in range(rows):
        row_cols = st.columns(cols)
        row_data = []
        for c in range(cols):
            with row_cols[c]:
                # استخدام number_input يجبر الهاتف على فتح لوحة الأرقام
                val = st.number_input(
                    label=f"{prefix} R{r}C{c}", 
                    value=0, 
                    step=1, 
                    key=f"{name}_{r}_{c}", 
                    label_visibility="collapsed"
                )
                row_data.append(int(val))
        grid_data.append(row_data)
    return grid_data

# ==========================================
# 2. إنشاء المصفوفات M1 و M2
# ==========================================
st.markdown("### 📊 2. Matrices $M_1$ (Pre) et $M_2$ (Post)")

col_m1, space, col_m2 = st.columns([1, 0.1, 1])

with col_m1:
    st.markdown("**Matrice $M_1$ (Pre)**")
    m1_data = create_input_grid("m1", P, T, "M1")

with col_m2:
    st.markdown("**Matrice $M_2$ (Post)**")
    m2_data = create_input_grid("m2", P, T, "M2")

st.markdown("---")

# ==========================================
# 3. حساب وعرض M3
# ==========================================
st.markdown("### 🧮 3. Matrice d'Incidence $M_3$ ($M_2 - M_1$)")

# حساب M3 بنفس خوارزمية Tkinter
m3_data = []
for r in range(P):
    row = []
    for c in range(T):
        val = m2_data[r][c] - m1_data[r][c]
        row.append(val)
    m3_data.append(row)

# عرض M3 بشكل ملون تماماً كما في كودك الأصلي باستخدام HTML
m3_html = "<div style='display: flex; justify-content: center;'><table style='border-collapse: collapse; text-align: center; font-weight: bold;'>"
for r in range(P):
    m3_html += "<tr>"
    for c in range(T):
        val = m3_data[r][c]
        color = "#e74c3c" if val < 0 else ("#2ecc71" if val > 0 else "#95a5a6")
        m3_html += f"<td style='background-color: {color}; color: white; padding: 10px 20px; border: 2px solid white;'>{val}</td>"
    m3_html += "</tr>"
m3_html += "</table></div>"

st.markdown(m3_html, unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 4. العلامة الابتدائية i والشعاع S
# ==========================================
st.markdown("### 🎯 4. Vecteurs de Marquage ($i$) et Algébrique ($S$)")

col_i, space2, col_s = st.columns([1, 0.1, 1])

with col_i:
    st.markdown("**Marquage Initial ($i$)**")
    i_data = create_input_grid("i", P, 1, "I")
    i_vec = [row[0] for row in i_data] # تحويله إلى قائمة مسطحة

with col_s:
    st.markdown("**Vecteur Algébrique ($S$)**")
    s_data = create_input_grid("s", T, 1, "S")
    s_vec = [row[0] for row in s_data] # تحويله إلى قائمة مسطحة

st.markdown("---")

# ==========================================
# 5. العمليات والمحاكاة (بنفس منطق TPmod.py)
# ==========================================
st.markdown("### 🚀 5. Actions et Simulation")

# حاويات لعرض النتائج
res_alg = st.empty()
res_fran = st.empty()
res_sim = st.empty()

col_btn1, col_btn2 = st.columns(2)

# ----- زر الحساب الجبري K -----
with col_btn1:
    if st.button("🧮 1. Calcul Algébrique ($K$)", use_container_width=True):
        res_alg.empty() # تفريغ النتيجة السابقة
        k_result = []
        for r in range(P):
            dot_product = sum(m3_data[r][c] * s_vec[c] for c in range(T))
            res_val = i_vec[r] + dot_product
            k_result.append(res_val)
            
        with res_alg.container():
            st.info("**Résultat K (Équation d'état) :**")
            k_html = "<div style='display: flex; gap: 5px;'>"
            for val in k_result:
                color = "#e74c3c" if val < 0 else "#2ecc71"
                k_html += f"<div style='background-color: {color}; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px;'>{val}</div>"
            k_html += "</div>"
            st.markdown(k_html, unsafe_allow_html=True)

# ----- زر الانتقالات القابلة للعبور -----
with col_btn2:
    if st.button("✅ 2. Afficher Franchissables", use_container_width=True):
        res_fran.empty()
        franchissables = []
        for t in range(T):
            # دالة is_franchissable مدمجة هنا
            is_franchissable = True
            for p in range(P):
                if i_vec[p] < m1_data[p][t]:
                    is_franchissable = False
                    break
            if is_franchissable:
                franchissables.append(f"T{t+1}")
                
        with res_fran.container():
            if franchissables:
                st.success(f"**Transitions Franchissables au marquage $i$ :** {', '.join(franchissables)}")
            else:
                st.error("**Aucune transition franchissable à ce stade.**")

st.markdown("<br>", unsafe_allow_html=True)

# ----- محاكاة التسلسل -----
st.markdown("**Simulation de Séquence $S$**")
seq_str = st.text_input("Séquence (ex: 1, 2, 1 pour $T_1 \\rightarrow T_2 \\rightarrow T_1$) :", placeholder="1, 2, 1")

if st.button("🎬 3. Simuler Séquence", use_container_width=True, type="primary"):
    res_sim.empty()
    if not seq_str.strip():
        st.warning("⚠️ Veuillez entrer une séquence (ex: 1, 2, 1)")
    else:
        try:
            # تنظيف المدخلات (نفس كودك الأصلي)
            raw_seq = seq_str.replace("T", "").replace("t", "").split(",")
            sequence = [int(x.strip()) - 1 for x in raw_seq if x.strip()]
            
            marking = list(i_vec) # أخذ نسخة من العلامة الابتدائية
            
            with res_sim.container():
                st.write(f"**Trace de Simulation :**")
                st.markdown(f"**$M_0$ = {marking}**")
                
                for step, t in enumerate(sequence):
                    if t < 0 or t >= T:
                        st.error(f"❌ La transition **$T_{t+1}$** n'existe pas.")
                        break
                        
                    # التحقق من العبور
                    is_franchissable = True
                    for p in range(P):
                        if marking[p] < m1_data[p][t]:
                            is_franchissable = False
                            break
                            
                    if is_franchissable:
                        # تطبيق الانتقال: M_new = M_old + M3[:, t]
                        for p in range(P):
                            marking[p] = marking[p] + m3_data[p][t]
                        st.success(f"✅ **$T_{t+1}$** franchie. **$M_{step+1}$ = {marking}**")
                    else:
                        st.error(f"❌ **ÉCHEC** : **$T_{t+1}$** NON franchissable à ce stade ! Simulation arrêtée.")
                        break # تتوقف المحاكاة إذا كان الانتقال غير ممكن
                        
        except ValueError:
            st.error("⚠️ Format de séquence invalide. Utilisez des nombres séparés par des virgules.")
                        
