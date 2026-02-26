# Vyvanse (Lisdexamfetamine) — The Raw Science: Pharmacology & Mechanism of Action

## Summary

Lisdexamfetamine dimesylate (LDX/Vyvanse) is an inactive prodrug consisting of d-amphetamine covalently bonded to the amino acid l-lysine. After oral ingestion, it is absorbed intact via the PEPT1 oligopeptide transporter in the small intestine and then hydrolyzed by aminopeptidases in red blood cell cytosol to release pharmacologically active d-amphetamine. This rate-limited enzymatic conversion—rather than GI dissolution mechanics—controls d-amphetamine delivery, producing a delayed Tmax (~3.5–4.7 h vs. ~2–3 h for IR d-amphetamine), lower Cmax variability (CV 12–36%), and a duration of therapeutic action extending 13–14 hours post-dose. Once liberated, d-amphetamine enters the CNS and acts as a substrate for the dopamine transporter (DAT) and norepinephrine transporter (NET), triggering reverse transport of catecholamines into the synapse, inhibiting vesicular monoamine transporter 2 (VMAT2), and agonizing the intracellular trace amine-associated receptor 1 (TAAR1). These actions increase extracellular dopamine and norepinephrine primarily in the prefrontal cortex, striatum, and nucleus accumbens—circuits governing executive function, attention, and reward. Chronic therapeutic exposure produces measurable neuroadaptations including DAT upregulation, D2/D3 receptor changes, and dendritic remodeling, though the clinical significance of these changes at therapeutic doses remains an active area of investigation.

---

## Key Findings

- **LDX is hydrolyzed inside red blood cells**, not in the GI tract or liver. The conversion enzyme is a cytosolic aminopeptidase (not yet fully characterized). Half-life of LDX itself in blood is ~1.1–1.4 hours in vitro.
- **Prodrug conversion is the rate-limiting step**: food, GI pH (e.g., proton pump inhibitors), and route of administration (oral, intranasal, IV) have minimal effect on the d-amphetamine PK profile—a key abuse-deterrent property.
- **d-Amphetamine's primary mechanism is reverse transport, not reuptake inhibition**: it enters neurons via DAT/NET, causes cytoplasmic dopamine/NE release from vesicles (via VMAT2 inhibition), then reverses transporter direction to flood the synapse.
- **TAAR1 is a critical intracellular modulator**: d-amphetamine activates TAAR1 inside dopamine neurons, which triggers PKA/PKC phosphorylation of DAT, contributing to transporter internalization and reverse transport. TAAR1 knockout mice show exaggerated responses to amphetamine.
- **Dolder et al. (2017) found no difference in Cmax** between oral lisdexamfetamine (100 mg) and equimolar d-amphetamine (40 mg) in healthy subjects—only a ~1.1 h delay in Tmax. This challenges the common claim that LDX produces "lower peak levels."
- **Chronic stimulant treatment increases striatal DAT density by ~24%** after 12 months (Wang et al., 2013 PET study), potentially contributing to tolerance.
- **Amphetamine produces region-specific dendritic remodeling**: increased spine density in medial prefrontal cortex and nucleus accumbens shell, but decreased spine density in orbital prefrontal cortex—a dissociation with potential implications for decision-making.

---

## 1. Prodrug Mechanism: From LDX to d-Amphetamine

### Chemistry
LDX consists of d-amphetamine covalently linked to l-lysine via a peptide bond at the amino group of d-amphetamine and the carboxyl group of l-lysine. The intact molecule is pharmacologically inactive—it does not bind DAT, NET, or any known CNS target. [(Ermer et al., 2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4823324/)

### Absorption
After oral administration, intact LDX is rapidly absorbed from the small intestine via carrier-mediated active transport, likely through the oligopeptide transporter PEPT1. This is fundamentally different from all other long-acting stimulants, which rely on mechanical phased-release systems in the GI tract. [(Ermer et al., 2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4823324/)

### Red Blood Cell Hydrolysis
Once in the bloodstream, LDX enters red blood cells and is cleaved by an aminopeptidase in the erythrocyte cytosol. Key findings from Sharman & Pennick (2014):

- The hydrolysis occurs specifically in **RBC cytosol**, not in plasma, liver, or other tissues
- The responsible enzyme is a **peptidase** (aminopeptidase, not fully characterized) that cleaves the lysine-amphetamine peptide bond
- In vitro half-life of LDX in whole blood: **~1.1–1.4 hours** (healthy donors: 1.13–1.15 h; sickle cell donors: 1.30–1.36 h)
- After 4 hours of incubation, only **10–15% of initial LDX** remained intact
- LDX hydrolysis is **haematocrit-dependent**, but substantial d-amphetamine production still occurs at 10% of normal haematocrit
- Sickle cell disease does not meaningfully alter conversion rates

[(Sharman & Pennick, 2014 — PMC4257105)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4257105/) [(Pennick, 2013 — tandfonline)](https://www.tandfonline.com/doi/full/10.3109/21556660.2013.775132)

### Why This Matters: Abuse Deterrence
The rate-limited enzymatic conversion means that:
- **Intranasal LDX** produces the same d-amphetamine PK profile as oral administration (no faster onset)
- **Intravenous LDX 50 mg** produced Tmax of 2.5 h and Cmax of 38.9 ng/mL vs. IV d-amphetamine 20 mg at Tmax 0.8 h and Cmax 105 ng/mL
- Drug-liking scores for IV LDX were **not significantly different from placebo** (p = 0.290), while IV d-amphetamine was (p = 0.01)
- Real-world data: odds of abuse/misuse were **1.9x higher** for Adderall XR and **2.3x higher** for IR amphetamine compared to LDX

[(Ermer et al., 2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4823324/)

### GI Independence
Unlike Adderall XR (pH-sensitive bead technology), LDX's d-amphetamine delivery is:
- Unaffected by food (only ~1 h delay in Tmax, no change in Cmax or AUC)
- Unaffected by proton pump inhibitors (omeprazole had no effect on d-amphetamine PK)
- Can be dissolved in water, mixed into food/yogurt, or opened and sprinkled with identical PK

---

## 2. Neurotransmitter Effects: How d-Amphetamine Works at the Molecular Level

### The Core Mechanism: Reverse Transport (Not Just Reuptake Inhibition)

**This is the most commonly misunderstood aspect of amphetamine pharmacology.** Unlike cocaine or methylphenidate—which are DAT/NET *blockers* (reuptake inhibitors)—d-amphetamine is a DAT/NET *substrate* that enters the neuron and causes reverse transport. The distinction is critical:

| Mechanism | Cocaine/Methylphenidate | d-Amphetamine |
|-----------|------------------------|---------------|
| Primary action | Blocks DAT/NET from outside | Enters neuron via DAT/NET |
| Effect on transporter | Inhibits reuptake | Reverses transport direction |
| Vesicular effects | None | Inhibits VMAT2, releases vesicular DA |
| Intracellular action | None | Activates TAAR1, redistributes DA |
| Net result | Prevents clearance | Actively ejects DA into synapse |

[(Robertson et al., 2009 — PMC2729543)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2729543/) [(Sulzer et al., 2005 — Progress in Neurobiology)](https://www.sciencedirect.com/science/article/abs/pii/S0301008205000432)

### Step-by-Step Molecular Mechanism

**Step 1 — Entry via DAT/NET**: d-Amphetamine is a competitive substrate for the dopamine transporter (DAT) and norepinephrine transporter (NET). It competes with dopamine/NE for the inward-facing binding site and is transported into the presynaptic terminal. This competitive binding alone provides some reuptake inhibition.

**Step 2 — VMAT2 inhibition and vesicular DA release**: Inside the neuron, d-amphetamine is a weak base (pKa ~10) that enters synaptic vesicles and collapses the pH gradient that VMAT2 relies on to sequester dopamine. This releases stored dopamine from vesicles into the cytoplasm, creating a large pool of free cytoplasmic DA. d-Amphetamine also directly inhibits VMAT2 function. [(Sulzer et al., 2005)](https://www.sciencedirect.com/science/article/abs/pii/S0301008205000432)

**Step 3 — DAT/NET reverse transport**: The elevated cytoplasmic DA/NE concentration, combined with amphetamine-induced phosphorylation of DAT (via TAAR1 → PKA/PKC signaling), causes the transporter to reverse direction—pumping dopamine/NE *out* of the neuron and into the synapse. This is the primary mechanism by which amphetamine increases extracellular catecholamines. [(Robertson et al., 2009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2729543/)

**Step 4 — TAAR1 activation**: d-Amphetamine activates the intracellular trace amine-associated receptor 1 (TAAR1), a Gs/Gq-coupled GPCR located predominantly inside dopamine neurons (not on the cell surface). TAAR1 activation:
- Triggers cAMP accumulation via adenylyl cyclase
- Activates PKA and PKC, which phosphorylate DAT
- Phosphorylated DAT shifts to a "channel-like" mode favoring reverse transport
- Promotes DAT internalization from the cell surface
- Acts as a **rheostat** that modulates dopamine neuron firing rate

[(Miller, 2011 — PMC3005101)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3005101/) [(Zilberg et al., 2024 — Nature Communications)](https://www.nature.com/articles/s41467-023-44601-4)

> **Surprising finding**: TAAR1 knockout mice show markedly elevated dopamine neuron firing rates at baseline and exaggerated responses to amphetamine, confirming TAAR1 normally acts as a brake on dopaminergic transmission. This is why TAAR1 agonists are being explored as antipsychotics. [(Halff et al., 2023 — Trends in Neurosciences)](https://www.sciencedirect.com/science/article/pii/S0166223622002119)

**Step 5 — MAO inhibition** (minor): At higher concentrations, amphetamine weakly inhibits monoamine oxidase (MAO), reducing intracellular degradation of catecholamines. This is a secondary mechanism at therapeutic doses.

### Transporter Affinities
d-Amphetamine has higher affinity for DAT than NET, but acts on both. It has minimal direct serotonergic activity (unlike MDMA or methamphetamine), though high doses can weakly affect SERT. The selectivity for catecholamine systems is what makes it effective for ADHD without prominent serotonergic side effects. [(Faraone, 2018 — Neurosci Biobehav Rev)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8063758/)

---

## 3. Brain Regions Affected

### Prefrontal Cortex (PFC) — "The Executive Control Center"

The dorsolateral and ventromedial prefrontal cortex are critically involved in:
- Working memory
- Sustained attention
- Behavioral inhibition
- Planning and organization

The PFC operates on an **inverted-U dose-response curve** for catecholamines. Both too little *and* too much DA/NE impair PFC function. At low to moderate concentrations:
- **Dopamine acts via D1 receptors** to strengthen delay-period firing in PFC networks ("signal")
- **Norepinephrine acts via α2A receptors** to suppress irrelevant inputs ("noise")

This is why therapeutic doses of amphetamine improve attention in ADHD (moving patients from the left side of the inverted-U toward the peak), while supertherapeutic doses can impair cognition (pushing past the peak).

[(Arnsten & Pliszka, 2011 — PMC3129015)](https://ncbi.nlm.nih.gov/pmc/articles/PMC3129015/)

### Striatum (Caudate/Putamen) — "The Habit and Motor System"

The dorsal striatum (caudate nucleus and putamen) receives dense dopaminergic input from the substantia nigra (nigrostriatal pathway). This region is involved in:
- Procedural learning
- Habit formation
- Motor control

Amphetamine increases extracellular DA in the striatum via the reverse transport mechanism. In rat microdialysis studies, LDX produced a **more gradual and sustained** increase in striatal DA efflux compared to IR d-amphetamine, which produced a sharp spike followed by rapid decline. This smoother DA profile may underlie LDX's reduced behavioral activation and lower acute tolerance. [(Rowley et al., 2012 — Neuropharmacology)](https://www.sciencedirect.com/science/article/abs/pii/S0028390812003437)

### Nucleus Accumbens (NAc) — "The Reward Center"

The NAc is the ventral striatum and is the primary target of the mesolimbic dopamine pathway (from ventral tegmental area). It mediates:
- Reward processing
- Motivation
- Reinforcement learning

Amphetamine-induced DA release in the NAc shell drives the reinforcing and euphorigenic effects. **At therapeutic doses**, the moderate DA increase improves motivation and task engagement. **At supertherapeutic doses**, the DA surge produces euphoria and drives abuse potential.

> **Key finding (Thomas lab, 2015)**: Repeated amphetamine exposure potentiates AMPA receptor-mediated synaptic transmission in NAc shell medium spiny neurons—a glutamatergic plasticity change that persists 10–14 days after the last dose and is depotentiated only by re-exposure. This represents a cellular substrate for drug-seeking behavior. [(Nature Neuropsychopharmacology, 2015)](https://www.nature.com/articles/npp2015168)

### Locus Coeruleus (LC) — "The Arousal Hub"

The LC is the brain's primary source of norepinephrine, projecting widely throughout the cortex. Amphetamine's NET-mediated effects in the LC:
- Increase tonic NE release, promoting wakefulness and arousal
- Modulate the signal-to-noise ratio in cortical processing
- Contribute to the alerting and attentional effects of stimulants

The LC operates in tonic (baseline vigilance) and phasic (event-driven alerting) modes. Therapeutic stimulant doses appear to optimize the phasic mode, improving focused attention. [(Arnsten & Pliszka, 2011)](https://ncbi.nlm.nih.gov/pmc/articles/PMC3129015/)

---

## 4. Pharmacokinetics: The Numbers

### Key PK Parameters for LDX → d-Amphetamine

| Parameter | LDX (therapeutic range) | IR d-Amphetamine | Source |
|-----------|------------------------|-------------------|--------|
| **Tmax (d-amph)** | 3.5–4.7 h | 2.0–3.0 h | Ermer 2016 |
| **Tlag** | 1.5 h (1.3–1.7) | 0.8 h (0.6–1.0) | Dolder 2017 |
| **Cmax** | 108–133 ng/mL (70 mg) | 108–133 ng/mL (equiv.) | Dolder 2017 |
| **t½ (d-amph)** | 7.9–10.4 h | 7.9–10 h | Dolder 2017, Ermer 2016 |
| **t½ (intact LDX)** | 0.4–0.9 h | N/A | Ermer 2016 |
| **AUC∞** | ~1817 ng·h/mL (100 mg) | ~1727 ng·h/mL (40 mg equiv.) | Dolder 2017 |
| **Duration of efficacy** | 13–14 h | 4–6 h | Ermer 2016 |
| **Steady state** | Reached by day 5 | — | Krishnan 2008 |
| **Steady-state trough** | ~20 ng/mL (70 mg) | — | Krishnan 2008 |
| **Steady-state Cmax** | ~90 ng/mL (70 mg) | — | Krishnan 2008 |
| **Inter-individual CV** | 12–36% (low) | Higher | Ermer 2016 |

### The Dolder 2017 Challenge

This is a critical and often overlooked study. Dolder et al. (Frontiers in Pharmacology, 2017) directly compared equimolar oral doses of LDX (100 mg) and d-amphetamine (40 mg) in 24 healthy subjects:

- **Cmax was NOT significantly different** between LDX and d-amphetamine (118 vs. 120 ng/mL)
- **AUC was NOT significantly different** (1817 vs. 1727 ng·h/mL)
- **The only difference was timing**: Tlag was 0.6 h longer and Tmax was 1.1 h later for LDX
- **Peak subjective effects (drug liking, drug high, stimulation) were identical**
- Authors concluded: "The pharmacokinetics and pharmacodynamics of lisdexamfetamine are similar to D-amphetamine administered 1 h later"

This contradicts the narrative that LDX produces "lower peak levels" and "less euphoria" than equivalent oral d-amphetamine. The abuse-deterrent advantage appears to be primarily in **parenteral** routes (intranasal, IV), where the prodrug mechanism prevents bypassing the rate-limited conversion.

[(Dolder et al., 2017 — Front Pharmacol)](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2017.00617/full)

### Comparison with Methylphenidate

| Parameter | LDX/d-Amphetamine | Methylphenidate (Concerta) |
|-----------|-------------------|---------------------------|
| Mechanism | Reverse transport + VMAT2 | DAT/NET reuptake inhibition |
| t½ | ~10 h | ~3.5 h |
| Duration | 13–14 h | 10–12 h |
| Catecholamine selectivity | DA > NE >> 5-HT | DA ≈ NE, no 5-HT |
| Stereochemistry | d-amphetamine (dextro) | dl-threo-methylphenidate |

[(Faraone, 2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8063758/)

---

## 5. Dose-Response Relationship

### Therapeutic Dose Range
- **Available doses**: 10, 20, 30, 40, 50, 60, 70 mg capsules; 10–70 mg chewable tablets
- **Typical starting dose**: 30 mg/day
- **Maximum recommended dose**: 70 mg/day
- **Dose titration**: Increments of 10–20 mg at weekly intervals

### Dose-Response Efficacy (Faraone et al., 2012)

A forced-dose titration study in adults with ADHD (30, 50, 70 mg LDX) found:
- **Linear dose-response**: Higher LDX doses → greater improvement in ADHD-RS scores
- Both **inattentive and hyperactive-impulsive** symptoms showed dose-dependent improvement
- Patients with greater baseline severity benefited more from higher doses (especially for hyperactive-impulsive symptoms)
- About **4% of patients** assigned to 50 mg and **14% assigned to 70 mg** could not achieve their target dose due to adverse effects
- The dose-response relationship was **not affected by prior pharmacotherapy**

[(Faraone et al., 2012 — J Atten Disord)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3355536/)

### The Inverted-U and the Narrow Window

The inverted-U dose-response applies specifically to **prefrontal cortex function**:

- **Low catecholamine levels** (unmedicated ADHD): Poor PFC engagement → inattention, impulsivity
- **Optimal levels** (therapeutic dose): Enhanced D1/α2A signaling → improved working memory, inhibition
- **Excessive levels** (supertherapeutic): D1 overstimulation + α1/β activation → stereotypy, anxiety, cognitive rigidity

This window is narrower than commonly appreciated. The Arnsten lab has shown that even small increases above optimal catecholamine levels can shift PFC networks from "thoughtful" top-down regulation to "fight-or-flight" amygdala-driven responses. [(Arnsten & Pliszka, 2011)](https://ncbi.nlm.nih.gov/pmc/articles/PMC3129015/)

### Common Adverse Effects (dose-related)
- **Decreased appetite**: 27–39% (children), up to 27% (adults)
- **Insomnia**: 11–19% (vs. ~5% placebo)
- **Dry mouth**: ~26% in adults
- **Increased heart rate**: Mean increase ~5–6 bpm at therapeutic doses
- **Blood pressure increase**: Systolic +2–4 mmHg, diastolic +1–3 mmHg (mean)

---

## 6. Neuroplasticity: What Chronic Exposure Does to the Brain

### Dopamine Transporter (DAT) Upregulation

**Wang et al. (2013)** — PET imaging study in adults with ADHD:
- 12 months of methylphenidate treatment **increased striatal DAT availability by ~24%** compared to baseline
- This was measured using [11C]cocaine PET
- The increase in DAT levels may represent a **compensatory adaptation** to chronic transporter blockade/reverse transport
- Clinical implication: potential contributor to **tolerance** (more DAT = faster dopamine clearance = reduced drug efficacy over time)

[(Wang et al., 2013 — PLoS ONE — PMC3655054)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3655054/)

### Dopamine Receptor Changes

**D2/D3 receptors in stimulant users (meta-analysis, Proebstl et al., 2019)**:
- Cocaine users showed significant **decreases in D2/D3 receptor availability** across the entire striatum
- Amphetamine/methamphetamine users showed a **trend toward decreased D2/D3** but results were less consistent
- **Important caveat**: Most studies examined recreational/abusive doses, not therapeutic ADHD doses

**Ginovart et al. (1999)** — PET study in nonhuman primates:
- Chronic amphetamine (escalating doses over weeks) reduced striatal D2 receptor density
- This downregulation was partially reversible after drug cessation

[(Ginovart et al., 1999 — PubMed 10024013)](https://pubmed.ncbi.nlm.nih.gov/10024013/) [(Proebstl et al., 2019 — European Psychiatry)](https://www.sciencedirect.com/science/article/abs/pii/S0924933819300574)

### Dendritic Morphology: Region-Specific Remodeling

This is one of the most fascinating areas of amphetamine neuroscience:

**Robinson & Kolb (1997)** — Landmark study:
- Rats given repeated amphetamine (escalating doses) showed **persistent structural changes** in neurons, lasting at least 1 month after cessation:
  - **Nucleus accumbens medium spiny neurons**: Increased dendritic branching and spine density
  - **Prefrontal cortex layer III pyramidal neurons**: Increased dendritic branching and spine density
- These changes were in the same direction as those produced by enriched environments

[(Robinson & Kolb, 1997 — J Neurosci 17:8491)](https://www.jneurosci.org/content/17/21/8491)

**Selemon et al. (2007)** — Nonhuman primates:
- Amphetamine sensitization in rhesus monkeys altered dendritic morphology in **prefrontal cortical pyramidal neurons**
- Changes were more subtle than in rodents but still detectable

[(Selemon et al., 2007 — Neuropsychopharmacology)](https://www.nature.com/articles/1301179)

**DePoy & Bhagat (2015)** — The mPFC/oPFC dissociation:
- **Medial PFC**: Amphetamine and cocaine *increase* dendrite length and spine density
- **Orbital PFC**: Amphetamine and cocaine *decrease* dendrite length and *eliminate* dendritic spines
- This dissociation may explain why chronic stimulant users show **impaired reversal learning** (an oPFC-dependent function) despite preserved or enhanced other executive functions

[(DePoy & Bhagat, 2015 — Traffic)](https://onlinelibrary.wiley.com/doi/10.1111/tra.12295)

### AMPA Receptor Plasticity

**Repeated amphetamine exposure potentiates AMPAR-mediated transmission** specifically in NAc shell (not core) medium spiny neurons. This glutamatergic plasticity:
- Persists 10–14 days after the last dose
- Is reversed (depotentiated) by drug re-exposure
- Is thought to encode drug-associated memories and drive motivation for drug-seeking

[(Nature Neuropsychopharmacology, 2015)](https://www.nature.com/articles/npp2015168)

### Acute Tolerance (Tachyphylaxis)

Both LDX and d-amphetamine show **clockwise hysteresis** in effect-concentration plots — meaning the subjective/cardiovascular effects are greater on the ascending limb of the concentration-time curve than on the descending limb at equivalent plasma levels. This acute pharmacological tolerance:
- Develops within a single dose
- Is similar for LDX and d-amphetamine
- Is proposed as why LDX's slower onset may paradoxically result in **longer** duration of action: less acute tolerance develops during the gradual rise, so effects persist further into the declining phase

[(Dolder et al., 2017)](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2017.00617/full) [(Ermer et al., 2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4823324/)

> **Surprising finding**: The mechanism explaining why LDX lasts ~13–14 hours (vs. 4–6 for IR amphetamine) despite having the *same* d-amphetamine half-life (~10 h) and *same* AUC is likely **reduced acute tolerance** from the slower rise, not a fundamentally different PK profile. The d-amphetamine is the same molecule either way—but how fast it arrives in the brain changes how the brain responds to it.

---

## Sources

1. Ermer JC, Pennick M, Frick G. Lisdexamfetamine Dimesylate: Prodrug Delivery, Amphetamine Exposure and Duration of Efficacy. *Clin Drug Investig*. 2016;36:341–356. [PMC4823324](https://pmc.ncbi.nlm.nih.gov/articles/PMC4823324/)
2. Sharman J, Pennick M. Lisdexamfetamine prodrug activation by peptidase-mediated hydrolysis in the cytosol of red blood cells. *Neuropsychiatr Dis Treat*. 2014;10:2275–2280. [PMC4257105](https://pmc.ncbi.nlm.nih.gov/articles/PMC4257105/)
3. Dolder PC, et al. Pharmacokinetics and Pharmacodynamics of Lisdexamfetamine Compared with D-Amphetamine in Healthy Subjects. *Front Pharmacol*. 2017;8:617. [PMC5594082](https://pmc.ncbi.nlm.nih.gov/articles/PMC5594082/)
4. Robertson SD, Matthies HJ, Galli A. A closer look at amphetamine-induced reverse transport and trafficking of the dopamine and norepinephrine transporters. *Mol Neurobiol*. 2009;39(2):73–80. [PMC2729543](https://pmc.ncbi.nlm.nih.gov/articles/PMC2729543/)
5. Sulzer D, et al. Mechanisms of neurotransmitter release by amphetamines: A review. *Prog Neurobiol*. 2005;75(6):406–433. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0301008205000432)
6. Miller GM. The emerging role of trace amine-associated receptor 1 in the functional regulation of monoamine transporters and dopaminergic activity. *J Neurochem*. 2011;116(2):164–176. [PMC3005101](https://pmc.ncbi.nlm.nih.gov/articles/PMC3005101/)
7. Faraone SV. The pharmacology of amphetamine and methylphenidate: Relevance to the neurobiology of ADHD. *Neurosci Biobehav Rev*. 2018;87:255–270. [PMC8063758](https://pmc.ncbi.nlm.nih.gov/articles/PMC8063758/)
8. Arnsten AFT, Pliszka SR. Catecholamine Influences on Prefrontal Cortical Function: Relevance to Treatment of ADHD. *Pharmacol Biochem Behav*. 2011;99(2):211–216. [PMC3129015](https://ncbi.nlm.nih.gov/pmc/articles/PMC3129015/)
9. Wang GJ, Volkow ND, et al. Long-Term Stimulant Treatment Affects Brain Dopamine Transporter Level in Patients with ADHD. *PLoS ONE*. 2013;8(5):e63023. [PMC3655054](https://pmc.ncbi.nlm.nih.gov/articles/PMC3655054/)
10. Robinson TE, Kolb B. Persistent Structural Modifications in Nucleus Accumbens and Prefrontal Cortex Neurons Produced by Previous Experience with Amphetamine. *J Neurosci*. 1997;17(21):8491–8497. [jneurosci.org](https://www.jneurosci.org/content/17/21/8491)
11. Fernandez-Espejo E, Rodriguez-Espinosa N. Psychostimulant Drugs and Neuroplasticity. *Pharmaceuticals*. 2011;4(7):976–991. [PMC4058673](https://pmc.ncbi.nlm.nih.gov/articles/PMC4058673/)
12. DePoy LM, et al. Synaptic Cytoskeletal Plasticity in the Prefrontal Cortex Following Psychostimulant Exposure. *Traffic*. 2015;16(9):919–940. [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/tra.12295)
13. Calipari ES, Ferris MJ. Amphetamine Mechanisms and Actions at the Dopamine Terminal Revisited. *J Neurosci*. 2013;33(21):8923–8925. [PMC3753078](https://ncbi.nlm.nih.gov/pmc/articles/PMC3753078/)
14. Rowley HL, et al. Lisdexamfetamine and immediate release d-amfetamine – Differences in PK/PD relationships. *Neuropharmacology*. 2012;63(6):1064–1074. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0028390812003437)
15. Faraone SV, et al. Dose Response Effects of Lisdexamfetamine Dimesylate Treatment in Adults with ADHD. *J Atten Disord*. 2012;16(2):118–127. [PMC3355536](https://pmc.ncbi.nlm.nih.gov/articles/PMC3355536/)
16. Halff EF, et al. TAAR1 agonism as a new treatment strategy for schizophrenia. *Trends Neurosci*. 2023;46(1):60–74. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0166223622002119)
17. Zilberg G, et al. Molecular basis of human trace amine-associated receptor 1 activation. *Nature Communications*. 2024;15:108. [nature.com](https://www.nature.com/articles/s41467-023-44601-4)
18. Ginovart N, et al. Changes in striatal D2-receptor density following chronic treatment with amphetamine. *Synapse*. 1999;31(2):154–162. [PubMed 10024013](https://pubmed.ncbi.nlm.nih.gov/10024013/)
19. Proebstl L, et al. Effects of stimulant drug use on the dopaminergic system: A systematic review and meta-analysis. *European Psychiatry*. 2019;59:15–24. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0924933819300574)
20. Pennick M. Metabolism of the prodrug lisdexamfetamine dimesylate in human red blood cells from normal and sickle cell disease donors. *J Drug Assess*. 2013. [tandfonline](https://www.tandfonline.com/doi/full/10.3109/21556660.2013.775132)
