# Equity Model 14 Analysis
## Reproduction Check: Inclusion Model 14
- Data: `../processed/analysis_data.csv`
- Reference script: `../code/08_moderated_mediation.py`
- Bootstrap: 5,000 case-resampling iterations, seed=42, percentile 95% CI
- Reproduction checks: `{'interaction_b': np.True_, 'interaction_p': np.True_, 'index': True, 'index_ci_low': True, 'index_ci_high': True, 'low_ie': True, 'low_ci_low': True, 'low_ci_high': True, 'high_ie': True, 'high_ci_low': True, 'high_ci_high': True}`

Inclusion OI x EL -> UPB: B=-0.062264, p=0.011124

Inclusion index of moderated mediation: -0.025635, 95% CI [-0.045425, -0.005770]

## Equity A Path

| Path         |        B |        SE |       z |           p |   ci_low |   ci_high |
|:-------------|---------:|----------:|--------:|------------:|---------:|----------:|
| Equity -> OI | 0.376346 | 0.0191342 | 19.6687 | 3.99781e-86 | 0.338843 |  0.413848 |

## Equity B Paths and Moderation

| Path           |          B |        SE |        z |           p |     ci_low |    ci_high |
|:---------------|-----------:|----------:|---------:|------------:|-----------:|-----------:|
| OI -> UPB      |  0.170733  | 0.0276361 |  6.17789 | 6.4966e-10  |  0.116567  |  0.224899  |
| EL -> UPB      |  0.0971636 | 0.0231294 |  4.20086 | 2.65901e-05 |  0.0518307 |  0.142496  |
| OI x EL -> UPB | -0.0622635 | 0.0245249 | -2.53879 | 0.0111236   | -0.110331  | -0.0141957 |

## Simple Slopes: OI -> UPB by EL

| EL level   |        B |        SE |       z |           p |    ci_low |   ci_high |
|:-----------|---------:|----------:|--------:|------------:|----------:|----------:|
| -1 SD      | 0.230177 | 0.0354742 | 6.48857 | 8.66558e-11 | 0.160648  |  0.299707 |
| Mean       | 0.170733 | 0.0276361 | 6.17789 | 6.4966e-10  | 0.116566  |  0.2249   |
| +1 SD      | 0.111289 | 0.0369534 | 3.01159 | 0.00259882  | 0.0388599 |  0.183717 |

## Conditional Indirect Effects

| DEI dimension   | EL level   |   Conditional indirect effect (B) |   Bootstrap SE | 95% Bootstrap CI   | Decision    |
|:----------------|:-----------|----------------------------------:|---------------:|:-------------------|:------------|
| Equity          | -1 SD      |                         0.0866825 |      0.0148169 | [0.058, 0.117]     | significant |
| Equity          | Mean       |                         0.0642705 |      0.0113566 | [0.043, 0.087]     | significant |
| Equity          | +1 SD      |                         0.0418585 |      0.0141194 | [0.014, 0.070]     | significant |
| Inclusion       | -1 SD      |                         0.094633  |      0.0158839 | [0.064, 0.126]     | significant |
| Inclusion       | Mean       |                         0.0701584 |      0.0121537 | [0.047, 0.095]     | significant |
| Inclusion       | +1 SD      |                         0.0456839 |      0.015305  | [0.016, 0.076]     | significant |

## Index of Moderated Mediation

| DEI dimension   |   Index of Moderated Mediation |   Bootstrap SE | 95% Bootstrap CI   | Decision    |
|:----------------|-------------------------------:|---------------:|:-------------------|:------------|
| Equity          |                     -0.023475  |     0.00939643 | [-0.042, -0.005]   | significant |
| Inclusion       |                     -0.0256353 |     0.0102391  | [-0.045, -0.006]   | significant |
