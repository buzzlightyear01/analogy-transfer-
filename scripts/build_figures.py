"""Compact paper figures from retained thesis audits; no new experimental data."""
from pathlib import Path
import os, json, csv
BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / 'figures'
OUT.mkdir(exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(BASE / 'build' / 'mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
data=json.loads((ROOT/'tehran-thesis-master/output/phase1_cot_transitions/audit.json').read_text())
rows=[r for r in data['comparisons'] if r['model']=='Mistral-7B-Instruct-v0.3']
labels={1:'Analogy 300w',2:'Analogy 600w',3:'2 x 300w',4:'3 x 200w',7:'Random same domain',8:'Random other domain',21:'Self-analogy'}
fig,ax=plt.subplots(figsize=(3.8,2.6))
y=np.arange(len(rows))
for sign,col,key,label,dy in [(1,'#78B64A',1,'Incorrect to correct',-.16),(-1,'#FF8CC6',2,'Correct to incorrect',.16)]:
 vals=[sign*r['percentages'][key] for r in rows]
 ax.barh(y+dy,vals,height=.3,color=col,label=label)
 for yy,v in zip(y+dy,vals): ax.text(v+(0.35 if v>=0 else -.35),yy,f'{abs(v):.1f}',ha='left' if v>=0 else 'right',va='center',fontsize=8)
ax.set_yticks(y,[labels[r['condition']] for r in rows]);ax.invert_yaxis();ax.axvline(0,color='#6B7280',lw=.7)
ax.set_xlim(-18,29);ax.set_xlabel('Share of all matched questions (%)')
ax.legend(loc='upper center',bbox_to_anchor=(.35,1.2),ncol=2,frameon=False,fontsize=7)
fig.tight_layout();fig.savefig(OUT/'phase1_transitions.pdf',bbox_inches='tight');fig.savefig(OUT/'phase1_transitions.png',dpi=180,bbox_inches='tight');plt.close(fig)
source=ROOT/'result_audit/real_chart_atlas/canonical/observed_stage_flow_data.csv'
with source.open() as f: states=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(3.8,2.3))
for dataset,n,color,offset in [('GPQA',73,'#367CA0',-14),('Murder Mystery',43,'#9D6797',8)]:
 ss=[r for r in states if r['dataset']==dataset and r['state'] in ['Initial diagnosis','After Gold Retrieval','After Gold Mapping','After Gold Schema']]
 counts=[int(r['correct'])//2 for r in ss]
 assert all(int(r['denominator'])//2==n for r in ss)
 vals=np.array(counts)*100/n
 ax.plot(range(4),vals,'o-',color=color,lw=1.7,markersize=4,label=dataset)
 for x,p,c in zip(range(4),vals,counts):
  if x:ax.annotate(f'{c}/{n}',(x,p),xytext=(0,offset),textcoords='offset points',ha='center',fontsize=8,color=color)
ax.set_xticks(range(4),['Initial','+Retrieval','+Mapping','+Schema'],fontsize=8)
ax.set_ylim(-2,43);ax.set_ylabel('Rescued initial failures (%)',fontsize=9)
ax.grid(axis='y',alpha=.2);ax.legend(loc='upper left',fontsize=8,frameon=False)
fig.tight_layout();fig.savefig(OUT/'phase3_repairs.pdf',bbox_inches='tight');fig.savefig(OUT/'phase3_repairs.png',dpi=180,bbox_inches='tight');plt.close(fig)
print('Built two figures using retained audit counts.')
