"""Owned independent DMN-style adapter. No downloaded author code is executed.
prepare never instantiates a network or emits market model outputs.
run is exclusive, gated and cannot be repeated after its claim exists."""
import os, sys, json, csv, math, hashlib, time, warnings, resource, argparse
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
P = Path(__file__).resolve().parent
A = P / "artifacts"
A.mkdir(exist_ok=True)
AUTH = P / "authorization-and-budget.json"
PROPOSAL_SHA = "4b2e1a51a9ffe31c2b40b62df1f558dc3bbd7c5fb2ca7221128a6af1d76d175b"
PROTOCOL_SHA = "4eebd510205468f1b5e8877a42554b4c63490f4d0e8fdbfc96dc3d49eb1b0c15"
HORIZONS = (1,21,63,126,252)
SPLITS = {"train":("2014-01-01","2018-12-31"),
          "validation":("2020-01-01","2021-12-31"),
          "final_test":("2023-01-01","2025-12-31")}
def utc(): return datetime.now(timezone.utc).isoformat()
def write(n,v):
    (A/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def digest(f):
    h=hashlib.sha256()
    with Path(f).open("rb") as r:
        for b in iter(lambda:r.read(1048576),b""): h.update(b)
    return h.hexdigest()
def ident(f): return {"sha256":digest(f),"bytes":Path(f).stat().st_size}
def seal(n,files):
    write(n,{"sealed_UTC":utc(),"inputs":{str(Path(f).resolve()):ident(f) for f in files}})
def check_limits():
    au=json.loads(AUTH.read_text())
    if datetime.now(timezone.utc)>=datetime.fromisoformat(au["total_unit_deadline_UTC"]):
        raise RuntimeError("TOTAL_UTC_DEADLINE")
    mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    mem=mem if sys.platform=="darwin" else mem*1024
    if mem>au["RSS_bytes_max"]: raise RuntimeError("RSS_LIMIT")
    if sum(f.stat().st_size for f in P.rglob("*") if f.is_file())>au["new_disk_bytes_max"]:
        raise RuntimeError("DISK_LIMIT")
def fixed():
    au=json.loads(AUTH.read_text())
    assert au["authorization"]=="EXPLICITLY_APPROVED"
    assert digest(au["proposal"])==PROPOSAL_SHA
    assert digest(au["protocol"])==PROTOCOL_SHA
    cfg=json.loads(Path(au["protocol"]).read_text())
    return au,cfg
def health(stage):
    global np, torch
    import numpy as np
    import torch
    if sys.version_info[:3]!=(3,12,14): raise RuntimeError("PYTHON_VERSION_MISMATCH")
    if np.__version__!="2.2.6" or torch.__version__!="2.8.0": raise RuntimeError("PACKAGE_VERSION_MISMATCH")
    torch.set_num_threads(6); torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    np.seterr(divide="raise",over="raise",invalid="raise",under="ignore")
    assert torch.get_num_threads()==6 and torch.get_num_interop_threads()==1
    assert bool(torch.isfinite(torch.tensor([0.,1.],device="cpu")).all())
    assert bool(np.isfinite(np.array([0.,1.])).all())
    out={"UTC":utc(),"Python":sys.version,"numpy":np.__version__,"torch":torch.__version__,
         "torch_intra":torch.get_num_threads(),"torch_interop":torch.get_num_interop_threads(),
         "deterministic_requested":torch.are_deterministic_algorithms_enabled(),
         "device":"CPU","no_network_or_model_constructed":True,
         "thread_environment":{k:os.environ.get(k) for k in ["OMP_NUM_THREADS","MKL_NUM_THREADS",
           "OPENBLAS_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS","PYTHONDONTWRITEBYTECODE"]}}
    for k,v in out["thread_environment"].items():
        if k!="PYTHONDONTWRITEBYTECODE": assert v=="6"
    write("health-"+stage+".json",out)
    check_limits()

def ledger(prices,volumes,targets,dates,bps,signal=None,caps=None):
    """Independent cash/unit accounting, not a weights-difference cost approximation."""
    cash=5000.; units=0.; c=bps/10000.; rows=[]; returns=[]; path=[5000.]
    for i in range(len(prices)):
        terminal=i==len(prices)-1; price=float(prices[i])
        intended=0. if terminal else float(targets[i])
        pre=cash+units*price; oldcash=cash; oldunits=units
        a=units*price/pre
        eff=a if volumes[i]==0 else intended
        sign=0. if eff==a else (1. if eff>a else -1.)
        phi=(1+c*sign*a)/(1+c*sign*eff)
        if volumes[i]!=0:
            post=phi*pre; units=eff*post/price; cash=(1-eff)*post
        post=cash+units*price; delta=units-oldunits; nominal=abs(delta)*price; cost=c*nominal
        tol=max(1e-8,1e-10*pre)
        assert abs(pre-post-cost)<=tol
        assert abs(cash-(oldcash-delta*price-cost))<=tol
        assert cash>=-1e-9 and units>=-1e-9
        assert 0<=intended<=1 and 0<=eff<=1
        nxt=post if terminal else cash+units*float(prices[i+1])
        ret=None if terminal else nxt/pre-1
        if ret is not None: returns.append(ret)
        elif returns: returns[-1]=(1+returns[-1])*(post/pre)-1
        path.extend([pre,post,nxt])
        row={"execution_date":str(dates[i]),"decision_time":str(dates[i])+"T00:10:00Z",
             "feature_cutoff":(date.fromisoformat(str(dates[i]))-timedelta(days=2)).isoformat(),
             "price_proxy_time":str(dates[i])+"T00:10:00Z","P":price,
             "signal":None if terminal or signal is None else float(signal[i]),
             "risk_cap":None if terminal or caps is None else float(caps[i]),
             "targetweight":intended,"intendedweight":intended,"actualweight":eff,
             "pretrade_units":oldunits,"pretrade_cash":oldcash,"pretrade_equity":pre,
             "driftedweight":a,"trade_BTC":delta,"reference_trade_USD":nominal,
             "cost_bps":bps,"cost_USD":cost,"posttrade_units":units,"posttrade_cash":cash,
             "posttrade_equity":post,"next_equity":nxt,"daily_net_return":ret,
             "terminal_liquidation_flag":terminal,"reference_bar_Volume":float(volumes[i]),
             "zero_volume_no_fill":bool(volumes[i]==0),
             "risk_target_deviation":None if terminal or caps is None else eff-float(caps[i])}
        rows.append(row)
    q=np.array(returns,dtype=np.float64)
    assert np.isfinite(q).all() and np.isfinite(path).all()
    assert abs(float(np.prod(1+q))*5000-rows[-1]["posttrade_equity"])<=max(1e-8,1e-10*rows[-1]["posttrade_equity"])
    # Terminal fee is assigned only once, to the last holding interval.
    if len(q):
        rows[-2]["daily_net_return"]=float(q[-1])
        rows[-2]["next_equity"]=rows[-1]["posttrade_equity"]
    valid=units==0.
    return rows,q,np.array(path),valid

def tensor_account(prices,volumes,targets):
    """Differentiable same cash/unit path, float64. No model construction here."""
    cash=torch.tensor(5000.,dtype=torch.float64); units=torch.tensor(0.,dtype=torch.float64)
    c=.0025; qs=[]
    for i in range(len(prices)):
        price=prices[i]; pre=cash+units*price; a=units*price/pre
        terminal=i==len(prices)-1
        intended=torch.zeros((),dtype=torch.float64) if terminal else targets[i].to(torch.float64)
        if volumes[i]>0:
            sign=torch.sign(intended-a)
            phi=(1+c*sign*a)/(1+c*sign*intended)
            post=phi*pre
            units=intended*post/price; cash=(1-intended)*post
        post=cash+units*price
        if terminal:
            if float(units.detach())!=0.: raise RuntimeError("TERMINAL_NO_FILL_WITH_HOLDING")
            qs[-1]=(1+qs[-1])*(post/pre)-1
        else:
            qs.append((cash+units*prices[i+1])/pre-1)
    q=torch.stack(qs)
    if not bool(torch.isfinite(q).all()): raise RuntimeError("NONFINITE_TRAIN_ACCOUNT")
    return q

def synthetic_fixtures():
    fixtures=[
      ([100.,110.,90.,105.],[1.,1.,1.,1.],[.5,.75,.2]),
      ([100.,110.,90.,105.],[0.,1.,0.,1.],[.5,.75,.2]),
      ([100.,100.,100.],[1.,1.,1.],[0.,0.])]
    checks=[]
    for prices,vols,weights in fixtures:
        rr,q,_,valid=ledger(prices,vols,weights,["2000-01-01"]*len(prices),25)
        tq=tensor_account(torch.tensor(prices,dtype=torch.float64),vols,torch.tensor(weights,dtype=torch.float64,requires_grad=True))
        assert np.allclose(tq.detach().numpy(),q,rtol=0,atol=1e-12)
        checks.append({"q_agreement_abs_max":float(np.max(np.abs(tq.detach().numpy()-q))),"valid_terminal":valid})
    # Hand identity for cash ->100% BTC at unchanged100, then exit.
    rr,q,_,_=ledger([100.,100.],[1.,1.],[1.],["2000-01-01"]*2,25)
    expected=5000*(1-.0025)/(1+.0025)
    assert abs(rr[-1]["posttrade_cash"]-expected)<1e-9
    # No-fill terminal must retain actual units and invalidate cash realization.
    rr,_,_,v=ledger([100.,100.],[1.,0.],[1.],["2000-01-01"]*2,25)
    assert not v and rr[-1]["posttrade_units"]>0
    write("synthetic-accounting-fixtures.json",{"kind":"SYNTHETIC_NOT_MARKET_RESULTS",
      "checks":checks,"entry_exit_hand_identity_agrees":True,"terminal_no_fill_invalid":True,
      "no_model_constructed_no_market_prediction":True})

def aggregate(cfg):
    src=Path(cfg["data"]["path"])
    assert src.stat().st_size==cfg["data"]["bytes"]
    assert digest(src)==cfg["data"]["sha256"]
    daily=[]; current=None; group=None; previous=None; n=0
    def finish(g):
        if g is None: return
        g["complete"]=g["count"]==1440 and g["first_minute"]==0 and g["last_minute"]==1439
        daily.append(g)
    with src.open(newline="") as f:
        r=csv.reader(f); assert next(r)==cfg["data"]["columns"]
        for row in r:
            n+=1
            if n%100000==0: check_limits()
            assert len(row)==6
            t=int(row[0]); assert str(t)==row[0] and t%60==0
            assert previous is None or t-previous==60; previous=t
            o,h,l,close,vol=map(float,row[1:])
            assert all(math.isfinite(x) for x in [o,h,l,close,vol])
            assert min(o,h,l,close)>0 and vol>=0 and h>=max(o,l,close) and l<=min(o,h,close)
            day=t//86400; minute=t%86400//60
            if day!=current:
                finish(group);current=day
                group={"day":day,"date":datetime.fromtimestamp(day*86400,timezone.utc).date().isoformat(),
                  "count":0,"first_minute":minute,"last_minute":minute,"close":None,"price":None,"volume":None,"zero_minutes":0}
            group["count"]+=1;group["last_minute"]=minute;group["zero_minutes"]+=vol==0
            if minute==1439: group["close"]=close
            if minute==10: group["price"]=close; group["volume"]=vol
    finish(group)
    assert n==7780439
    partial=[g for g in daily if not g["complete"]]
    assert [g["date"] for g in partial]==["2012-01-01","2026-10-17"]
    complete=[g for g in daily if g["complete"]]
    assert all(complete[i+1]["day"]-complete[i]["day"]==1 for i in range(len(complete)-1))
    with (A/"daily-source-inputs.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(daily[0]));w.writeheader();w.writerows(daily)
    return complete,{"minute_rows":n,"complete_label_days":len(complete),"partial_days":partial,
                    "data_identity":ident(src)}

def prepare():
    au,cfg=fixed();health("prepare");synthetic_fixtures()
    daily,source=aggregate(cfg)
    C=np.array([g["close"] for g in daily],dtype=np.float64)
    # These are only past-return features, never a future-outcome summary.
    r=np.full(len(C),np.nan);r[1:]=C[1:]/C[:-1]-1
    sigma=np.full(len(C),np.nan);features=np.full((len(C),5),np.nan)
    for j in range(60,len(C)): sigma[j]=max(float(np.std(r[j-59:j+1],ddof=0)),1e-6)
    for j in range(252,len(C)):
        features[j]=[(C[j]/C[j-h]-1)/(sigma[j]*math.sqrt(h)) for h in HORIZONS]
    mapping={g["date"]:i for i,g in enumerate(daily)}
    arrays={}; manifests=[]; splitmeta={}; train_union=set()
    for name,(start,end) in SPLITS.items():
        day=date.fromisoformat(start);last=date.fromisoformat(end);inds=[]
        while day<=last:
            key=day.isoformat()
            assert key in mapping,"MISSING_REQUIRED_DAY:"+key
            inds.append(mapping[key]);day+=timedelta(days=1)
        assert all(inds[i+1]-inds[i]==1 for i in range(len(inds)-1))
        windows=[]
        for j in inds[:-1]:
            lo,hi=j-61,j-1 # exclusivehi: last feature j-2
            assert hi-lo==60 and lo-252==j-313
            assert np.isfinite(features[lo:hi]).all()
            windows.append(np.arange(lo,hi))
            if name=="train":train_union.update(range(lo,hi))
            manifests.append({"split":name,"execution_date":daily[j]["date"],
              "feature_first":daily[lo]["date"],"feature_last":daily[hi-1]["date"],
              "earliest_raw_close":daily[j-313]["date"],"window_length":60})
        arrays[name+"_window_indices"]=np.stack(windows)
        arrays[name+"_prices"]=np.array([daily[j]["price"] for j in inds],dtype=np.float64)
        arrays[name+"_volumes"]=np.array([daily[j]["volume"] for j in inds],dtype=np.float64)
        arrays[name+"_dates"]=np.array([daily[j]["date"] for j in inds])
        arrays[name+"_caps"]=np.array([min(1.,.4/(math.sqrt(365)*sigma[j-2])) for j in inds[:-1]],dtype=np.float64)
        arrays[name+"_trend"]=np.array([C[j-2]>C[j-65] for j in inds[:-1]],dtype=np.float64)
        splitmeta[name]={"windows":len(windows),"first_execution":start,"terminal":end,
            "zero_volume_execution_reference_count":int(sum(daily[j]["volume"]==0 for j in inds)),
            "terminal_reference_positive_volume":bool(daily[inds[-1]]["volume"]>0)}
    union=np.array(sorted(train_union))
    mu=features[union].mean(axis=0);std=features[union].std(axis=0,ddof=0);constant=std==0
    scale=np.where(constant,1.,std)
    for name in SPLITS:
        ix=arrays.pop(name+"_window_indices")
        x=(features[ix]-mu)/scale;x[:,:,constant]=0
        arrays[name+"_X"]=np.clip(x,-10,10).astype(np.float32)
        assert arrays[name+"_X"].shape[1:]==(60,5)
    write("scalers.json",{"fit_source":"Unique TRAIN feature-date rows only","mean":mu.tolist(),
       "std_population":std.tolist(),"constant_channels":constant.tolist(),"unique_rows":len(union),
       "first_feature_date":daily[int(union[0])]["date"],"last_feature_date":daily[int(union[-1])]["date"],
       "not_refit_on_validation_test":True})
    with (A/"alignment-manifest.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(manifests[0]));w.writeheader();w.writerows(manifests)
    np.savez(A/"prepared-inputs.npz",**arrays)
    write("preflight.json",{"status":"STOPPED_BEFORE_MODEL_FIT_OR_FORWARD","UTC":utc(),
       "source":source,"splits":splitmeta,"input_shape":[60,5],"scaler_fit_unique_train_only":True,
       "network_instances":0,"fit_claim_exists":(P/"fit-started.json").exists(),
       "model_predictions":0,"market_performance_metrics":0,"no_data_repair":True,
       "synthetic_fixtures_separate":True,"clock":"e-2; raw e-313..e-2;312 raw close labels",
       "terminal_volume_note":"Metadata only, no modeled holdings or performance examined"})
    seal("prepared-seal.json",[A/"prepared-inputs.npz",A/"scalers.json",A/"alignment-manifest.csv",
         A/"daily-source-inputs.csv",A/"preflight.json",A/"health-prepare.json",A/"synthetic-accounting-fixtures.json"])
    print("STOPPED_BEFORE_MODEL_FIT_OR_FORWARD",splitmeta,flush=True)

def verify_gate(gate):
    au,cfg=fixed();g=json.loads(Path(gate).read_text())
    assert g["allow_fit"] is True and g["allow_scoring"] is True
    inputs=g["source_inputs"]
    for f in [Path(__file__),P/"supervise.py",AUTH,Path(au["protocol"]),Path(au["proposal"]),
              A/"preflight.json",A/"prepared-seal.json"]:
        ref=inputs[str(f.resolve())];assert digest(f)==ref["sha256"],"GATE_SOURCE_CHANGED:"+str(f)
    ss=json.loads((A/"prepared-seal.json").read_text())
    for f,ref in ss["inputs"].items(): assert ident(f)==ref
    assert digest(cfg["data"]["path"])==cfg["data"]["sha256"]
    return au,cfg,g

def make_network():
    class Net(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm=torch.nn.LSTM(5,16,num_layers=1,batch_first=True,bias=True,
                 dropout=0,bidirectional=False,proj_size=0)
            self.head=torch.nn.Linear(16,1)
        def forward(self,x):
            out,_=self.lstm(x)
            return torch.sigmoid(self.head(out[:,-1,:])).squeeze(-1)
    torch.manual_seed(20261017)
    net=Net().cpu()
    # Explicit independent seeded initialization; do not depend on constructors' RNG draws.
    generator=torch.Generator(device="cpu");generator.manual_seed(20261017)
    with torch.no_grad():
        for name,param in sorted(net.named_parameters()):
            param.uniform_(-.1,.1,generator=generator)
    return net
def param_hash(net):
    h=hashlib.sha256()
    for name,t in sorted(net.state_dict().items()):
        h.update(name.encode());h.update(t.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()

def metrics(rows,q,path,valid):
    sd=float(np.std(q,ddof=0));mean=float(np.mean(q))
    sharpe=0. if np.all(q==0) else (math.sqrt(365)*mean/sd if sd>0 else None)
    peak=path[0];mdd=0.
    for v in path:
        peak=max(peak,v);mdd=max(mdd,1-v/peak)
    end=rows[-1]["posttrade_equity"]; costs=sum(r["cost_USD"] for r in rows)
    years={}
    for r,v in zip(rows[:-1],q):
        y=r["execution_date"][:4]
        yy=years.setdefault(y,{"log_growth":0.,"net_USD_contribution":0.,"cost_USD":0.,"intervals":0})
        yy["log_growth"]+=math.log1p(float(v));yy["net_USD_contribution"]+=float(v)*r["pretrade_equity"]
        yy["cost_USD"]+=r["cost_USD"];yy["intervals"]+=1
    years[rows[-2]["execution_date"][:4]]["cost_USD"]+=rows[-1]["cost_USD"]
    return {"terminal_equity_USD":end,"terminal_cash_USD":rows[-1]["posttrade_cash"],
       "residual_BTC":rows[-1]["posttrade_units"],"valid_liquidation":bool(valid),"net_USD":end-5000,
       "total_return":end/5000-1,"CAGR":(end/5000)**(365/len(q))-1,
       "mean_daily_return":mean,"annualized_mean_return":365*mean,
       "annualized_volatility":sd*math.sqrt(365),"Sharpe":sharpe,"maximum_drawdown":mdd,
       "turnover":sum(r["reference_trade_USD"]/r["pretrade_equity"] for r in rows),
       "total_cost_USD":costs,"average_exposure":float(np.mean([r["actualweight"] for r in rows[:-1]])),
       "zero_volume_reference_count":sum(r["zero_volume_no_fill"] for r in rows),
       "year_contributions_not_independent_tests":years}
def bootstrap(model_q,control_q):
    d=np.log1p(model_q)-np.log1p(control_q);n=len(d);rng=np.random.default_rng(20261017)
    lengths=[90]*(n//90)+([n%90] if n%90 else [])
    starts=rng.integers(0,n,size=(10000,len(lengths)))
    prefix=np.concatenate([[0.],np.cumsum(np.concatenate([d,d[:90]]))])
    means=np.zeros(10000)
    for j,L in enumerate(lengths):means+=prefix[starts[:,j]+L]-prefix[starts[:,j]]
    means/=n
    return {"mean_daily_log_excess":float(np.mean(d)),
       "one_sided_97_5_lower_bound":float(np.quantile(means,.025,method="linear")),
       "block_days":90,"replicates":10000,"seed":20261017,"RNG":"NumPyPCG64default_rng"}

def run(gate):
    au,cfg,g=verify_gate(gate)
    with (P/"fit-started.json").open("x") as f:
        json.dump({"UTC":utc(),"gate":str(Path(gate).resolve()),"gate_hash":digest(gate),
          "pid":os.getpid(),"once_only":True},f,indent=2)
    health("run")
    data=np.load(A/"prepared-inputs.npz",allow_pickle=False)
    net=make_network();initial=param_hash(net)
    optimizer=torch.optim.Adam(net.parameters(),lr=.001,betas=(.9,.999),eps=1e-8,
                              weight_decay=0,amsgrad=False)
    tx=torch.from_numpy(data["train_X"])
    tp=torch.from_numpy(data["train_prices"])
    caps=torch.from_numpy(data["train_caps"])
    log=[]
    net.train()
    for epoch in range(1,101):
        check_limits();optimizer.zero_grad(set_to_none=True)
        signal=torch.cat([net(tx[i:i+64]) for i in range(0,len(tx),64)])
        weights=signal.to(torch.float64)*caps
        q=tensor_account(tp,data["train_volumes"],weights)
        loss=-math.sqrt(365)*q.mean()/torch.sqrt(q.var(unbiased=False)+1e-8)
        if not bool(torch.isfinite(loss)): raise RuntimeError("NONFINITE_LOSS")
        loss.backward()
        for param in net.parameters():
            if param.grad is None or not bool(torch.isfinite(param.grad).all()):raise RuntimeError("NONFINITE_GRADIENT")
        norm=torch.nn.utils.clip_grad_norm_(net.parameters(),1.,error_if_nonfinite=True)
        optimizer.step()
        if any(not bool(torch.isfinite(v).all()) for v in net.parameters()):raise RuntimeError("NONFINITE_WEIGHT")
        log.append({"epoch":epoch,"loss":float(loss.detach()),"mean":float(q.mean().detach()),
          "std_population":float(q.std(unbiased=False).detach()),"grad_norm_before_clip":float(norm)})
        write("train-log.json",log)
        if epoch%10==0: print("EPOCH",epoch,"train_loss",log[-1]["loss"],flush=True)
    torch.save(net.state_dict(),A/"final-state-dict.pt")
    write("run-settings.json",{"protocol_sha":PROTOCOL_SHA,"proposal_sha":PROPOSAL_SHA,
          "initial_tensorhash":initial,"final_tensorhash":param_hash(net),"epochs":100,
          "seed":20261017,"optimizer":"Adam .001/.9/.999/1e-8/weightdecay0/amsgradFalse",
          "one_loss_and_update_per_epoch":True,"no_earlystop_no_tuning":True,"CPU_only":True})
    net.eval();preds={};signals={};files=[A/"final-state-dict.pt",A/"run-settings.json",A/"scalers.json",A/"train-log.json"]
    with torch.no_grad():
        for name in SPLITS:
            xx=torch.from_numpy(data[name+"_X"])
            ss=torch.cat([net(xx[i:i+64]) for i in range(0,len(xx),64)]).cpu().numpy().astype(np.float64)
            ww=ss*data[name+"_caps"]
            assert np.isfinite(ss).all() and ((ss>=0)&(ss<=1)).all()
            preds[name]=ww; signals[name]=ss
            f=A/(name+"-sealed-targets.csv")
            with f.open("w",newline="") as out:
                wr=csv.writer(out);wr.writerow(["execution_date","feature_cutoff","signal","risk_cap","targetweight"])
                for dt,s,cap,w in zip(data[name+"_dates"][:-1],ss,data[name+"_caps"],ww):
                    wr.writerow([dt,(date.fromisoformat(str(dt))-timedelta(days=2)).isoformat(),s,cap,w])
            files.append(f)
    seal("all-targets-before-heldout-scoring.seal.json",files)
    # All intent outputs sealed. Compute independent paths; do not score until ALL ledgers sealed.
    cache={};ledgerfiles=[]
    for name in SPLITS:
        controls={"LSTM":preds[name],"BTC_buy_hold":np.ones(len(preds[name])),
            "risk_scaled_buy_hold":data[name+"_caps"],
            "fixed_trend":data[name+"_caps"]*data[name+"_trend"],"cash":np.zeros(len(preds[name]))}
        for bps in (25,50):
            for control,w in controls.items():
                check_limits()
                rows,q,path,valid=ledger(data[name+"_prices"],data[name+"_volumes"],w,
                    data[name+"_dates"],bps,signal=(signals[name] if control=="LSTM" else None),caps=data[name+"_caps"])
                f=A/(name+"-"+control+"-"+str(bps)+"bps-ledger.csv")
                with f.open("w",newline="") as out:
                    wr=csv.DictWriter(out,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
                ledgerfiles.append(f);cache[(name,bps,control)]=(rows,q,path,valid)
    seal("all-ledgers-before-summary.seal.json",ledgerfiles)
    results={}
    for (name,bps,control),items in cache.items():
        results.setdefault(name,{}).setdefault(str(bps),{})[control]=metrics(*items)
    tests={}
    for control in ("risk_scaled_buy_hold","fixed_trend"):
        check_limits()
        tests[control]=bootstrap(cache[("final_test",25,"LSTM")][1],cache[("final_test",25,control)][1])
    m=results["final_test"]["25"]["LSTM"];v=results["validation"]["25"]["LSTM"];s=results["final_test"]["50"]["LSTM"]
    controls=("risk_scaled_buy_hold","fixed_trend")
    allvalid=all(x[3] for x in cache.values())
    gates={"validation_positive":v["terminal_cash_USD"]>5000,
      "test_positive":m["terminal_cash_USD"]>5000,
      "Sharpe_increment":m["Sharpe"] is not None and all(results["final_test"]["25"][c]["Sharpe"] is not None and m["Sharpe"]>=results["final_test"]["25"][c]["Sharpe"]+.2 for c in controls),
      "drawdown_primary":m["maximum_drawdown"]<=.35,
      "paired_log_excess":all(t["mean_daily_log_excess"]>0 and t["one_sided_97_5_lower_bound"]>0 for t in tests.values()),
      "stress_positive_and_controls":s["terminal_cash_USD"]>5000 and all(s["terminal_cash_USD"]>results["final_test"]["50"][c]["terminal_cash_USD"] for c in controls),
      "drawdown_stress":s["maximum_drawdown"]<=.40,"all_liquidations_valid":allvalid}
    status="TECHNICALLY_INVALID" if not allvalid else ("CANDIDATE_SUPPORTED" if all(gates.values()) else "NOT_SUPPORTED")
    write("evaluation-results.json",{"status":status,"UTC":utc(),"all_metrics":results,"paired_tests":tests,
          "gates":gates,"historical_assumed_cost_only":True,"actual_trades":0,"wealth_goal_achieved":False})
    seal("final-result.seal.json",[A/"evaluation-results.json",A/"all-targets-before-heldout-scoring.seal.json",
          A/"all-ledgers-before-summary.seal.json"])
    check_limits()
    print("COMPLETE",status,flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument("stage",choices=["prepare","run"])
    parser.add_argument("--approval");args=parser.parse_args()
    write("worker-"+args.stage+"-start.json",{"UTC":utc(),"pid":os.getpid(),"stage":args.stage})
    try:
        if args.stage=="prepare":prepare()
        else:
            if not args.approval:raise RuntimeError("MISSING_GATE")
            run(args.approval)
    except BaseException as e:
        write("worker-"+args.stage+"-STOP.json",{"UTC":utc(),"error":type(e).__name__+":"+str(e),
             "fit_claim_exists":(P/"fit-started.json").exists(),"no_automatic_retry":True})
        raise
    finally:
        write("worker-"+args.stage+"-end.json",{"UTC":utc(),"pid":os.getpid(),"peak_RSS_native_units":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
if __name__=="__main__":main()

