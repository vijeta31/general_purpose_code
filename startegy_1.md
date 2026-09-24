Your setup already gives you the hardest part of a knowledge graph for free. The Hot Topics are a human-curated grouping: someone has already decided that these 43 tickets describe the same problem. The structured parts (HT_ID, ticket IDs, portal-linked products) can be mapped directly with no NLP. Extraction is only needed for the messy ticket text, and even there the grouping helps a lot.

This is a graph schema that fits your case:The typical relationships in this schema are:
- (HotTopic)-[:CONTAINS]->(Ticket)
- (HotTopic)-[:AFFECTS]->(Product)
- (Ticket)-[:REPORTS]->(Symptom)
- (Ticket)-[:SHOWS_CODE]->(ErrorCode)
- (Ticket)-[:INVOLVES]->(Component)
- (Ticket)-[:RAISED_BY]->(Customer)
- (HotTopic)-[:CAUSED_BY]->(RootCause)
- (RootCause)-[:FIXED_BY]->(Fix)

The build order below is what I'd recommend.

## Step 1: Load the structured data directly

HT_ID, ticket IDs, the HT→Ticket membership, timestamps, customer and account fields, and the portal's product links all go straight into the graph through a mapping script. No NLP is needed here.

The portal's product links are your most trusted entity data, so treat them as ground truth. They also give you context for later steps. Once you know the HT is about Product X, an ambiguous acronym in its tickets probably refers to something inside Product X.

## Step 2: Build the alias and acronym dictionary before any extraction

With messy tickets, this matters more than which model you pick. If "WSG", "web sec gw", and "WebSecure Gateway" become three nodes, or error code "E-4012" and "err 4012" never connect, the graph is useless for search and root-cause analysis.

Seed the dictionary from sources you already have:
- product names, SKUs, and short names from the portal;
- error-code and alert-code catalogues from engineering or monitoring docs;
- internal glossaries and wiki pages.

Then mine the tickets themselves, which is where the HT grouping pays off:
- Tickets in the same HT describe the same problem, so a term that shows up in many tickets of one HT and rarely elsewhere is probably an alias for something central to that HT.
- Explicit expansions like "WSG (WebSecure Gateway)" can be harvested with simple patterns.
- An LLM can propose candidate expansions ("in these 43 tickets about Product X, what does 'SCN' most likely mean?"). A support SME should approve them before they go in the dictionary.

Store each entry as canonical ID → list of variants, with a scope where needed. "SC" can mean different things for different products.

## Step 3: Extract entities in two layers, deterministic first

**Layer A: rules and dictionary, for high precision and low cost.**
- Regex patterns catch error codes and alert codes, which usually follow fixed formats like `E\d{4}` or `ALRT-\d+`. Normalize them all to one form, so "E-4012", "e4012", and "err 4012" all become `E4012`.
- Dictionary matching catches products, components, and acronyms. spaCy's EntityRuler or FlashText work well for this and are fast even over millions of tickets.

**Layer B: an LLM, only for the fuzzy parts.** Rules can't pull out the symptom from "customer says its not working after the update, pls chk urgent", but an LLM can. Give it:
- the ticket text;
- the entities Layer A already found, already resolved to canonical IDs;
- the portal's product for this HT;
- a fixed schema of what to extract: symptom, component, trigger (upgrade, config change, and so on), impact, steps already tried, and workaround.

Tell it not to invent codes or products and to output only the allowed types. Because the codes and products are resolved before the LLM sees the ticket, it has far less room to hallucinate them.

Here is a made-up example of what one ticket turns into:

> *"Cust on v8.2 getting E-4012 on WSG after upgrade, ALRT221 firing continuously, users can't login. restarted svc no luck"*

→ Product: WebSecure Gateway (v8.2) · ErrorCode: E4012 · AlertCode: ALRT-221 · Symptom: login failure · Trigger: upgrade · Tried: service restart

## Step 4: Normalize symptoms into canonical nodes

Symptoms are free text. "Can't log in", "login fails", and "auth not working" should become a single Symptom node. To do this:
- embed the extracted symptom phrases;
- cluster them, which works best within a product first;
- have an LLM or a person name each cluster;
- link tickets to the cluster node, not the raw phrase.

The HT grouping works as a sanity check here. If one HT's symptoms scatter across ten clusters, your clustering is too fine.

## Step 5: Aggregate at the Hot Topic level

This is where the graph becomes more than a ticket database. For each HT:
- Roll up the ticket edges into weighted HT edges. For example, E4012 appearing in 38 of 43 tickets becomes a strong edge, while a code seen in only 2 tickets is probably noise.
- Generate an HT summary and, if engineering resolved it, attach RootCause and Fix nodes from the closure notes or linked bug tickets.
- Add version and customer-environment patterns, such as "only on v8.2" or "only on-prem".

## Step 6: Keep provenance on everything

Every extracted edge should carry the source ticket ID, the extraction method (regex, dictionary, or LLM), and a confidence score. When an engineer asks why E4012 is linked to a component, they can click through to the actual tickets. You can also re-run just the LLM layer later without touching the reliable rule-based edges.

## Step 7: Feed unknown terms back into the dictionary

Anything that looks like a code or acronym but isn't in the dictionary goes into an "unresolved terms" review queue. As SMEs resolve these, the dictionary grows and extraction improves with each monthly batch. After a few cycles, most new tickets resolve fully through the cheap deterministic layer.

## What this graph enables

- **Early hot topic detection.** A new ticket's extracted entities are matched against existing HTs, for example "this looks like HT_16738923 with 90% overlap". That lets you link it immediately or flag an emerging issue.
- **Cross-HT root cause discovery.** Two HTs that look different but share an error code, component, and version may be the same underlying bug.
- **Agent assist or GraphRAG.** An agent asks "customer sees ALRT-221 on WSG", and the system returns the matching HT, its known fix, and similar tickets.

For storage, a property graph like Neo4j suits this well, with a vector index on ticket text and symptoms for hybrid search. Start with last month's HTs as a pilot, and have one or two SMEs check a sample of the extracted graphs before scaling up.

If you can share one or two anonymized tickets showing the real acronyms and code formats, I can draft the regex patterns, dictionary structure, and LLM extraction prompt for your data.
