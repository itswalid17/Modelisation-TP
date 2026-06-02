import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple

st.set_page_config(
    page_title="TP Réseaux de Petri",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Helpers
# ---------------------------

def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def parse_matrix_text(text: str, rows: int, cols: int, name: str) -> List[List[int]]:
    """
    Parse a matrix entered as plain text.
    Accepted formats:
    - rows separated by newlines or semicolons
    - values separated by commas, spaces, or tabs
    Example:
        1, 0, 2
        0, 1, 0
    """
    if not text or not text.strip():
        raise ValueError(f"{name}: veuillez saisir des valeurs.")

    raw_rows = [r.strip() for r in text.replace(";", "\n").splitlines() if r.strip()]
    if len(raw_rows) != rows:
        raise ValueError(f"{name}: attendu {rows} lignes, trouvé {len(raw_rows)}.")

    matrix = []
    for i, row in enumerate(raw_rows, start=1):
        tokens = [t for t in row.replace("\t", " ").replace(",", " ").split() if t]
        if len(tokens) != cols:
            raise ValueError(f"{name}: ligne {i} attend {cols} valeurs, trouvé {len(tokens)}.")
        try:
            matrix.append([int(x) for x in tokens])
        except Exception:
            raise ValueError(f"{name}: toutes les valeurs doivent être entières (ligne {i}).")
    return matrix


def matrix_to_text(matrix: List[List[int]]) -> str:
    return "\n".join(", ".join(str(v) for v in row) for row in matrix)


def empty_matrix(rows: int, cols: int, fill: int = 0) -> List[List[int]]:
    return [[fill for _ in range(cols)] for _ in range(rows)]


def matrix_to_df(matrix: List[List[int]], row_prefix: str, col_prefix: str) -> pd.DataFrame:
    df = pd.DataFrame(matrix)
    df.index = [f"{row_prefix}{i+1}" for i in range(len(matrix))]
    df.columns = [f"{col_prefix}{j+1}" for j in range(len(matrix[0]))]
    return df


def compute_incidence(m1: List[List[int]], m2: List[List[int]]) -> List[List[int]]:
    return [[m2[i][j] - m1[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]


def get_marking_from_text(text: str, size: int, name: str) -> List[int]:
    if not text or not text.strip():
        raise ValueError(f"{name}: veuillez saisir {size} valeurs.")
    tokens = [t for t in text.replace(";", "\n").replace(",", " ").replace("\t", " ").split() if t]
    if len(tokens) != size:
        raise ValueError(f"{name}: attendu {size} valeurs, trouvé {len(tokens)}.")
    try:
        return [int(x) for x in tokens]
    except Exception:
        raise ValueError(f"{name}: toutes les valeurs doivent être entières.")


def get_sequence(text: str, t_count: int) -> List[int]:
    if not text or not text.strip():
        raise ValueError("Veuillez entrer une séquence.")
    cleaned = text.upper().replace("T", " ").replace("(", " ").replace(")", " ")
    tokens = [t for t in cleaned.replace(";", ",").replace(" ", ",").split(",") if t.strip()]
    seq = []
    for tok in tokens:
        try:
            val = int(tok)
        except Exception:
            raise ValueError("Séquence invalide. Utilisez par exemple: 1,2,1 ou T1,T2,T1")
        if not (1 <= val <= t_count):
            raise ValueError(f"Transition T{val} inexistante. Le réseau contient T1 à T{t_count}.")
        seq.append(val - 1)
    return seq


def is_franchissable(marking: List[int], pre_matrix: List[List[int]], t_index: int) -> bool:
    return all(marking[p] >= pre_matrix[p][t_index] for p in range(len(marking)))


def apply_transition(marking: List[int], incidence: List[List[int]], t_index: int) -> List[int]:
    return [marking[p] + incidence[p][t_index] for p in range(len(marking))]


def color_for_value(v: int) -> str:
    if v < 0:
        return "rgba(220, 53, 69, 0.12)"
    if v > 0:
        return "rgba(40, 167, 69, 0.12)"
    return "rgba(108, 117, 125, 0.12)"


def styled_matrix_df(matrix: List[List[int]], title: str, row_prefix: str, col_prefix: str):
    df = matrix_to_df(matrix, row_prefix=row_prefix, col_prefix=col_prefix)

    def style_df(frame: pd.DataFrame):
        return frame.applymap(lambda v: f"background-color: {color_for_value(v)}; font-weight: 600; text-align: center;")

    st.subheader(title)
    st.dataframe(
        df.style.apply(style_df, axis=None),
        use_container_width=True,
        height=120 + 28 * len(matrix),
    )


def init_state():
    defaults = {
        "P": 3,
        "T": 2,
        "m1_text": "1, 0\n0, 1\n1, 0",
        "m2_text": "1, 1\n0, 1\n1, 1",
        "i_text": "1, 0, 2",
        "s_text": "1, 2, 1",
        "seq_text": "1,2,1",
        "results": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# ---------------------------
# UI
# ---------------------------

st.title("TP Modélisation et Simulation — Réseaux de Petri")
st.caption("Interface Streamlit optimisée pour lecture sur mobile, saisie rapide et calculs structurés.")

with st.sidebar:
    st.header("Paramètres")
    st.session_state.P = st.number_input("Nombre de places (P)", min_value=1, max_value=20, value=int(st.session_state.P), step=1)
    st.session_state.T = st.number_input("Nombre de transitions (T)", min_value=1, max_value=20, value=int(st.session_state.T), step=1)

    st.divider()
    st.subheader("Actions")
    create_btn = st.button("Créer / Réinitialiser les matrices", use_container_width=True)
    clear_btn = st.button("Effacer les résultats", use_container_width=True)

    st.divider()
    st.info(
        "Astuce mobile : utilisez le format texte. "
        "Chaque ligne = une ligne de matrice, valeurs séparées par virgules."
    )

if clear_btn:
    st.session_state.results = None

if create_btn:
    st.session_state.m1_text = matrix_to_text(empty_matrix(int(st.session_state.P), int(st.session_state.T), 0))
    st.session_state.m2_text = matrix_to_text(empty_matrix(int(st.session_state.P), int(st.session_state.T), 0))
    st.session_state.i_text = ", ".join(["0"] * int(st.session_state.P))
    st.session_state.s_text = ", ".join(["0"] * int(st.session_state.T))
    st.session_state.seq_text = ""
    st.session_state.results = None

col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("Saisie des matrices")
    st.write("Format recommandé :")
    st.code("1, 0, 2\n0, 1, 0", language="text")

    st.session_state.m1_text = st.text_area(
        "Matrice M1 (Pre)",
        value=st.session_state.m1_text,
        height=140,
        help="Entrez P lignes et T colonnes. Exemple: 1,0,2 ثم سطر جديد.",
    )
    st.session_state.m2_text = st.text_area(
        "Matrice M2 (Post)",
        value=st.session_state.m2_text,
        height=140,
        help="Entrez P lignes و T colonnes بنفس الطريقة.",
    )

    m1_ready = m2_ready = None
    try:
        m1_ready = parse_matrix_text(st.session_state.m1_text, int(st.session_state.P), int(st.session_state.T), "M1")
        m2_ready = parse_matrix_text(st.session_state.m2_text, int(st.session_state.P), int(st.session_state.T), "M2")
        incidence = compute_incidence(m1_ready, m2_ready)
        st.success("Matrices M1 et M2 lues avec succès.")
    except Exception as e:
        incidence = None
        st.warning(str(e))

    st.subheader("Marquage et vecteur")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.i_text = st.text_input(
            "Marquage initial i",
            value=st.session_state.i_text,
            help=f"{int(st.session_state.P)} valeurs séparées par virgules",
        )
    with c2:
        st.session_state.s_text = st.text_input(
            "Vecteur S (algébrique)",
            value=st.session_state.s_text,
            help=f"{int(st.session_state.T)} valeurs séparées par virgules",
        )

    st.session_state.seq_text = st.text_input(
        "Séquence à simuler",
        value=st.session_state.seq_text,
        placeholder="1,2,1 ou T1,T2,T1",
    )

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    calc_btn = btn_col1.button("Calculer M3", use_container_width=True)
    k_btn = btn_col2.button("Calculer K", use_container_width=True)
    fr_btn = btn_col3.button("Transitions franchissables", use_container_width=True)

    sim_btn = st.button("Simuler la séquence", use_container_width=True)

with col2:
    st.subheader("Aperçu")
    if m1_ready is not None and m2_ready is not None:
        styled_matrix_df(m1_ready, "Matrice M1 (Pre)", "P", "T")
        styled_matrix_df(m2_ready, "Matrice M2 (Post)", "P", "T")
        st.divider()
        styled_matrix_df(incidence, "Matrice d'incidence M3 = M2 - M1", "P", "T")
    else:
        st.info("Les matrices valides apparaîtront ici après saisie correcte.")

# ---------------------------
# Results
# ---------------------------

if calc_btn or k_btn or fr_btn or sim_btn:
    if m1_ready is None or m2_ready is None:
        st.error("Veuillez corriger la saisie de M1 et M2.")
    else:
        if calc_btn:
            st.subheader("Résultat M3")
            st.dataframe(matrix_to_df(incidence, "P", "T"), use_container_width=True)

        if k_btn:
            try:
                i_vec = get_marking_from_text(st.session_state.i_text, int(st.session_state.P), "Marquage initial i")
                s_vec = get_marking_from_text(st.session_state.s_text, int(st.session_state.T), "Vecteur S")
                k_vec = [
                    i_vec[p] + sum(incidence[p][t] * s_vec[t] for t in range(int(st.session_state.T)))
                    for p in range(int(st.session_state.P))
                ]

                st.subheader("Calcul algébrique K")
                out = pd.DataFrame({"K": k_vec}, index=[f"P{i+1}" for i in range(int(st.session_state.P))])
                st.dataframe(out, use_container_width=True)
                st.success("K = i + M3 × S")
            except Exception as e:
                st.error(str(e))

        if fr_btn:
            try:
                i_vec = get_marking_from_text(st.session_state.i_text, int(st.session_state.P), "Marquage initial i")
                franch = [f"T{t+1}" for t in range(int(st.session_state.T)) if is_franchissable(i_vec, m1_ready, t)]
                st.subheader("Transitions franchissables")
                if franch:
                    st.success(", ".join(franch))
                else:
                    st.error("Aucune transition franchissable au marquage initial.")
            except Exception as e:
                st.error(str(e))

        if sim_btn:
            try:
                i_vec = get_marking_from_text(st.session_state.i_text, int(st.session_state.P), "Marquage initial i")
                sequence = get_sequence(st.session_state.seq_text, int(st.session_state.T))

                st.subheader("Trace de simulation")
                trace = []
                current = i_vec[:]
                trace.append(("M0", current[:], "Marquage initial"))

                stopped = False
                for step, t in enumerate(sequence, start=1):
                    if is_franchissable(current, m1_ready, t):
                        current = apply_transition(current, incidence, t)
                        trace.append((f"M{step}", current[:], f"T{t+1} franchie"))
                    else:
                        trace.append((f"M{step}", current[:], f"T{t+1} non franchissable"))
                        stopped = True
                        break

                trace_df = pd.DataFrame(
                    {
                        "Étape": [x[0] for x in trace],
                        "Marquage": [str(x[1]) for x in trace],
                        "Statut": [x[2] for x in trace],
                    }
                )
                st.dataframe(trace_df, use_container_width=True)

                if stopped:
                    st.error("La simulation s'est arrêtée car une transition n'était pas franchissable.")
                else:
                    st.success(f"Simulation terminée. Marquage final : {current}")
            except Exception as e:
                st.error(str(e))

st.divider()
st.caption("Déployable directement sur Streamlit Community Cloud avec ce fichier comme app principale.")
    
