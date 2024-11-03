## Installation de l'environnement de travail

### Conda

Depuis la racine du projet, lancer :

```bash
conda env create -f environment.yml
conda activate pesto-crypto
```

### SageMath

Il faut créer un environnement Sage pour faire tourner le notebook. La commande suivante installe SageMath comme un nouveau kernel sous le nom `sagemath-dev`.

```bash
# À exécuter dans l'environnement pesto-crypto
jupyter kernelspec install --user $(sage -sh -c 'ls -d $SAGE_VENV/share/jupyter/kernels/sagemath') --name sagemath-dev
```

Après avoir ouvert le notebook dans VSCode, il suffit de sélectionner le kernel jupyter `sagemath-dev` pour faire tourner les cellules.