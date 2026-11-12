# Numerai公共记录链：独立限定验收

**PASS_LIMITED_PUBLIC_RECORD_CHAIN_REVIEW，无材料错误；完整盈利记录链仍未取得。**

- Saved public_user_profile source L429-475 binds tournament-specific model UUID and public v3UserProfile;raw_query defaults authorizationFalse L89-94/134-141. Request uses documented selected fields, no private-account mutation or pending_model_payouts.
- Saved submission_scores source L1406-1485 matches query variables/score fields. Public scores do not include all actual per-round stakes, NMR transfers/claim tx, gas, conversion or USD profit;authenticated pending_model_payouts is distinct L1487-1537 and not requested. payoutSettled in old v2 method is not independently proved onchain settlement.
- Public response modelId/username bound; not fixed code/weights/history. nmrStaked:null unknown, not zero nor proof UI0.05 false.
- 32B submissionScores empty list is query result only. resolvedTrue+lastNRounds1 does not prove latest-resolved selector or absence of historic predictions/profit. Corrected all_resolved_true null retains vacuous raw allTrue, not completion evidence.
- UI Woke2019 date, description late2023 and moving source link neither prove unchanged model nor prove model switch. Score averages/current multipliers not historical-reward reconstruction. UI values root observations only, not independently refreshed.
- Next request spec has executionfalse; removing recency/change distinct is only saved next-read draft, no public read performed by reviewer. Existing TLS fail and curl success distinct receipts; strictTLS sslverify0/authfalse/curl-q configuration claims supported by saved receipts, not independently observed network execution.

两份原响应bytes/SHA与各自成功receipt匹配；所有实际输入指纹见JSON。本审阅未独立重开网页或观察curl执行，浏览器字段和运输设置分别为root原观察及保存收据层。无新增公开读取、模型、回测、账户、交易或收益计算，仅写review。actual model/effort UNKNOWN。
