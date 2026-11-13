---
name: analyse-dynamics
description: Break down a toxic family system with family-systems research (Bowen, Minuchin, roles, DARVO): layers of harm, triangles, coalitions.
---

# Analyse the dynamics

Take the recorded system apart through the research lenses in `docs/frameworks.md`:
who originates harm, who carries it, who is protected, who absorbs it, which structures
hold it in place, and what repeats across generations. The output is written into the
overview and actor files, so it serves as reference for therapy and for other tools.

This is analysis of a system, not therapy and not a verdict on the user. The user's account
is the material; the agent does not test it.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory.
2. Read `profile.env` and `analyse-dynamics.md` in the overlay if present.
3. Read `AGENTS.md`, `docs/frameworks.md` in full, `docs/glossary.md`, `vocabulary.md`,
   `family-overview.md` and every actor file. Read sources only where an event needs
   checking for detail.

## Lenses, in order

For each, look for evidence in the recorded events; name the concept and tier; link the
actors and events. Skip a lens with nothing to say rather than forcing it.

1. **Layers of harm.** From the centre outward: originators (whose behaviour drives the
   harm), carriers (who act for them: recruited relatives, "flying monkeys"), protected
   members (favoured, "golden child"), bystanders and enablers (who see and do nothing, or
   cover), absorbers (scapegoat, parentified child, the user). One member can sit in more
   than one layer, and positions can change over time.
2. **Structure** (Minuchin): subsystems, boundaries (enmeshed, disengaged, clear),
   hierarchy and where it is inverted, coalitions and cross-generational coalitions,
   triangulation, detouring.
3. **Triangles and process** (Bowen): the main triangles and how tension moves around them;
   family projection onto a child; over- and under-functioning; cutoffs between other
   members; multigenerational transmission.
4. **Roles** with their functions; the user's terms with their mappings (Tier C role
   labels recorded as such).
5. **Parentification**: instrumental or emotional, by whom, from when.
6. **Abuse-specific patterns**: DARVO sequences, gaslighting, coercive-control patterns,
   ostracism or silent treatment, hoovering cycles. Quote the recorded events.
7. **Loyalties and ledger** (contextual): invisible loyalties, split loyalty, destructive
   entitlement passed down.
8. **Functioning**: a short description against each Circumplex and McMaster dimension.
9. **Family rules**: what keeps the system closed.

## Write

- Overview: `Layers of harm`, `Structure`, `Functioning`, `Recurring dynamics`,
  `Multigenerational patterns`, `Family rules`. Each dynamic: one line naming it, the
  lens and tier, the actors, and the events it rests on (linked).
- Actor files: add the lenses that apply under `Interpretations and lenses`, labelled as
  the agent's analysis with lens and tier; update `Roles` and `roles:` frontmatter.
- Relationships: add any coalitions, recruitments, favouring or scapegoating edges the
  analysis surfaced to the overview's `relationships` list.
- Gaps: where a lens would apply but events are thin, add an `Open questions` item ("Were
  there other times the aunt raised things on mother's behalf?"), not a hedge.
- History and Change log lines: "<date>: dynamics analysis; added <lenses>".

Then run `uv run --script scripts/family_map.py all` and commit:
`git commit -m "Analyse dynamics <date>"`.

## Report to the user

A short spoken-style summary: the layers, the two or three central dynamics, and what is
still unknown. Offer `map-family-system` and `prepare-intake-pack`. Do not offer advice on
what to do about the family unless asked.

## Data storage

Reads `profile.env` and `analyse-dynamics.md` from the overlay folder. Writes only inside
the workspace and commits.
