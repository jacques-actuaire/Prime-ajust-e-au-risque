def analyse_tarification(fichier_excel):
    import pandas as pd
    import numpy as np
    import statsmodels.api as sm
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Lecture du fichier
    df = pd.read_excel(fichier_excel)

    # Nettoyage
    df = df[df["ID"] != "Moyenne / Total"]

    # Statistiques de base
    frequence = df["NbSinistres"].sum() / len(df)
    severite = df["CoutSinistres"].sum() / df["NbSinistres"].sum()
    prime_pure = frequence * severite
    print("La prime pure moyenne est :", prime_pure, "FCFA")

    # Variables
    df["Severite"] = df["CoutSinistres"] / df["NbSinistres"]
    df["Severite"] = df["Severite"].fillna(0)
    df["Frequence"] = df["NbSinistres"]
    df["PrimePure"] = df["Frequence"] * df["Severite"]

    # Préparation des variables explicatives
    X = df[["Age","Sexe","AnciennetePermis","Ville","TypeVehicule","PuissanceCV","ValeurVehicule","KilometrageAnnuel"]]
    y = df["NbSinistres"]

    variables_cat = ["Sexe","Ville","TypeVehicule"]
    preprocesseur = ColumnTransformer([("cat", OneHotEncoder(drop="first"), variables_cat)], remainder="passthrough")
    X_prepare = preprocesseur.fit_transform(X)

    # Modèle Poisson
    modele_poisson = sm.GLM(y, X_prepare, family=sm.families.Poisson())
    resultat = modele_poisson.fit()
    df["Frequence_Predite"] = resultat.predict(X_prepare)

    # Modèle Gamma (sévérité)
    df_severite = df[df["NbSinistres"] > 0].copy()
    y_severite = df_severite["Severite"]
    X_severite = df_severite[["Age","Sexe","AnciennetePermis","Ville","TypeVehicule","PuissanceCV","ValeurVehicule","KilometrageAnnuel"]]

    preprocesseur_gamma = ColumnTransformer([("cat", OneHotEncoder(drop="first"), variables_cat)], remainder="passthrough")
    X_severite_prepare = preprocesseur_gamma.fit_transform(X_severite)

    modele_gamma = sm.GLM(y_severite, X_severite_prepare, family=sm.families.Gamma(link=sm.families.links.Log()))
    resultat_gamma = modele_gamma.fit()
    df_severite["Severite_Predite"] = resultat_gamma.predict(X_severite_prepare)

    # Fusion des résultats
    df["Severite_Predite"] = 0
    df.loc[df_severite.index, "Severite_Predite"] = df_severite["Severite_Predite"]
    df["Prime_Proposee"] = df["Frequence_Predite"] * df["Severite_Predite"]

    # Prime commerciale
    taux_chargement = 0.25
    df["Prime_Commerciale"] = df["Prime_Proposee"] * (1 + taux_chargement)
    df["Ecart_Prime"] = df["Prime_Proposee"] - df["PrimeActuelle"]
    df["Ecart_%"] = (df["Ecart_Prime"] / df["PrimeActuelle"]) * 100

    # Export final
    df.to_excel("Resultats_Tarification_Automobile.xlsx", index=False)
    print("Export terminé.")

    return df
