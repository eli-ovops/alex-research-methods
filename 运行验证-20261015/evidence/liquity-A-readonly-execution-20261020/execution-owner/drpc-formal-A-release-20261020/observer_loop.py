"""Original observer loop, with only all-head warmup continuity recorded."""
from adapters import *
from readonly_collector import completed_event_audit, timely, compact_snapshot, qualify

def observe_window(b,c,budget,evidence,rpc,stream,scanner,t0,t1,state,continuity,on_first_complete=None):
    tracker=ChainTrack();episodes=Episodes();last_audit=None;covered=0;unknown=0;scenario_wei=0;completed_count=0;clock_wall=time.time();clock_mono=time.monotonic();anchor_B=None;audit_usage={'transactions':0,'disk':0,'cpu':0}
    def audit_window(lo,hi,headers):
        old_disk=evidence.used();old_cpu=time.process_time();remaining=c['audit_reserve']['max_detail_transactions']-audit_usage['transactions']
        result=completed_event_audit(rpc,b,lo,hi,headers,max_transactions=remaining);evidence.save('result-audit',result)
        audit_usage['transactions']+=len(result['completed_transactions']);audit_usage['disk']+=evidence.used()-old_disk;audit_usage['cpu']+=time.process_time()-old_cpu
        if audit_usage['disk']>c['audit_reserve']['disk_bytes'] or audit_usage['cpu']>c['audit_reserve']['cpu_seconds']:raise Stop('AUDIT_ALLOWANCE_EXHAUSTED_UNKNOWN')
        return result
    while dt.datetime.now(dt.timezone.utc)<t1:
        budget.resource_check()
        if abs((time.time()-clock_wall)-(time.monotonic()-clock_mono))>1:raise Stop('UTC_MONOTONIC_CLOCK_DISCONTINUITY')
        head=stream.head();received=dt.datetime.now(dt.timezone.utc);timely(head,c['timeliness'])
        continuity_event=continuity.accept(head)
        if received<t0 and continuity_event=='REORG':evidence.save('warmup-reorg',{'UTC':utc(),'header':head,'not_formal_A_sample':True})
        if received<t0:continue
        if received>=t1:break
        n=quantity(head['number']);event=tracker.accept(head)
        if event=='DUPLICATE':continue
        if event=='REORG':
            episodes.unknown()
            if anchor_B is not None and n<=anchor_B:raise Stop('REORG_INVALIDATES_FIXED_USD_ANCHOR')
            last_audit=min(last_audit,n-1) if last_audit is not None else None;evidence.save('reorg',{'UTC':utc(),'header':head,'action':'Priorbranch snapshots/virtualdecisions invalidated; no reranking to claim freshopportunity','coverage_complete':False});unknown+=1
        processing=time.monotonic();snapshot=scanner.snapshot(head);timely(head,c['timeliness'],time.monotonic()-processing,stream.backlog())
        if dt.datetime.fromisoformat(snapshot['formed']['UTC'])>=t1:
            evidence.save('late-final-snapshot',compact_snapshot(snapshot));unknown+=1;break
        if snapshot['oracle_raw']['simulated_newOracleFailureDetected']:
            episodes.unknown();evidence.save('oracle-policy-skip',snapshot);continue
        if scanner.usd_anchor is None:
            scanner.usd_anchor=int(snapshot['protocol_price_18']);anchor_B=n
            evidence.save('A-USD-anchor',{'B':head['number'],'hash':head['hash'],'protocol_ETH_USD_18':str(scanner.usd_anchor),'arrival':head['_received_UTC'],'formed':snapshot['formed'],'fixed_before_candidate_fee_evaluation':True})
            snapshot['rows']=qualify(snapshot['rows'],snapshot['count'],int(snapshot['MCR']),int(snapshot['SP_total']),int(snapshot['protocol_price_18']),quantity(head['baseFeePerGas']),c['fee_policy'],scanner.usd_anchor)
        day=snapshot['formed']['UTC'][:10];selected=episodes.update(snapshot['rows'],day,head['hash'])
        if selected:scenario_wei+=selected['minimum_reward_minus_ceiling']
        snapshot['virtual_selected']=selected;snapshot['not_fill']=True;evidence.save('snapshot',compact_snapshot(snapshot));covered+=1
        if covered==1:
            state['A_observation_started']=True;state['budget']=budget.state()
            if on_first_complete is not None:on_first_complete()
        n=quantity(head['number'])
        if last_audit is None:last_audit=n-1
        if n-last_audit>=100:
            audit=audit_window(last_audit+1,n,tracker.headers);completed_count+=len(audit['completed_transactions']);last_audit=n
        timely(head,c['timeliness'],time.monotonic()-processing,stream.backlog())
        if covered%20==0:evidence.save('heartbeat',{'status':'OBSERVING','covered_blocks':covered,'unknown':unknown,'UTC':utc(),'budget':budget.state()})
    if last_audit is not None and tracker.tip>last_audit:audit_window(last_audit+1,tracker.tip,tracker.headers)
    state.update(status='WINDOW_ENDED_PENDING_INDEPENDENT_REVIEW',covered_blocks=covered,unknown_reorgs=unknown,episode_participations=episodes.participations,UTC_day_clusters=episodes.daily,scenario_reward_less_assumed_gas_wei=str(scenario_wei),scenario_after_actual_necessary_costs='UNKNOWN_PENDING_ACTUAL_LABOR_INFRASTRUCTURE_LEDGER_AND_INDEPENDENT_REVIEW',completed_tx_audits=completed_count,coverage_ratio_and_missed_unknown='Independent canonical/timing audit required; never fill gaps0',complete_A_pass_not_automatically_declared=True)
