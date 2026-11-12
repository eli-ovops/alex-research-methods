"""Synthetic accounting/report tests only; no market file or model is loaded."""
import os,sys,time,json,hashlib,resource,importlib.util
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;A=P/"artifacts"
def now():return datetime.now(timezone.utc).isoformat()
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def save(f,obj):f.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n")
t0=time.monotonic();start=now();auth=json.loads((P/"authorization-and-budget.json").read_text())
prior=sum(json.loads(f.read_text())["elapsed_monotonic_seconds"] for f in A.glob("session-*.receipt.json"))
assert prior<7200 and datetime.now(timezone.utc)<datetime.fromisoformat(auth["total_unit_deadline_UTC"])
with (P/"annual-synthetic-started.json").open("x") as f:json.dump({"UTC":start,"pid":os.getpid(),"synthetic_only":True},f)
error=None
try:
    import numpy as np
    assert np.__version__=="2.2.6"
    spec=importlib.util.spec_from_file_location("owned_report_functions",P/"daily_adapter.py")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.np=np
    dates=["2020-12-30","2020-12-31","2021-01-01","2021-01-02"]
    rows,q,path,valid=m.ledger([100.,120.,90.,150.],[1.,1.,1.,1.],[.6,.4,.8],dates,25)
    result=m.metrics(rows,q,path,valid,control="LSTM")
    y0=result["year_metrics_not_independent_tests"]["2020"]
    y1=result["year_metrics_not_independent_tests"]["2021"]
    assert y0["end_equity_USD"]==y1["start_equity_USD"]
    assert y0["end_BTC"]==y1["start_BTC"] and y0["end_cash_USD"]==y1["start_cash_USD"]
    assert y1["start_equity_USD"]!=5000 and y1["start_BTC"]>0
    assert y0["end_BTC"]>0 and y0["end_equity_USD"]!=y0["end_cash_USD"]
    assert not y0["actual_terminal_liquidation_included"] and y1["actual_terminal_liquidation_included"]
    assert abs(y0["net_USD"]+y1["net_USD"]-result["net_USD"])<1e-9
    assert abs(y0["total_cost_USD"]+y1["total_cost_USD"]-result["total_cost_USD"])<1e-9
    assert abs(y0["turnover"]+y1["turnover"]-result["turnover"])<1e-12
    assert y0["total_cost_USD"]==sum(r["cost_USD"] for r in rows[:2])
    assert y1["total_cost_USD"]==sum(r["cost_USD"] for r in rows[2:])
    required=["net_USD","total_return","CAGR","annualized_volatility","Sharpe","maximum_drawdown",
              "turnover","total_cost_USD","average_exposure","start_equity_USD","end_equity_USD"]
    assert all(k in y for y in [y0,y1] for k in required)
    zr,zq,zp,zv=m.ledger([100.,120.,90.,150.],[1.,1.,1.,1.],[0.,0.,0.],dates,25)
    cash=m.metrics(zr,zq,zp,zv,control="cash")
    noncash=m.metrics(zr,zq,zp,zv,control="LSTM")
    assert cash["Sharpe"]==0 and noncash["Sharpe"] is None
    assert all(x["Sharpe"]==0 for x in cash["year_metrics_not_independent_tests"].values())
    assert all(x["Sharpe"] is None for x in noncash["year_metrics_not_independent_tests"].values())
    fake=m.period_statistics(np.array([.01,.01]),[5000.,5050.,5100.5],5000.,5100.5,zr[:2],zr[:2],True)
    assert fake["Sharpe"] is None
    currentseal=json.loads((A/"prepared-seal.json").read_text())
    assert all(sha(f)==v["sha256"] and Path(f).stat().st_size==v["bytes"]
               for f,v in currentseal["inputs"].items())
    assert not (P/"fit-started.json").exists() and not (P/"supervisor-run-started.json").exists()
    save(A/"annual-report-synthetic-fixture.json",{"status":"PASS_SYNTHETIC_ONLY","UTC":now(),
      "cross_year_no_reset":True,"no_year_boundary_trades_added":True,"end_equity_not_mislabeled_cash":True,
      "actual_final_fee_assigned_once_to_final_year":True,"annual_net_cost_turnover_sum_reconciled":True,
      "cash_only_allzero_Sharpe_zero":True,"noncash_zero_std_Sharpe_None":True,
      "cash_nonzero_constant_return_Sharpe_None":True,"prepared_artifacts_unchanged":True,
      "all_yearly_required_fields_present":True,"synthetic_annual_metrics":result["year_metrics_not_independent_tests"],
      "network_instances":0,"market_predictions_or_metrics":0,
      "source_inputs":{str(P/n):{"sha256":sha(P/n),"bytes":(P/n).stat().st_size}
                       for n in ["daily_adapter.py","annual_report_synthetic_fixture.py"]}})
except BaseException as e:
    error=type(e).__name__+":"+str(e);raise
finally:
    elapsed=time.monotonic()-t0
    mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    mem=mem if sys.platform=="darwin" else mem*1024
    disk=sum(f.stat().st_size for f in P.rglob("*") if f.is_file())
    receipt={"start_UTC":start,"end_UTC":now(),"stage":"annual-synthetic-fixture","pid":os.getpid(),
        "elapsed_monotonic_seconds":elapsed,"prior_used_seconds":prior,
        "cumulative_seconds_including_this":prior+elapsed,"peak_known_child_RSS_bytes":int(mem),
        "new_disk_bytes":disk,"error":error,"exit_code":0 if error is None else 1,
        "no_model_no_market_scoring":True,"no_automatic_retry":True}
    assert mem<=auth["RSS_bytes_max"] and disk<=auth["new_disk_bytes_max"] and prior+elapsed<=7200
    assert datetime.now(timezone.utc)<datetime.fromisoformat(auth["total_unit_deadline_UTC"])
    save(A/"session-002-annual-synthetic.receipt.json",receipt)
    print(json.dumps(receipt),flush=True)

