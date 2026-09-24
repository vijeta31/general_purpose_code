Your data is a good fit for a hybrid approach. Much of the graph can be built from data you already have, before any text extraction runs, and the terse ticket text is exactly where a mix of dictionary lookups and an LLM works best. Here's how I'd approach it.

## Step 1: Build the structured layer first

Part of the graph needs no NLP at all, because the relationships already exist in your database and portal:

- **Hot Topic to tickets.** Each Hot Topic node links to its child tickets, e.g. HT_16738923 → 43 Ticket nodes.
- **Hot Topic to product.** The portal link becomes an AFFECTS edge to a Product node.
- **Ticket metadata.** Customer, created date, severity, region, and any product version or component fields become properties or nodes.

This gives you a reliable skeleton. Everything extracted from text later attaches to it.

## Step 2: Build an alias and code dictionary

For your kind of data, this is the most important step. If the dictionary is missing, "E4012", "err 4012", and "4012 error" become three different nodes and the graph falls apart.

A dictionary maps every variant to one canonical entity:

```
"FW", "firmware", "f/w"            → Concept: Firmware
"E4012", "err 4012", "0xFAC"       → ErrorCode: E4012 (meaning: ...)
"DP alarm", "data-path alert"      → AlertCode: DP_ALARM
"ProdX", "PX", "Product X Gen2"    → Product: <ID from portal>
```

There are three good ways to populate it:

- **Mine your own tickets.** Use regex to find anything shaped like a code (e.g. `E\d{4}`, `0x[0-9A-F]+`, `ALM-\d+`). Then count frequent all-caps tokens and short words that don't appear in a normal English dictionary. This surfaces most of your acronyms in an afternoon.
- **Pull from existing sources.** Error code catalogs, alert definitions, KB articles, and product documentation often contain official meanings you can import directly.
- **Let an LLM propose, and have a human confirm.** Give the LLM an unknown acronym plus 5–10 tickets where it appears, and ask what it most likely means. Then have an engineer approve or correct the suggestion. This bootstraps quickly without letting guesses leak into the graph unchecked.

Store the dictionary as Alias nodes linked to canonical entities, or as a separate lookup table. Either way, it grows over time.

## Step 3: Extract facts from each ticket

Run two passes over every ticket.

**Pass 1 is deterministic.** Regex and dictionary matching pick up error codes, alert codes, product names, and versions. These are the most reliable facts in a ticket, so don't hand them to an LLM to guess at.

**Pass 2 uses an LLM with a schema.** It extracts what regex can't: symptoms, affected component, environment, what the customer already tried, and any workaround or root cause. Two details make a big difference with terse tickets:

- **Inject the dictionary hits into the prompt**, e.g. "In this ticket, E4012 = <meaning>, DP = data path."
- **Give the model the Hot Topic context.** Include the Hot Topic title or a short summary of the sibling tickets. Your 43 tickets all describe the same issue, so the sibling context makes it much easier for the model to decode a vague one-line ticket correctly. Few datasets have this advantage.

Here is what one poorly written ticket might become (the ticket itself is made up for illustration):

```
Ticket: "cust seeing E4012 on node after FW upg, DP alarms flapping, rebooted no luck"

→ (Ticket)-[:MENTIONS]->(ErrorCode: E4012)
→ (Ticket)-[:MENTIONS]->(AlertCode: DP_ALARM)
→ (Ticket)-[:REPORTS]->(Symptom: "alarm flapping after firmware upgrade")
→ (Ticket)-[:TRIGGERED_BY]->(Event: Firmware upgrade)
→ (Ticket)-[:TRIED]->(Action: Reboot, outcome: failed)
```

## Step 4: Normalise symptoms

The 43 tickets will describe the same problem in many different ways. Take the extracted symptom phrases, embed them, and cluster them into a few canonical Symptom nodes. Do this within each Hot Topic first, then across Hot Topics. Clustering across Hot Topics is where the graph starts showing its value, because it reveals that two Hot Topics from different months share the same symptom and error code.

## Suggested schema

```
(:HotTopic)-[:HAS_TICKET]->(:Ticket)
(:HotTopic)-[:AFFECTS]->(:Product)
(:Ticket)-[:ON_VERSION]->(:ProductVersion)
(:Ticket)-[:MENTIONS]->(:ErrorCode | :AlertCode)
(:Ticket)-[:REPORTS]->(:Symptom)
(:Ticket)-[:TRIED]->(:Action)
(:Ticket)-[:RESOLVED_BY]->(:Workaround | :Fix)
(:Alias)-[:REFERS_TO]->(any canonical entity)
```

Every extracted edge should carry the source ticket ID and a confidence score. That lets you trace any fact back to its ticket and filter out weak ones.

## Practical notes

- **Mask customer PII** (names, emails, IPs, account numbers) before sending ticket text to an external LLM.
- **Start with one month of Hot Topics.** Review the output for a few of them by hand, fix the dictionary and prompt, and only then run everything.
- **Keep the schema small at first.** Five or six relation types you trust are worth more than twenty inconsistent ones.

What do you mainly want to use the graph for? For example, finding root causes, detecting new Hot Topics early, or helping support agents search past fixes. The answer changes which parts of this are worth investing in first.
