"""Render the four recorded stage contracts without calling a model service.

Templates are extracted from recorded natural prompts, not invented replacements.
The caller supplies a stateless completion function; semantic adequacy remains an
inspection task. This adapter is not the historical API/retry implementation.
"""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]
STAGES = ('retrieval', 'mapping', 'schema_induction', 'adaptation')
SCHEMA_FIELDS = ('schema_text', 'roles', 'relations', 'applicability_conditions',
                 'solution_or_inference_rule', 'boundaries_and_exceptions', 'sufficiency')


def render(stage, target, artifacts, source_count=3):
    saved = json.loads((BASE / 'analysis/inputs/natural_interface_audit.json').read_text())
    templates = {r['stage']: r['template'] for r in saved['templates']}
    template = templates[stage]
    if stage == 'retrieval':
        data = {'target': target, 'source_count': source_count}
    elif stage == 'mapping':
        data = {'sources': artifacts['retrieval']}
    elif stage == 'schema_induction':
        data = {'mapping_package': artifacts['mapping']}
    else:
        schema = artifacts['schema_induction']
        data = {'target': target, 'schema': {k:schema[k] for k in SCHEMA_FIELDS if k in schema} if schema else None}
    return json.dumps({'prompt_version': template['prompt_version'], 'task': template['task'],
                       'allowed_data': data, 'output_contract': template['output_contract']},
                      ensure_ascii=False, indent=2)


def run(target, complete, source_count=3):
    """Call complete(stage, prompt) once per stage, with no conversation history.

    No reference-answer argument is provided. Callers must supply a public target
    without its key, and the callback must enforce fresh service calls.
    JSON parseability is checked; semantic adequacy and model use are not.
    """
    artifacts = {}
    for stage in STAGES:
        output = complete(stage, render(stage, target, artifacts, source_count))
        artifacts[stage] = json.loads(output) if isinstance(output, str) else output
        if not isinstance(artifacts[stage], dict):
            raise ValueError(f'{stage} must return a JSON object')
    return artifacts


def continue_after_replacement(target, artifacts, stage, reference, complete):
    """Keep preceding artifacts, replace one, then rerun later calls statelessly.

    Repeated invocation retains earlier replacements. This function does not
    create references, assign diagnoses, check answer correctness, or claim a
    causal effect. Replacing adaptation produces no solver continuation.
    """
    index = STAGES.index(stage)
    chain = {s: artifacts[s] for s in STAGES[:index]}
    chain[stage] = reference
    for downstream in STAGES[index + 1:]:
        output = complete(downstream, render(downstream, target, chain))
        chain[downstream] = json.loads(output) if isinstance(output, str) else output
        if not isinstance(chain[downstream], dict):
            raise ValueError(f'{downstream} must return a JSON object')
    return {'artifacts': chain, 'oracle_assisted': True,
            'has_solver_continuation': stage != 'adaptation'}
