# Lab 1 — Written explanations

## Lab 1

### Step 2 Why high accuracy can coexist with modest AUC

Accuracy is (TP + TN) / N at a particular decision threshold. If only 10% of customers churn, predicting “no churn” for everyone gives 90% accuracy, but it finds no churners: recall is 0. A constant score gives AUC 0.5 because it cannot rank churners above non-churners. ROC AUC measures ranking over thresholds, so a model can have an AUC around 0.7–0.8 and still achieve high accuracy mainly from the majority class. Use the exact prevalence printed by generate_data.py to compute your own majority baseline as 1 minus prevalence. AUC is not an accuracy percentage.

### E1 Precision and recall

Precision = TP / (TP + FP): of the people offered retention benefits, how many would churn? Recall = TP / (TP + FN): of all churners, how many did we identify? The supplied script logs both with zero_division=0 so a model predicting no positives reports 0 rather than producing an undefined-value warning.

For a fixed, costly outreach budget, precision is important because false positives consume offers unnecessarily. Recall still matters because missed high-value churners represent lost revenue. A practical decision should optimize expected retained value minus offer cost under a budget constraint, choose a threshold on validation data, and report both metrics. If retention value greatly exceeds offer cost, favoring recall may be rational; there is no universal answer independent of costs. The default 0.5 threshold is a lab starting point, not a proven business optimum. A model with nonzero AUC and low recall may rank customers usefully even though its thresholded actions are poor.

### E2 Third challenger

GradientBoostingClassifier is implemented with learning_rate, n_estimators and max_depth. The runner uses (100, 0.05, depth 3) and (200, 0.1, depth 3). It registers the best full-dataset run after those trials. Compare your actual AUCs to decide whether the winning weights changed. A new registry version can refer to the same trained model; version history alone does not prove a different winner. More trees or a more complex algorithm need not outperform a simpler model when labels contain irreducible random noise.

### E3 Human tags

Author and purpose describe the context of a run and are useful for search and organization. Tags can be amended as understanding changes. Hyperparameters such as C or tree depth define how the estimator was trained; parameters record these choices and are not a suitable mutable workspace for human notes. The filter is tags.author = 'your actual name'. A data fingerprint is logged as a parameter because the exact input snapshot is part of the run's reproducible specification.

### E4 Data fingerprints

Removing one row changes the logged MD5-prefix fingerprint, revealing that two scores came from different data snapshots even if both files were named churn_data.csv. This prevents a comparison such as “my AUC is higher, therefore my algorithm is better” when Priya and Arjun actually trained and tested on different data. Identical data bytes produce the same fingerprint on different computers; it is not a machine ID. A short hash is useful for this exercise but a real governed system should store the dataset/version and a stronger complete digest as well.

### E5 Autolog versus manual

Autolog records estimator parameters beyond the small manually selected set, model artifacts and training evaluation information; depending on supported calls/version it also captures dataset metadata and post-training evaluation. Inspect your actual artifact and parameter list and name one item absent from your manual run, such as an RF estimator option or an automatically produced training confusion-matrix artifact. Autolog cannot infer the intended business purpose, your chosen author identity or the exact custom CSV fingerprint convention. Our train_auto.py contains no manual log calls; its test score printout is not named test_auc, so it is intentionally excluded from the manual champion-selection query.

### Reflection Separate laptop stores

Two local SQLite databases create two separate experiment histories and potentially two incompatible meanings of “champion”. Artifact paths on one laptop are inaccessible on the other; concurrent writers and backups also become operational problems. A shared tracking server, shared artifact storage, centralized access control and a suitable multi-user database provide a common history and registry. A model artifact plus pinned environment is necessary but not sufficient for reproducibility: version data, preprocessing, code and splits too.

