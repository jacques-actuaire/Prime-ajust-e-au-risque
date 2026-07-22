import streamlit as st
from analyse import analyse_tarification
import matplotlib.pyplot as plt
import pandas as pd

st.title("Application de Tarification Automobile")

uploaded_file = st.file_uploader("Uploader le fichier Excel des contrats", type=["xlsx"])

if uploaded_file is not None:
    st.success("Fichier reçu : " + uploaded_file.name)

    if st.button("Lancer l'analyse"):
        df_resultats = analyse_tarification(uploaded_file)
        st.write("Analyse terminée ✅")

        # Aperçu des données
        st.subheader("Aperçu des résultats")
        st.dataframe(df_resultats.head(20))

        # Indicateurs clés
        st.subheader("Indicateurs de performance")
        st.metric("Prime actuelle moyenne", f"{df_resultats['PrimeActuelle'].mean():,.0f} FCFA")
        st.metric("Prime proposée moyenne", f"{df_resultats['Prime_Proposee'].mean():,.0f} FCFA")
        st.metric("Prime commerciale moyenne", f"{df_resultats['Prime_Commerciale'].mean():,.0f} FCFA")

        sous_tarifes = df_resultats[df_resultats["Ecart_Prime"] > 0]
        sur_tarifes = df_resultats[df_resultats["Ecart_Prime"] < 0]
        st.metric("Sous-tarifés", len(sous_tarifes))
        st.metric("Sur-tarifés", len(sur_tarifes))

        # Graphiques
        st.subheader("Visualisations")
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        ax[0].hist(df_resultats["PrimeActuelle"], bins=30, edgecolor="black")
        ax[0].set_title("Distribution de la prime actuelle")
        ax[1].hist(df_resultats["Prime_Proposee"], bins=30, edgecolor="black")
        ax[1].set_title("Distribution de la prime proposée")
        st.pyplot(fig)

        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.scatter(df_resultats["PrimeActuelle"], df_resultats["Prime_Proposee"], alpha=0.6)
        ax2.plot([0, max(df_resultats["PrimeActuelle"].max(), df_resultats["Prime_Proposee"].max())],
                 [0, max(df_resultats["PrimeActuelle"].max(), df_resultats["Prime_Proposee"].max())],
                 "r--")
        ax2.set_xlabel("Prime actuelle")
        ax2.set_ylabel("Prime proposée")
        ax2.set_title("Prime actuelle vs Prime proposée")
        st.pyplot(fig2)

        # Téléchargement du fichier Excel
        st.download_button(
            label="Télécharger les résultats Excel",
            data=open("Resultats_Tarification_Automobile.xlsx", "rb").read(),
            file_name="Resultats_Tarification_Automobile.xlsx"
        )
