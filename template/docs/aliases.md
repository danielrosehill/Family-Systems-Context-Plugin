# Aliases and obfuscation

For many people in these systems, the names themselves hurt: reading "Mum" or a father's
first name a hundred times while mapping the family is its own small exposure. This
workspace lets the user give every person an alias, keep a reversible key, work in alias
form if they prefer, and produce de-identified copies for people or tools they trust
less.

## Why an alias can take the sting out

No study has tested aliasing family members as such. The practice borrows from
techniques that have been studied:

| Technique | What it is | Evidence |
| --- | --- | --- |
| **Cognitive defusion** (Acceptance and Commitment Therapy) | Changing one's relationship to a distressing word or thought rather than its content: repeating it, saying it in a silly voice, labelling it. Hayes, S. C., Strosahl, K. D., & Wilson, K. G. (2012). *Acceptance and Commitment Therapy* (2nd ed.). Guilford | Tier A. Rapid repetition of a self-relevant negative word reduced its discomfort and believability more than distraction or control tasks (Masuda, A., Hayes, S. C., Sackett, C. F., & Twohig, M. P. (2004). *Behaviour Research and Therapy, 42*(4), 477–485) |
| **Externalisation** (narrative therapy) | Giving a problem a name of its own, often a playful one, so it becomes something the person stands apart from. White, M., & Epston, D. (1990). *Narrative Means to Therapeutic Ends*. Norton | Tier B: established clinical practice, limited trials |
| **Psychological distancing** | Viewing an experience from further away (a third-person or observer perspective) reduces emotional reactivity when recalling it. Kross, E., & Ayduk, O. (2017). Self-distancing: Theory, research, and current directions. *Advances in Experimental Social Psychology, 55*, 81–136 | Tier A for self-distancing; applying it through a renamed other is an extension |
| **Pseudonymisation** | Replacing identifiers with stand-ins so material can be shared; standard in qualitative research ethics and defined in data-protection law (GDPR, Art. 4(5)) | A privacy technique, not a psychological one |

So: an alias is a reasonable, low-cost thing to try, with plausible mechanisms and no
promise. If a name stops hurting, it can be switched back with one command.

## Kinds of alias

The user chooses; the agent can suggest. Suggestions should fit what the user wants the
alias to do:

- **Neutral**: a role or letter ("Parent A", "the Eldest"), for distance without tone.
- **Descriptive**: a name for the function ("the Weather System" for a parent whose moods
  ran the house; "the Courier" for a relative who carried messages), in the spirit of
  narrative externalisation.
- **Deflating**: something small or absurd that drains the power from the name, in the
  spirit of defusion. Only if the user wants it; never mocking of the user's own feelings.
- **Plain substitute**: an ordinary first name, so the material reads naturally.

Ask before suggesting deflating aliases, and never pick aliases that name a diagnosis.

## Real names in the record, mappings on the way out

The workspace is always written with **real names**: that keeps the record accurate,
searchable and unambiguous. Aliases are applied only when material leaves the record:

- when the agent **shows or reads material to the user** (the `present_with` mapping,
  usually `comfort`);
- when the user **prepares material** for someone else (an intake pack, a diagram, a
  copy of the files), with whichever mapping fits the reader.

Nothing is converted in place, so nothing can drift or be lost.

## aliases.yaml

```yaml
present_with: comfort      # mapping used whenever the agent shows material to the user;
                           # "real" to see real names
people:
  - slug: mother           # the actor file, actors/mother.md
    names: ["Jane Doe", "Jane", "Mum", "Mother"]   # every way she is written (any case)
    comfort: "the Weather" # what the user sees
    share: "Parent A"      # neutral label for other readers
other_identifiers:         # places, schools, workplaces, community names
  - {real: "Springfield", share: "[home town]"}
# Optional: define or override mappings. These four exist by default:
# mappings:
#   real:       {names: null}
#   comfort:    {names: comfort}
#   share:      {names: share, identifiers: true}
#   obfuscated: {names: share, identifiers: true,
#                strip: [full-dates, emails, urls, phones], sources: false}
```

- A mapping's `names` field says which per-person value to use. Add any field you like
  (`therapist: "Ms A"`) and a mapping that uses it (`therapist: {names: therapist}`).
- A per-person value can also be a dict, to give variants different aliases:
  `comfort: {"Mum": "the Weather", "*": "W"}` (`*` covers the rest).
- Matching is whole-word and case-insensitive, longest variant first, and covers
  possessives ("Mum's").
- `aliases.yaml` is the key. It holds real names, stays in the private repository, and is
  never part of an export.

Use role-based actor slugs (`mother.md`, not `jane.md`) so file names give nothing away.

## Mappings

| Mapping | For | What it does |
| --- | --- | --- |
| `real` | The record itself | Nothing |
| `comfort` | Showing material to the user | Names to the user's chosen aliases |
| `share` | A therapist or group the user half-trusts; another AI tool | Names to neutral role labels; other identifiers replaced |
| `obfuscated` | Untrusted readers: a forum post, a public tool | `share`, plus full dates reduced to the year, emails, links and phone numbers removed, sources left out unless asked for; then an agent review for anything still identifying |

## Commands

```bash
scripts/aliases.py check                                  # every actor covered, no clashes
scripts/aliases.py filter --mapping comfort actors/mother.md   # print one file through a mapping
scripts/aliases.py render --mapping share                 # mapped copy of the workspace in exports/
scripts/aliases.py key                                    # exports/alias-key-<date>.md
scripts/family_map.py pdf --mapping comfort               # diagram with aliases
scripts/intake_pack.py --mapping share                    # intake pack with aliases
```

Obfuscation lowers the chance of identification; it does not guarantee it. Distinctive
events identify people as well as names do. The `share-safely` skill says what it could
not remove.
