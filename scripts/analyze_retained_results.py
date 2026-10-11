"""Offline paired analyses of retained results. No model calls or new annotations.

The bootstrap resamples target-story groups, preserving all four cells and all
saved executions of a question. Intervals are conditional on the retained source
corpus, assignment and prompts; they do not cover regenerated source uncertainty.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse
import csv
import hashlib
import json
import numpy as np

BASE = Path(__file__).resolve().parents[1]
MODELS = ['llama-3.2-1b-instruct', 'llama-3.2-3b-instruct',
          'llama-3.1-8b-instruct', 'llama-3.1-70b-instruct',
          'qwen3-14b', 'qwen3-32b']


def bootstrap(values, groups, rng, draws=20000):
    labels = sorted(set(groups))
    sums = np.array([values[np.array(groups) == g].sum() for g in labels])
    sizes = np.array([sum(x == g for x in groups) for g in labels])
    indices = rng.integers(0, len(labels), (draws, len(labels)))
    sampled = sums[indices].sum(axis=1) / sizes[indices].sum(axis=1)
    return [float(x) for x in np.quantile(sampled * 100, [.025, .975])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--import-workspace', type=Path)
    args = parser.parse_args()
    out = BASE / 'analysis'
    out.mkdir(exist_ok=True)
    inputs = out / 'inputs'
    inputs.mkdir(exist_ok=True)
    if args.import_workspace:
        root = args.import_workspace.resolve()
        rows = []
        for name in ['phase2_chart_options', 'phase2_qwen_charts']:
            rows.extend(json.loads((root / 'tehran-thesis-master/output' / name / 'response_data.json').read_text()))
        (inputs / 'transfer_responses.json').write_text(json.dumps(rows, indent=2))
        assignments = []
        source_dir = root / 'github codex/analogy-codex/MuSR analogies/datasets/generated_analogies/random_controls_seed_20260903'
        for p in sorted(source_dir.glob('*.csv')):
            dataset = p.name.removeprefix('random_control_').split('_openai__')[0]
            for r in csv.DictReader(p.open(encoding='utf-8-sig')):
                assignments.append(dict(item_id=f"{dataset}:{r['story_id']}:{r['question_id']}",
                                        donor_id=f"{r['random_control_donor_dataset']}:{r['random_control_donor_story_id']}:{r['random_control_donor_question_id']}",
                                        same_story=r['random_control_same_story'].lower() == 'true'))
        assert len(assignments) == 103
        assert len({r['item_id'] for r in assignments}) == 103
        assert len({r['donor_id'] for r in assignments}) == 103
        assert all(r['item_id'] != r['donor_id'] for r in assignments)
        (inputs / 'random_assignments.json').write_text(json.dumps(assignments, indent=2))
        # Only scored outcome metadata is copied; no prompts, private config or keys.
        natural = []
        for model in ['cf.llama-3.1-8b-instruct-fast', 'deepseek-v4-flash']:
            for dataset in ['gpqa_main', 'musr_murder_mystery']:
                p = root.parent / '🌷 schema codex portable/runs' / model / dataset / 'reports/accuracy.json'
                d = json.loads(p.read_text())
                b = {r['item_id']: r for r in d['baseline']['cases']}
                f = {r['item_id']: r for r in d['framework']['cases']}
                assert set(b) == set(f) and len(b) == 100
                for item in sorted(b):
                    natural.append(dict(model=model, dataset=dataset, item_id=item,
                                        baseline_correct=b[item]['correct'], framework_correct=f[item]['correct']))
        (inputs / 'natural_framework_outcomes.json').write_text(json.dumps(natural, indent=2))
        # Audit recorded input keys; this is a mechanical interface check, not
        # a semantic leakage test or an evaluation of artifact correctness.
        expected = {'retrieval': {'target', 'source_count'}, 'mapping': {'sources'},
                    'schema_induction': {'mapping_package'}, 'adaptation': {'target', 'schema'}}
        trace_checks, prompt_templates = [], {}
        for model in ['cf.llama-3.1-8b-instruct-fast', 'deepseek-v4-flash']:
            for dataset in ['gpqa_main', 'musr_murder_mystery']:
                run = root.parent / '🌷 schema codex portable/runs' / model / dataset
                report = json.loads((run / 'reports/accuracy.json').read_text())
                ids = {r['item_id'] for r in report['framework']['cases']}
                found = defaultdict(list)
                for p in (run / 'results/framework').glob('*.json'):
                    d = json.loads(p.read_text())
                    if d['item']['item_id'] in ids:
                        found[d['item']['item_id']].append(d)
                assert set(found) == ids and all(len(v) == 1 for v in found.values())
                for item in sorted(found):
                    stages = found[item][0]['result']['stages']
                    target = json.loads(stages['retrieval']['attempts'][0]['prompt'])['allowed_data']['target']
                    attempts = 0
                    for stage, content in stages.items():
                        for a in content['attempts']:
                            attempts += 1
                            prompt = json.loads(a['prompt'])
                            allowed = set(prompt['allowed_data'])
                            assert allowed == expected[stage], (model, dataset, item, stage, allowed)
                            data = prompt['allowed_data']
                            if stage == 'retrieval':
                                assert data['target'] == target and data['source_count'] == 3
                            elif stage == 'mapping':
                                assert data['sources'] == stages['retrieval']['output']
                            elif stage == 'schema_induction':
                                assert data['mapping_package'] == stages['mapping']['output']
                            elif stage == 'adaptation':
                                schema_out = stages['schema_induction']['output']
                                keys = ('schema_text', 'roles', 'relations', 'applicability_conditions',
                                        'solution_or_inference_rule', 'boundaries_and_exceptions', 'sufficiency')
                                expected_schema = {k:schema_out[k] for k in keys if k in schema_out} if schema_out else None
                                assert data['schema'] == expected_schema
                                assert data['target'] == target
                            template = {k:v for k,v in prompt.items() if k != 'allowed_data'}
                            template['allowed_data_keys'] = sorted(allowed)
                            digest = hashlib.sha256(json.dumps(template, sort_keys=True).encode()).hexdigest()
                            prompt_templates[digest] = dict(stage=stage, template=template)
                    # Inspect the schema actually supplied to the last A attempt,
                    # not merely S's text field or a claimed use flag.
                    schema = json.loads(stages['adaptation']['attempts'][-1]['prompt'])['allowed_data']['schema'] or {}
                    core = ('schema_text', 'roles', 'relations', 'applicability_conditions',
                            'solution_or_inference_rule', 'boundaries_and_exceptions')
                    absent = all(not schema.get(k) for k in core)
                    if absent:
                        assert schema.get('sufficiency') in {'insufficient', 'sufficient', 'partial', 'complete'}
                    trace_checks.append(dict(model=model, dataset=dataset, item_id=item,
                                             recorded_attempts=attempts, recorded_stages=sorted(stages),
                                             recorded_parent_artifacts_match=True,
                                             adaptation_schema_sufficiency=schema.get('sufficiency'),
                                             adaptation_schema_content_absent=absent))
        assert len(trace_checks) == 400
        (inputs / 'natural_interface_audit.json').write_text(json.dumps(dict(
            interpretation='Recorded explicit input-key audit only; not semantic validation or hidden-history verification.',
            cases=trace_checks, templates=list(prompt_templates.values())), indent=2))
        # Preserve aggregate provenance as aggregates, never synthesized row labels.
        with (root / 'result_audit/real_chart_atlas/canonical/observed_stage_flow_data.csv').open() as fp:
            states = list(csv.DictReader(fp))
        for r in states:
            for key in r:
                if key not in ['dataset', 'state'] and r[key] != '':
                    assert int(r[key]) % 2 == 0
                    r[key] = int(r[key]) // 2
        (inputs / 'llama_retained_states.json').write_text(json.dumps(states, indent=2))
        deep = json.loads((root / 'result_audit/exhaustive_chart_atlas/deepseek_diagnostics.json').read_text())
        for v in deep.values():
            v['source'] = 'retained diagnostic bundle, restored 2026-10-07; display scaling removed'
        (inputs / 'deepseek_archived_states.json').write_text(json.dumps(deep, indent=2))
        phase1 = json.loads((root / 'tehran-thesis-master/output/phase1_cot_transitions/audit.json').read_text())
        selected = [r for r in phase1['comparisons'] if r['model'] == 'Mistral-7B-Instruct-v0.3']
        (inputs / 'mistral_transitions.json').write_text(json.dumps(selected, indent=2))
        # A compact evidence extract for the individual archived continuation.
        import csv as _csv
        run = root.parent / '🌷 schema codex portable/runs/deepseek-v4-flash/musr_murder_mystery'
        export = list(_csv.DictReader((run / 'exports/stage_replacement_diagnostic.csv').open(encoding='utf-8-sig')))
        case = next(r for r in export if r['item_id'] == 'musr_murder_mystery:87:0')
        summary = json.loads((run / 'diagnostics/murder_100_stage_replacements/summary_schema_induction.json').read_text())
        follow = json.loads((Path(summary['results'][0]['result_directory']) / 'result.json').read_text())
        assert follow['correct'] is True and follow['replacement_stage'] == 'schema_induction'
        excerpt = dict(item_id=case['item_id'], benchmark_key=case['correct_answer'],
                       original_answer=case['original_final_answer'],
                       original_schema=json.loads(case['original_schema_induction']),
                       original_adaptation_schema_checks=json.loads(case['original_adaptation'])['constraint_checks'][:1],
                       continuation_final_answer=follow['final_answer'],
                       continuation_status=follow['status'], oracle_assisted=follow['replacement_is_oracle_assisted'],
                       chain_sources={k:v['source'] for k,v in follow['chain'].items()},
                       reference_schema=follow['chain']['schema_induction']['output'],
                       created_at=follow['created_at'])
        (inputs / 'schema_case_87.json').write_text(json.dumps(excerpt, indent=2))

    rows = json.loads((inputs / 'transfer_responses.json').read_text())
    assert len(rows) == 6592
    by = defaultdict(dict)
    for r in rows:
        key = (r['model'], r['item_id'], r['run'])
        assert r['cell'] not in by[key]
        by[key][r['cell']] = r
    assert all(set(cells) == set('ABCD') for cells in by.values())
    rng = np.random.default_rng(20261012)
    assignments = json.loads((inputs / 'random_assignments.json').read_text())
    same_story_ids = {r['item_id'] for r in assignments if r['same_story']}
    assert len(same_story_ids) == 4
    summary = []
    all_ids = None
    for model in MODELS:
        ids = sorted({i for m, i, _ in by if m == model})
        assert len(ids) == 103
        if all_ids is None:
            all_ids = ids
        assert ids == all_ids
        assert set(ids) == {r['item_id'] for r in assignments}
        runs = sorted({k for m, _, k in by if m == model})
        assert len(runs) == (3 if model.startswith('llama') else 2)
        cube = np.array([[[int(by[model, i, k][c]['correct']) for c in 'ABCD'] for k in runs] for i in ids])
        valid = np.array([[[bool(by[model, i, k][c]['valid']) for c in 'ABCD'] for k in runs] for i in ids])
        item_cells = cube.mean(axis=1)
        contrasts = item_cells[:, 1] - item_cells[:, 0] - item_cells[:, 3] + item_cells[:, 2]
        stories = [i.rsplit(':', 1)[0] for i in ids]
        exact_common_valid = valid.all(axis=(1, 2))
        different_story = np.array([i not in same_story_ids for i in ids])
        summary.append(dict(model=model, questions=len(ids), stories=len(set(stories)), runs=len(runs),
                            cells_percent=(item_cells.mean(axis=0) * 100).tolist(),
                            interaction_pp=float(contrasts.mean() * 100),
                            story_bootstrap_95=bootstrap(contrasts, stories, rng),
                            item_bootstrap_95=bootstrap(contrasts, ids, rng),
                            invalid_events_per_cell=(~valid).sum(axis=(0, 1)).tolist(),
                            common_valid_questions=int(exact_common_valid.sum()),
                            common_valid_interaction_pp=float(contrasts[exact_common_valid].mean() * 100),
                            excluding_same_story_n=int(different_story.sum()),
                            excluding_same_story_interaction_pp=float(contrasts[different_story].mean() * 100)))
    natural = json.loads((inputs / 'natural_framework_outcomes.json').read_text())
    states = json.loads((inputs / 'llama_retained_states.json').read_text())
    for r in states:
        if r['state'] == 'All initial outcomes':
            assert r['denominator'] == 100
        elif r['state'] == 'After gold Adaptation':
            assert sum(int(r[k] or 0) for k in ['correct', 'gold_key_match', 'adjudicated']) == r['denominator']
        else:
            assert sum(int(r[k] or 0) for k in ['correct', 'retrieval', 'mapping', 'schema', 'adaptation']) == r['denominator']
    groups = defaultdict(list)
    for r in natural:
        assert isinstance(r['baseline_correct'], bool) and isinstance(r['framework_correct'], bool)
        groups[r['model'], r['dataset']].append(r)
    natural_summary = []
    interface = json.loads((inputs / 'natural_interface_audit.json').read_text())
    schema_flags = {(r['model'], r['dataset'], r['item_id']): r['adaptation_schema_content_absent'] for r in interface['cases']}
    for (model, dataset), rs in groups.items():
        assert len(rs) == len({r['item_id'] for r in rs}) == 100
        natural_summary.append(dict(model=model, dataset=dataset, n=100,
                                    baseline_correct=sum(r['baseline_correct'] for r in rs),
                                    framework_correct=sum(r['framework_correct'] for r in rs),
                                    incorrect_to_correct=sum(not r['baseline_correct'] and r['framework_correct'] for r in rs),
                                    correct_to_incorrect=sum(r['baseline_correct'] and not r['framework_correct'] for r in rs),
                                    no_schema_content=sum(schema_flags[model, dataset, r['item_id']] for r in rs),
                                    correct_without_schema_content=sum(schema_flags[model, dataset, r['item_id']] and r['framework_correct'] for r in rs)))
        if model == 'cf.llama-3.1-8b-instruct-fast':
            label = 'GPQA' if dataset == 'gpqa_main' else 'Murder Mystery'
            initial = next(r for r in states if r['dataset'] == label and r['state'] == 'All initial outcomes')
            assert initial['correct'] == natural_summary[-1]['framework_correct']
    manifest = [{'file':str(p.relative_to(BASE)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted(inputs.glob('*.json'))]
    result = dict(analysis_date='2026-10-12', seed=20261012, bootstrap_draws=20000,
                  interpretation='Conditional descriptive resampling intervals. No source-regeneration, permutation or annotation uncertainty.',
                  transfer=summary, natural_framework=natural_summary, inputs=manifest)
    (out / 'retained_results_audit.json').write_text(json.dumps(result, indent=2))
    for r in summary:
        print(r['model'], 'interaction', round(r['interaction_pp'], 2), 'story interval',
              [round(x, 2) for x in r['story_bootstrap_95']], 'stories', r['stories'],
              'valid subset', r['common_valid_questions'], round(r['common_valid_interaction_pp'],2),
              'no same story',round(r['excluding_same_story_interaction_pp'],2))
    print('Natural baselines:', natural_summary)


if __name__ == '__main__':
    main()
