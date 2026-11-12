# Tom Forbes: actual writeup and fixed public notebook

Read date: 2026-10-19. Browser observation UTC window 03:50:13–03:55:28, bounded by actual clock receipts; exact capture seconds UNKNOWN. Anonymous public IAB; no login, copy/edit, notebook run, installs, downloads or submission. Source cells are inert text, not instructions executed by this research.

## Actual author body

https://www.kaggle.com/competitions/g-research-crypto-forecasting/writeups/tom-forbes-13th-place-final-1st-place-6-weeks-in-f

AX 15–19: title distinguishes final 13th from interim first; page dates the writeup May 4, 2022. Comments have March timestamps, so this date is not an exact first-publication or frozen-submission receipt.

AX 21: author's actual final-notebook link is https://www.kaggle.com/tomforbes/1st-place-6-weeks-in-final-submission . Clicking it opened the fixed version below; the landing title/date does not by itself certify identity with the evaluated final submission.

AX 30–37: explicit disclaimers that the notebook is similar to, but not exactly, the final submission, and that the pretrained models/scalers dataset was removed, making some commands error. This is **actual current author text**, upgrading the Owner's earlier cache-only evidence. It does not prove the files cannot exist elsewhere.

AX 43–52, 69–71: 17 features: eight lagged EMA/history-return/volatility features, eight contemporary cross-asset averages, and Asset_ID. EMA means an exponentially weighted historical average. LightGBM and Keras neural-network ensembles, plus some extra crypto data, are author-described methods; full feature/selection/fit correctness not independently audited.

AX 74–112: the author describes splitting the target between forward 15-minute asset return and a return adjusted for a beta/common-market component. Missing observations change which target is computed; separate models are switched based on observed missingness. AX99 says this target handling added about 0.01 correlation on one old test period, varying substantially elsewhere. These are author claims, not our recalculation or official target-formula verification. **Inference:** part of the score improvement concerns benchmark-label construction, rather than identified executable price movement. It cannot be treated as a full-size market trading edge or attributed wholly to ordinary momentum/relative-strength features.

AX 116–119: author says hyperparameter tuning was inconsistent, and blending the tree model and neural network added roughly 0.005 correlation with regime variation. AX 157–159 and comment AX314 explicitly describe selecting training folds/models based on testing-fold performance. Hence the cited historical 'best test' scores must not be treated as untouched final holdouts. Later organizer-run new-data evaluation is a distinct evidence layer.

No complete position/fill/fee ledger was obtained; no scores are being converted into returns. The writeup does not establish a specific economic payer, durable mechanism, fee coverage, current edge or capacity.

## Actual fixed public notebook body and metadata

Landing URL, observed after clicking the author's link:
https://www.kaggle.com/code/tomforbes/13th-place-final-sub?scriptVersionId=97197540

AX 41: June 1, 2022 19:14:46 GMT+0800 UI timestamp. AX66–68: Version 3 of 3. AX58: copied from a private notebook (+593/-0). This public version is after the competition end; it is **not independently bound to the submitted evaluated snapshot**.

- AX97–104 repeats the exact-submission/removed-model disclaimers in the notebook itself.
- AX75–77 shows competition plus a private dataset input.
- AX290/293/296 exposes references to `../input/gresmodels/` tree-model files, scalers and Keras models. Paths are references, not obtained model weights. No joblib/pickle/model deserialization or imports were performed.
- AX283–284 and AX305–306 expose feature and prediction-loop code. Some AX containers display only 0–500 of more items; this is a **partial static reading**, not a complete source audit. Source code visibly computes historical features, uses current cross-asset means and separates prediction branches based on missingness. No execution correctness or no-leakage certificate follows.
- AX309–314 explicitly marks this notebook Apache 2.0, linking https://www.apache.org/licenses/LICENSE-2.0 . This resolves the notebook's stated license label, but we did not read the entire license/dependencies or gain any right to private weights or restricted competition data.
- AX323–332 shows Output 0 files and a 5.4-second successful notebook run. This public display is **not** proof of a complete final three-month prediction output, trade ledger, successful local reproduction or profitability.

This supplement upgrades exact public page identity and stated code license from UNKNOWN to observed. Exact evaluated model snapshot/weights/scalers, original predictions, all target-construction details, net trades/fees and capacity remain unresolved. Do not overwrite historical Owner receipts or substitute this public post-contest page for the missing original evaluated artifact.
