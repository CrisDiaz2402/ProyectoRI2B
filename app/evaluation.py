# app/evaluation.py
import streamlit as st

import json
import os
import numpy as np

def precision_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)
    return len([r for r in retrieved_k if r in relevant_set]) / k if k else 0

def recall_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)
    return len([r for r in retrieved_k if r in relevant_set]) / len(relevant_set) if relevant_set else 0

def f1_at_k(retrieved, relevant, k):
    p = precision_at_k(retrieved, relevant, k)
    r = recall_at_k(retrieved, relevant, k)
    return 2*p*r/(p+r) if (p+r) > 0 else 0

def average_precision(retrieved, relevant):
    score = 0.0
    num_hits = 0.0
    for i, r in enumerate(retrieved):
        if r in relevant:
            num_hits += 1
            score += num_hits / (i+1)
    return score / len(relevant) if relevant else 0

def mean_average_precision(results):
    # results: list of (retrieved, relevant)
    return np.mean([average_precision(r, rel) for r, rel in results]) if results else 0

def dcg_at_k(retrieved, relevant, k):
    dcg = 0.0
    for i, r in enumerate(retrieved[:k]):
        if r in relevant:
            dcg += 1 / np.log2(i+2)
    return dcg

def ndcg_at_k(retrieved, relevant, k):
    dcg = dcg_at_k(retrieved, relevant, k)
    ideal = dcg_at_k(relevant, relevant, min(k, len(relevant)))
    return dcg / ideal if ideal > 0 else 0

def mrr(results):
    # results: list of (retrieved, relevant)
    rr = []
    for retrieved, relevant in results:
        for i, r in enumerate(retrieved):
            if r in relevant:
                rr.append(1/(i+1))
                break
        else:
            rr.append(0)
    return np.mean(rr) if rr else 0

def calcular_ctr(feedback):
    # feedback: lista de dicts con 'click' (bool/int)
    if not feedback:
        return 0
    total = len(feedback)
    clicks = sum(1 for f in feedback if f.get('like', 0) or f.get('click', 0))
    return clicks / total if total else 0

def cargar_feedback():
    ruta = os.path.join(os.path.dirname(__file__), '../data/processed/feedback/feedback.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def cargar_resultados_reales():
    """
    Lee un archivo JSON con resultados y ground truth.
    Formato esperado:
    [
      {"retrieved": ["img1", "img2", ...], "relevant": ["img2", ...]},
      ...
    ]
    """
    ruta = os.path.join(os.path.dirname(__file__), '../data/processed/feedback/resultados_groundtruth.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [(d["retrieved"], d["relevant"]) for d in data]
    return None

def pagina_evaluacion():
    st.title("📈 Evaluación del Sistema")
    st.markdown("Métricas y análisis de rendimiento del buscador.")

    # Intentar cargar resultados reales
    resultados_reales = cargar_resultados_reales()
    if resultados_reales:
        st.success("Mostrando métricas calculadas con resultados reales.")
        resultados = resultados_reales
    else:
        st.warning("No se encontró archivo de resultados reales. Mostrando métricas de ejemplo.")
        resultados = [
            (["img1", "img2", "img3", "img4"], ["img2", "img4"]),
            (["img5", "img6", "img7"], ["img5"]),
            (["img8", "img9"], ["img10"]),
        ]

    k = 3
    prec = np.mean([precision_at_k(r, rel, k) for r, rel in resultados])
    rec = np.mean([recall_at_k(r, rel, k) for r, rel in resultados])
    f1 = np.mean([f1_at_k(r, rel, k) for r, rel in resultados])
    map_score = mean_average_precision(resultados)
    ndcg = np.mean([ndcg_at_k(r, rel, k) for r, rel in resultados])
    mrr_score = mrr(resultados)

    feedback = cargar_feedback()
    ctr = calcular_ctr(feedback)

    st.subheader("Métricas de Evaluación")
    st.write(f"**Precisión@{k}:** {prec:.2f}")
    st.write(f"**Recall@{k}:** {rec:.2f}")
    st.write(f"**F1-score@{k}:** {f1:.2f}")
    st.write(f"**Mean Average Precision (mAP):** {map_score:.2f}")
    st.write(f"**nDCG@{k}:** {ndcg:.2f}")
    st.write(f"**MRR:** {mrr_score:.2f}")
    st.write(f"**CTR (Tasa de clics/likes):** {ctr:.2f}")

    st.info("Para ver métricas reales, guarda tus resultados y ground truth en 'data/processed/feedback/resultados_groundtruth.json'.")