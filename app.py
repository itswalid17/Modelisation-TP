import streamlit as st

st.set_page_config(page_title="Réseaux de Petri", layout="centered")

st.markdown("<h2 style='text-align: center;'>🕸️ Matrice de Pétri : Saisie Matricielle</h2>", unsafe_allow_html=True)

# 1. الأبعاد
P = st.number_input("Nombre de Places (P)", min_value=1, value=3, step=1)
T = st.number_input("Nombre de Transitions (T)", min_value=1, value=2, step=1)

# 2. دالة بناء جدول مصفوفة حقيقي
def render_matrix_as_table(title, rows, cols, key_prefix):
    st.markdown(f"**{title}**")
    # إنشاء وعاء للمصفوفة
    matrix_container = st.container(border=True)
    with matrix_container:
        data = []
        for r in range(rows):
            row_cols = st.columns(cols)
            row_data = []
            for c in range(cols):
                with row_cols[c]:
                    # إدخال رقمي بسيط داخل خلية الجدول
                    val = st.number_input(f"{r}{c}", label_visibility="collapsed", 
                                          value=0, step=1, key=f"{key_prefix}_{r}_{c}")
                    row_data.append(int(val))
            data.append(row_data)
    return data

# عرض المصفوفات بجانب بعضها بشكل مربع
col1, col2 = st.columns(2)
with col1:
    m1 = render_matrix_as_table("Matrice M1 (Pre)", P, T, "m1")
with col2:
    m2 = render_matrix_as_table("Matrice M2 (Post)", P, T, "m2")

# 3. حساب M3 بنفس المنطق الرياضي
st.markdown("### 🧮 Matrice d'Incidence (M3)")
m3 = [[m2[r][c] - m1[r][c] for c in range(T)] for r in range(P)]

# عرض M3 في جدول مرتب كلاسيكي
def display_m3_table(matrix):
    table_html = "<table style='width:100%; border: 1px solid #ddd; text-align:center;'>"
    for row in matrix:
        table_html += "<tr>"
        for val in row:
            color = "#ffcccc" if val < 0 else ("#ccffcc" if val > 0 else "#f9f9f9")
            table_html += f"<td style='padding:10px; background-color:{color}; border: 1px solid #ccc;'>{val}</td>"
        table_html += "</tr>"
    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

display_m3_table(m3)

# 4. المحاكاة (نفس المنطق البرمجي لكودك)
st.markdown("---")
st.markdown("### 🚀 Simulation")
i_vec = [st.number_input(f"Marquage P{r+1}", value=0, key=f"i_{r}") for r in range(P)]
seq_input = st.text_input("Séquence (ex: 1, 2) :")

if st.button("Lancer Simulation"):
    current_marking = list(i_vec)
    seq = [int(x.strip())-1 for x in seq_input.split(",") if x.strip()]
    
    for t in seq:
        # التحقق من إمكانية العبور (Franchissabilité)
        if all(current_marking[p] >= m1[p][t] for p in range(P)):
            current_marking = [current_marking[p] + m3[p][t] for p in range(P)]
            st.success(f"Transition T{t+1} franchie. Marquage: {current_marking}")
        else:
            st.error(f"Transition T{t+1} bloquée!")
            break
            
