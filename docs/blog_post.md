Greenwashing is no longer just a PR problem. As of September 2025, it is a strict liability criminal offence in the UK.

That single shift, alongside the FCA anti-greenwashing rule and the CMA's new fining powers, has turned sustainability claims into a measurable financial risk. Which means greenwashing detection is no longer a comms exercise. It is a data problem.

Three regulatory changes matter for anyone working in ESG data right now:

→ The FCA anti-greenwashing rule came into force on 31 May 2024. It applies to every authorised firm making sustainability claims and gave the regulator an explicit basis for enforcement. The first FCA greenwashing investigation, into Drax Group, opened in 2025.

→ The Competition and Markets Authority can now issue direct fines of up to 10% of global turnover for misleading environmental claims, without going to court. Effective April 2025.

→ The Economic Crime and Corporate Transparency Act introduced a strict liability "failure to prevent fraud" offence on 1 September 2025. Greenwashing now sits within scope.

For asset managers, ESG rating providers, and the firms they cover, the cost of unverified sustainability language has shifted from reputational to financial.

That shift is the demand signal.

---

The honest version of the data problem looks like this.

A sustainability report from an oil major runs 80 to 200 pages and contains hundreds of distinct claims. Some are quantitative, like emissions targets tied to specific years. Some are directional. Many are qualitative language about responsibility and progress that is hard to falsify, and equally hard to verify.

For any given claim, three questions:

1. What is being claimed, and how specific is it?
2. What independent evidence supports or contradicts it?
3. How confident can you be in the contradiction?

None of these has an obvious technical answer. Claim extraction is harder than it looks because corporate sustainability language is deliberately hedged. Evidence retrieval depends on what you treat as a credible source, which is a judgement call before it is a retrieval problem. Confidence scoring runs into a hard truth — the absence of contradicting evidence is not the same as the presence of supporting evidence.

This is why most existing tools either give you a single number nobody knows how to interpret, or a long list of flagged sentences with no way to tell which ones matter.

---

I am building one focused on oil and gas majors. Three reasons:

→ The claim space is dense and well-defined. Net-zero targets, methane reduction, scope 3 disclosure, capital allocation to low carbon, climate lobbying — each has external benchmarks.

→ The evidence base is rich. Investigative journalism is sustained, and a small set of NGOs publish structured analyses that asset managers and regulators actually read. InfluenceMap on lobbying. Carbon Tracker on capex alignment. ClientEarth on legal exposure.

→ The contradictions are often quantitative. A company can claim alignment with the Paris Agreement while disclosing capex levels for new exploration that imply a temperature pathway well above 2°C. That kind of contradiction is detectable by a system.

---

The interesting design choice is not which model to use. It is what the system tells the user when it flags something.

A risk score on its own is not useful to anyone whose job depends on the answer. A compliance officer at an asset manager, a sustainability analyst at a rating agency, or a journalist working on a long form piece all need the same thing.

They need to see the claim, the evidence, the source of the evidence, and the reasoning that links them. They need to be able to disagree with the system and understand why.

This is the same design principle that applies to fraud detection in insurance, credit scoring, and any other domain where automated decisions touch regulated outcomes. Explainability is not a feature you add at the end. It is the shape of the output.

---

Over the next four weeks I am building GreenLens, an explainable greenwashing detection system focused on ten oil and gas majors. Sustainability reports as input. Evidence drawn from The Guardian and a curated set of NGO sources. Structured outputs that show their working.

The aim is not to beat a benchmark. There is no agreed benchmark in this space, and the academic numbers range from 70% to 91% depending on the dataset.

The aim is to build something a domain expert would find defensible. Hand-labelled evaluation set. Honest error analysis. A frontend that surfaces the reasoning rather than hiding it behind a score.

Code will be open source. Long-form technical writeup at the end.

The framing is the same one I have been applying to claims fraud detection at Govaxis AI. The candidate-facing thesis is simple. Detection systems for regulated industries need to show their working. The domain changes. The principle does not.

If you work on ESG data, climate disclosure, or sustainable finance, and you have views on what makes a detection system credible to people who actually use these outputs — I would value the conversation.

#ESG #Greenwashing #SustainableFinance #ClimateTech #NLP #FCA #ResponsibleInvesting